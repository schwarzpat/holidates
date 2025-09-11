import re

FLAGS = re.IGNORECASE | re.DOTALL

def to_hive(sql: str) -> str:
    # TRUNC(ts,'dd') -> cast(to_date(ts) as timestamp)
    sql = re.sub(
        r"TRUNC\s*\(\s*([^)]+?)\s*,\s*'dd'\s*\)",
        r"cast(to_date(\1) as timestamp)",
        sql,
        flags=FLAGS
    )

    # Normalize TO_DATE
    sql = re.sub(r"\bTO_DATE\s*\(", "to_date(", sql, flags=FLAGS)

    # ---- DAY offsets, including quoted numbers ----
    sql = re.sub(
        r"DATE_ADD\s*\(\s*((?:[^()]|\([^()]*\))+?)\s*,\s*INTERVAL\s*'?\s*([+-]?\d+)\s*'?\s*DAY\s*\)",
        r"date_add(\1, \2)",
        sql,
        flags=FLAGS
    )

    # ---- MINUTE fixed time: (H*60 + M) ----
    def repl_min_fixed(m):
        base = m.group(1).strip()
        h = int(m.group(2))
        mi = int(m.group(3))
        return f"cast(concat(to_date({base}), ' {h:02d}:{mi:02d}:00') as timestamp)"

    sql = re.sub(
        r"DATE_ADD\s*\(\s*((?:[^()]|\([^()]*\))+?)\s*,\s*INTERVAL\s*\(\s*(\d+)\s*\*\s*60\s*\+\s*(\d+)\s*\)\s*MINUTES?\s*\)",
        repl_min_fixed,
        sql,
        flags=FLAGS
    )

    # ---- MINUTE relative offset: N ----
    def repl_min_rel(m):
        base = m.group(1).strip()
        total = int(m.group(2))
        return f"from_unixtime(unix_timestamp({base}) + {total} * 60)"

    sql = re.sub(
        r"DATE_ADD\s*\(\s*((?:[^()]|\([^()]*\))+?)\s*,\s*INTERVAL\s*\(?\s*([+-]?\d+)\s*\)?\s*MINUTES?\s*\)",
        repl_min_rel,
        sql,
        flags=FLAGS
    )

    # ---- HOUR relative offset ----
    def repl_hour_rel(m):
        base = m.group(1).strip()
        total = int(m.group(2))
        return f"from_unixtime(unix_timestamp({base}) + {total} * 3600)"

    sql = re.sub(
        r"DATE_ADD\s*\(\s*((?:[^()]|\([^()]*\))+?)\s*,\s*INTERVAL\s*\(?\s*([+-]?\d+)\s*\)?\s*HOURS?\s*\)",
        repl_hour_rel,
        sql,
        flags=FLAGS
    )

    # ---- SECOND relative offset ----
    def repl_sec_rel(m):
        base = m.group(1).strip()
        total = int(m.group(2))
        return f"from_unixtime(unix_timestamp({base}) + {total})"

    sql = re.sub(
        r"DATE_ADD\s*\(\s*((?:[^()]|\([^()]*\))+?)\s*,\s*INTERVAL\s*\(?\s*([+-]?\d+)\s*\)?\s*SECONDS?\s*\)",
        repl_sec_rel,
        sql,
        flags=FLAGS
    )

    return sql
