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
        result.execute(sql, tuple(args))
        response = None

        if "RETURNING" in sql:
            response = result.fetchone()

        self.db.commit()
        result.close()
        return response

    def update(self, sql):
        result = self.db.cursor()
        result.execute(sql)
        self.db.commit()
        self.db.close()


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
        sql = "SELECT id FROM reminder WHERE is_notify = FALSE AND notify_at BETWEEN now() and now() + INTERVAL '10 MINUTES'"
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

    def update_remind(self):
        pass


class DictionaryQueries(DB):
    def get_words_list(self, language, word, limit):
        sql = "SELECT * FROM {language}_dictionary WHERE word LIKE '%{word}%' LIMIT {limit}".format(
            language=language,
            word=word,
            limit=limit
        )
        result = self.select(sql)
        return result

    def get_word_by_word_translate(self, language, word_translate):
        sql = "SELECT * FROM {language}_dictionary WHERE word_translate = '{word_translate}'".format(
            language=language,
            word_translate=word_translate
        )
        result = self.select(sql)
        return result

    def get_word_by_word(self, language, word):
        sql = "SELECT * FROM {language}_dictionary WHERE word = '{word}'".format(
            language=language,
            word=word
        )
        result = self.select(sql)
        return result

    def insert_word(self, language, word, word_translate):
        sql = "INSERT INTO {language}_dictionary (word, word_translate) VALUES(%s, %s) RETURNING *".format(
            language=language
        )

        try:
            response = self.insert(sql, word.lower(), word_translate.lower())

            return {
                'status': True,
                'data': response
            }

        except psycopg2.DatabaseError:
            if self.db:
                self.db.rollback()

            return {
                'status': False,
                'data': 'Произошла ошибка при добавлении нового слова'
            }
