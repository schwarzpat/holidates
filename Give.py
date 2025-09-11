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

    # DATE_ADD(x, INTERVAL N DAY) -> date_add(x, N)
    sql = re.sub(
        r"DATE_ADD\s*\(\s*([^)]+?)\s*,\s*INTERVAL\s+([+-]?\d+)\s+DAY\s*\)",
        r"date_add(\1, \2)",
        sql,
        flags=re.IGNORECASE
    )

    # ---- MINUTE patterns ----
    # DATE_ADD(base, INTERVAL (H*60 + M) MINUTE[S]?)
    def repl_h60m(m):
        base = m.group(1).strip()
        h = int(m.group(2))
        mins = int(m.group(3))
        return f"cast(concat(to_date({base}), ' {h:02d}:{mins:02d}:00') as timestamp)"

    sql = re.sub(
        r"DATE_ADD\s*\(\s*([^)]+?)\s*,\s*INTERVAL\s*\(\s*(\d+)\s*\*\s*60\s*\+\s*(\d+)\s*\)\s*MINUTES?\s*\)",
        repl_h60m,
        sql,
        flags=re.IGNORECASE
    )

    # DATE_ADD(base, INTERVAL N MINUTE[S]?)
    def repl_nmins(m):
        base = m.group(1).strip()
        total = int(m.group(2))
        h = total // 60
        mins = total % 60
        return f"cast(concat(to_date({base}), ' {h:02d}:{mins:02d}:00') as timestamp)"

    sql = re.sub(
        r"DATE_ADD\s*\(\s*([^)]+?)\s*,\s*INTERVAL\s*([+-]?\d+)\s*MINUTES?\s*\)",
        repl_nmins,
        sql,
        flags=re.IGNORECASE
    )

    # ---- HOUR patterns ----
    def repl_hours(m):
        base = m.group(1).strip()
        h = int(m.group(2))
        return f"cast(concat(to_date({base}), ' {h:02d}:00:00') as timestamp)"

    sql = re.sub(
        r"DATE_ADD\s*\(\s*([^)]+?)\s*,\s*INTERVAL\s*([+-]?\d+)\s*HOURS?\s*\)",
        repl_hours,
        sql,
        flags=re.IGNORECASE
    )

    # ---- SECOND patterns ----
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
