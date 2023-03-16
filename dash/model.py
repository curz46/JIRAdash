import sqlite3

class DashModel:
    def __init__(self, conn, schema):
        self._dbconn = conn
        self._columns = schema["gui"]["columns"]
        self._filters = schema["gui"]["filters"]

    def get_filter_data(self, filter_group):
        cur = self._dbconn.cursor()
        cur.execute(f"""SELECT {filter_group}, COUNT(*) as count
                        FROM issues
                        GROUP BY {filter_group}
                        ORDER BY count DESC
                        LIMIT 20""")
        return cur.fetchall()

    def search_issues(self, query, active_filters):
        cur = self._dbconn.cursor()

        select_columns = ", ".join(self._columns)
        query_columns = " OR ".join([f"{col} LIKE ?" for col in self._columns])

        filter_conditions = []
        filter_values = []
        for field, filter_set in active_filters.items():
            if filter_set:
                filter_conditions.append(f"{field} IN ({','.join(['?'] * len(filter_set))})")
                filter_values.extend(filter_set)

        filter_condition = " AND ".join(filter_conditions) if filter_conditions else "1"

        sql = f"""SELECT {select_columns} FROM issues
                  WHERE ({query_columns}) AND ({filter_condition})
                  ORDER BY updated_time DESC LIMIT 100"""

        cur.execute(sql, tuple([f"%{query}%"] * len(self._columns) + filter_values))

        return cur.fetchall()

