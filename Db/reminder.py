import psycopg2
from .db import DB


class ReminderQueries(DB):
    def __init__(self, db):
        self.db = db
        super(DB, self).__init__()

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
        sql = """
            SELECT pre_reminder.id, reminder.user_id, reminder.message, pre_reminder.notify_at
            FROM pre_reminder
              JOIN reminder ON pre_reminder.remind_id = reminder.id
            WHERE pre_reminder.is_sent = FALSE AND pre_reminder.notify_at BETWEEN now() and now() + INTERVAL '5 MINUTES'
        """

        result = self.select(sql)
        return result

    def insert_remind(self, user_id, msg, time):
        sql = "INSERT INTO reminder (user_id, message, notify_at) VALUES(%s, %s, %s) RETURNING *"

        try:
            response = self.insert(sql, user_id, msg, time)
            return {
                'status': True,
                'data': response
            }

        except psycopg2.DatabaseError:
            if self.db:
                self.db.rollback()

            return {
                'status': False,
                'data': 'Произошла ошибка при добавлении нового оповещения'
            }

    def insert_pre_reminder(self, data):
        sql = 'INSERT INTO pre_reminder (remind_id, notify_at) VALUES {} RETURNING id'.format(','.join(['%s'] * len(data)))

        try:
            response = self.insert_arr(sql, data)
            return {
                'status': True,
                'data': response
            }

        except psycopg2.DatabaseError:
            if self.db:
                self.db.rollback()

            return {
                'status': False,
                'data': 'Произошла ошибка при добавлении нового оповещения'
            }


    def update_pre_remind(self, id):
        sql = "UPDATE pre_reminder SET is_sent = TRUE WHERE id = %s"
        try:
            self.update(sql, id)

        except psycopg2.DatabaseError:
            if self.db:
                self.db.rollback()
            print('Ошибка при обновлении статуса оповещения')
