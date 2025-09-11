import re

def to_hive(sql: str) -> str:
    # --- TRUNC ---
    # TRUNC(ts,'dd') -> cast(to_date(ts) as timestamp)
    sql = re.sub(
        r"TRUNC\s*\(\s*([^)]+?)\s*,\s*'dd'\s*\)",
        r"cast(to_date(\1) as timestamp)",
        sql,
        flags=re.IGNORECASE
    )

    # --- TO_DATE ---
    sql = re.sub(r"\bTO_DATE\s*\(", "to_date(", sql, flags=re.IGNORECASE)

    # --- DAY offsets ---
    # DATE_ADD(x, INTERVAL N DAY) -> date_add(to_date(x), N)
    sql = re.sub(
        r"DATE_ADD\s*\(\s*([^)]+?)\s*,\s*INTERVAL\s+([+-]?\d+)\s+DAY\s*\)",
        r"date_add(to_date(\1), \2)",
        sql,
        flags=re.IGNORECASE
    )

    # --- MINUTES / HOURS / SECONDS ---
    # If pattern looks like (H*60 + M) treat as fixed clock time
    def repl_minutes(m):
        base = m.group(1).strip()
        expr = m.group(2).strip()
        hm = re.fullmatch(r"(\d+)\s*\*\s*60\s*\+\s*(\d+)", expr)
        if hm:
            h = int(hm.group(1))
            mins = int(hm.group(2))
            return f"cast(concat(to_date({base}), ' {h:02d}:{mins:02d}:00') as timestamp)"
        # otherwise relative shift
        return f"from_unixtime(unix_timestamp({base}) + ({expr}) * 60)"

    sql = re.sub(
        r"DATE_ADD\s*\(\s*([^)]+?)\s*,\s*INTERVAL\s*\(?([^)]*?)\)?\s*MINUTES?\s*\)",
        repl_minutes,
        sql,
        flags=re.IGNORECASE
    )

    def repl_hours(m):
        base = m.group(1).strip()
        expr = m.group(2).strip()
        if expr.isdigit():
            return f"cast(concat(to_date({base}), ' {int(expr):02d}:00:00') as timestamp)"
        return f"from_unixtime(unix_timestamp({base}) + ({expr}) * 3600)"

    sql = re.sub(
        r"DATE_ADD\s*\(\s*([^)]+?)\s*,\s*INTERVAL\s*\(?([^)]*?)\)?\s*HOURS?\s*\)",
        repl_hours,
        sql,
        flags=re.IGNORECASE
    )

    def repl_seconds(m):
        base = m.group(1).strip()
        expr = m.group(2).strip()
        return f"from_unixtime(unix_timestamp({base}) + ({expr}))"

    sql = re.sub(
        r"DATE_ADD\s*\(\s*([^)]+?)\s*,\s*INTERVAL\s*\(?([^)]*?)\)?\s*SECONDS?\s*\)",
        repl_seconds,
        sql,
        flags=re.IGNORECASE
    )

    return sql
