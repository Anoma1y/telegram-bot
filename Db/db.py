import psycopg2
import config as CONFIG


class DB:
    def __init__(self):
        self.db = psycopg2.connect(
            host=CONFIG.DB_HOST,
            user=CONFIG.DB_USERNAME,
            password=CONFIG.DB_PASSWORD,
            database=CONFIG.DB_NAME,
            port=CONFIG.DB_PORT
        )

    def close(self):
        self.db.close()

    def select(self, sql):
        result = self.db.cursor()
        result.execute(sql)
        rows = result.fetchall()
        self.db.close()
        return rows

    def insert(self, sql, *args):
        result = self.db.cursor()
        result.execute(sql, tuple(args))
        response = None

        if "RETURNING" in sql:
            response = result.fetchone()

        self.db.commit()
        result.close()
        return response

    def update(self, sql, *args):
        result = self.db.cursor()
        result.execute(sql, tuple(args))
        self.db.commit()
        self.db.close()
