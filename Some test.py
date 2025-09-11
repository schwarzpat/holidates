import re
import ast
import operator

FLAGS = re.IGNORECASE | re.DOTALL

# ---- safe integer arithmetic ----
_ALLOWED = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: lambda x: x,
}

def _safe_int(expr: str) -> int:
    node = ast.parse(expr.strip(), mode="eval").body

    def eval_node(n):
        if isinstance(n, ast.Num):  # py3.7
            return int(n.n)
        if isinstance(n, ast.Constant) and isinstance(n.value, int):
            return int(n.value)
        if isinstance(n, ast.UnaryOp) and type(n.op) in _ALLOWED:
            return _ALLOWED[type(n.op)](eval_node(n.operand))
        if isinstance(n, ast.BinOp) and type(n.op) in _ALLOWED:
            return _ALLOWED[type(n.op)](eval_node(n.left), eval_node(n.right))
        raise ValueError("unsupported expression")
    return int(eval_node(node))

# ---- main transformer ----
def to_hive(sql: str) -> str:
    prev = None
    out = sql

    # Normalize common bits
    out = re.sub(r"\bTO_DATE\s*\(", "to_date(", out, flags=FLAGS)
    out = re.sub(r"TRUNC\s*\(\s*([^)]+?)\s*,\s*'dd'\s*\)",
                 r"cast(to_date(\1) as timestamp)", out, flags=FLAGS)

    # Iterate to catch nested and multiline patterns
    for _ in range(10):
        prev = out

        # DATE_ADD(base, INTERVAL N DAY)  -> unix arithmetic in seconds
        def repl_day(m):
            base = m.group(1).strip()
            n = _safe_int(m.group(2))
            return f"from_unixtime(unix_timestamp({base}) + {n} * 86400)"
        out = re.sub(
            r"DATE_ADD\s*\(\s*((?:[^()]|\([^()]*\))+?)\s*,\s*INTERVAL\s*'?\s*([^']+?)\s*'?\s*DAY\s*\)",
            repl_day, out, flags=FLAGS
        )

        # DATE_ADD(base, INTERVAL expr MINUTE[S]?)
        def repl_min(m):
            base = m.group(1).strip()
            expr = m.group(2)
            total = _safe_int(expr)
            return f"from_unixtime(unix_timestamp({base}) + {total} * 60)"
        out = re.sub(
            r"DATE_ADD\s*\(\s*((?:[^()]|\([^()]*\))+?)\s*,\s*INTERVAL\s*\(?\s*([^)]+?)\s*\)?\s*MINUTES?\s*\)",
            repl_min, out, flags=FLAGS
        )

        # DATE_ADD(base, INTERVAL expr HOUR[S]?)
        def repl_hour(m):
            base = m.group(1).strip()
            expr = m.group(2)
            total = _safe_int(expr)
            return f"from_unixtime(unix_timestamp({base}) + {total} * 3600)"
        out = re.sub(
            r"DATE_ADD\s*\(\s*((?:[^()]|\([^()]*\))+?)\s*,\s*INTERVAL\s*\(?\s*([^)]+?)\s*\)?\s*HOURS?\s*\)",
            repl_hour, out, flags=FLAGS
        )

        # DATE_ADD(base, INTERVAL expr SECOND[S]?)
        def repl_sec(m):
            base = m.group(1).strip()
            expr = m.group(2)
            total = _safe_int(expr)
            return f"from_unixtime(unix_timestamp({base}) + {total})"
        out = re.sub(
            r"DATE_ADD\s*\(\s*((?:[^()]|\([^()]*\))+?)\s*,\s*INTERVAL\s*\(?\s*([^)]+?)\s*\)?\s*SECONDS?\s*\)",
            repl_sec, out, flags=FLAGS
        )

        if out == prev:
            break

    return out
