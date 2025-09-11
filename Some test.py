import re

def to_hive(sql: str) -> str:
    # TRUNC(ts,'dd') -> cast(to_date(ts) as timestamp)
    sql = re.sub(r"TRUNC\s*\(\s*([^)]+?)\s*,\s*'dd'\s*\)",
                 r"cast(to_date(\1) as timestamp)", sql, flags=re.IGNORECASE)

    # TO_DATE(x) -> to_date(x)
    sql = re.sub(r"TO_DATE\s*\(", "to_date(", sql, flags=re.IGNORECASE)

    # DATE_ADD(x, INTERVAL N DAY) -> date_add(x, N)
    sql = re.sub(
        r"DATE_ADD\s*\(\s*([^)]+?)\s*,\s*INTERVAL\s+([+-]?\d+)\s+DAY\s*\)",
        r"date_add(\1, \2)",
        sql,
        flags=re.IGNORECASE
    )

    # DATE_ADD(x, INTERVAL (expr) MINUTE) -> from_unixtime(unix_timestamp(x) + (expr)*60)
    sql = re.sub(
        r"DATE_ADD\s*\(\s*([^)]+?)\s*,\s*INTERVAL\s*\(\s*([^)]+?)\s*\)\s*MINUTE\s*\)",
        r"from_unixtime(unix_timestamp(\1) + (\2) * 60)",
        sql,
        flags=re.IGNORECASE
    )

    # DATE_ADD(x, INTERVAL N MINUTE) -> same idea without parentheses
    sql = re.sub(
        r"DATE_ADD\s*\(\s*([^)]+?)\s*,\s*INTERVAL\s+([^)]+?)\s*MINUTE\s*\)",
        r"from_unixtime(unix_timestamp(\1) + (\2) * 60)",
        sql,
        flags=re.IGNORECASE
    )

    return sql


# Example usage
before = """ some sql"""
print(to_hive(before))
