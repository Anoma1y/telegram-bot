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
        result = self.db.cursor()
        result.execute(sql)
        rows = result.fetchall()
        self.db.close()
        return rows

    def insert(self, sql, *args):
        result = self.db.cursor()
        id = None

        result.execute(sql, tuple(args))

        if "RETURNING" in sql:
            id = result.fetchone()[0]

        self.db.commit()
        result.close()
        return id

    def update(self, sql):
        result = self.db.cursor()
        result.execute(sql)
        self.db.commit()
        self.db.close()


class Queries(DB):
    def get_remind_list(self):
        sql = 'SELECT * FROM reminder'
        result = self.select(sql)
        return result

    def get_remind_single(self, id=None):

        if id is None:
            return False

        sql = "SELECT * FROM reminder WHERE id = {id}".format(
            id=id
        )
        result = self.select(sql)
        return result

    def get_remind_upcoming(self):
        sql = "SELECT id FROM reminder WHERE is_notify = FALSE AND notify_at BETWEEN now() and now() + INTERVAL '10 MINUTES'"
        result = self.select(sql)
        return result

    def insert_remind(self, user_id, msg, time):
        sql = "INSERT INTO reminder (user_id, message, notify_at) VALUES(%s, %s, %s) RETURNING id"

        try:
            reminder_id = self.insert(sql, user_id, msg, time)
            return reminder_id

        except psycopg2.DatabaseError as e:
            if self.db:
                self.db.rollback()

            print('Error %s' % e)

    def update_remind(self):
        pass
