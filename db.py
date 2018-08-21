# import postgresql
import psycopg2
import config


class DB:
    def __init__(self):
        self.db = psycopg2.connect(
            host=config.DB_HOST,
            user=config.DB_USERNAME,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            port=config.DB_PORT
        )

    def close(self):
        self.db.close()

    def select(self, sql):
        cur = self.db.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        self.db.close()
        return rows

    def insert(self, sql, *args):
        cur = self.db.cursor()
        id = None

        if len(args) == 1:
            cur.execute(sql, (args[0],))

        elif len(args) == 2:
            cur.execute(sql, (args[0], args[1],))

        elif len(args) == 3:
            cur.execute(sql, (args[0], args[1], args[2],))

        elif len(args) == 4:
            cur.execute(sql, (args[0], args[1], args[2], args[3],))

        elif len(args) == 5:
            cur.execute(sql, (args[0], args[1], args[2], args[3], args[4]))

        if "RETURNING" in sql:
            id = cur.fetchone()[0]

        self.db.commit()
        cur.close()
        return id

    def remove(self):
        pass

    def update(self, sql):
        cur = self.db.cursor()
        cur.execute(sql)
        self.db.commit()
        self.db.close()


class Queries(DB):
    def get_remind(self):
        sql = 'SELECT message FROM reminder'
        result = self.select(sql)
        return result

    def insert_remind(self, user_id, msg, time):
        sql = "INSERT INTO reminder (user_id, message, notify_at) VALUES(%s, %s, %s) RETURNING id"

        try:
            reminder_id = self.insert(sql, user_id, msg, time)
            print(reminder_id)

        except psycopg2.DatabaseError as e:
            if self.db:
                self.db.rollback()

            print('Error %s' % e)

    def update_remind(self):
        pass
