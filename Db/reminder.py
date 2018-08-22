import psycopg2
from .db import DB


class ReminderQueries(DB):
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
        sql = "SELECT id, user_id, message, notify_at FROM reminder WHERE is_notify = FALSE AND notify_at BETWEEN now() and now() + INTERVAL '10 MINUTES'"
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

    def update_remind(self, id):
        sql = "UPDATE reminder SET is_notify = TRUE WHERE id = %s"

        try:
            self.update(sql, id)

        except psycopg2.DatabaseError:
            if self.db:
                self.db.rollback()
            print('Ошибка при обновлении статуса оповещения')
