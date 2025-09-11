import re

def to_hive(sql: str) -> str:
    # TRUNC(ts,'dd') -> cast(to_date(ts) as timestamp)
    sql = re.sub(
        r"TRUNC\s*\(\s*([^)]+?)\s*,\s*'dd'\s*\)",
        r"cast(to_date(\1) as timestamp)",
        sql,
        flags=re.IGNORECASE
    )

    # TO_DATE(x) -> to_date(x)
    sql = re.sub(r"\bTO_DATE\s*\(", "to_date(", sql, flags=re.IGNORECASE)

    # --- Handle MINUTES ---
    def repl_minutes(m):
        base = m.group(1).strip()
        expr = m.group(2).strip()
        # case: H*60 + M
        hm = re.fullmatch(r"(\d+)\s*\*\s*60\s*\+\s*(\d+)", expr)
        if hm:
            h = int(hm.group(1))
            mins = int(hm.group(2))
            return f"cast(concat(to_date({base}), ' {h:02d}:{mins:02d}:00') as timestamp)"
        # case: plain integer
        if expr.isdigit():
            total = int(expr)
            h = total // 60
            mins = total % 60
            return f"cast(concat(to_date({base}), ' {h:02d}:{mins:02d}:00') as timestamp)"
        # fallback: leave unchanged
        return m.group(0)

    sql = re.sub(
        r"DATE_ADD\s*\(\s*([^)]+?)\s*,\s*INTERVAL\s*\(?([^)]*?)\)?\s*MINUTES?\s*\)",
        repl_minutes,
        sql,
        flags=re.IGNORECASE
    )

    # --- Handle HOURS ---
    def repl_hours(m):
        base = m.group(1).strip()
        total = int(m.group(2))
        return f"cast(concat(to_date({base}), ' {total:02d}:00:00') as timestamp)"

    sql = re.sub(
        r"DATE_ADD\s*\(\s*([^)]+?)\s*,\s*INTERVAL\s*([+-]?\d+)\s*HOURS?\s*\)",
        repl_hours,
        sql,
        flags=re.IGNORECASE
    )

    # --- Handle SECONDS ---
    def repl_seconds(m):
        base = m.group(1).strip()
        total = int(m.group(2))
        h = total // 3600
        rem = total % 3600
        mins = rem // 60
        secs = rem % 60
        return f"cast(concat(to_date({base}), ' {h:02d}:{mins:02d}:{secs:02d}') as timestamp)"

    sql = re.sub(
        r"DATE_ADD\s*\(\s*([^)]+?)\s*,\s*INTERVAL\s*([+-]?\d+)\s*SECONDS?\s*\)",
        repl_seconds,
        sql,
        flags=re.IGNORECASE
    )

    return sql
