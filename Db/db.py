class DB:
    def __init__(self, db):
        self.db = db

    def close(self):
        self.db.close()

    def select(self, sql):
        result = self.db.cursor()
        result.execute(sql)
        rows = result.fetchall()
        return rows

    def insert(self, sql, *args):
        result = self.db.cursor()
        result.execute(sql, tuple(args))
        response = None

        if "RETURNING" in sql:
            response = result.fetchone()

        self.db.commit()
        return response

    def update(self, sql, *args):
        result = self.db.cursor()
        result.execute(sql, tuple(args))
        self.db.commit()
