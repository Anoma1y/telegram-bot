import psycopg2
from .db import DB


class DictionaryQueries(DB):
    def __init__(self, db):
        self.db = db
        super(DB, self).__init__()

    def get_words_list(self, language, word, limit):
        sql = "SELECT * FROM {language}_dictionary WHERE word LIKE '%{word}%' LIMIT {limit}".format(
            language=language,
            word=word,
            limit=limit
        )
        result = self.select(sql)
        return result

    def get_random_list(self, language, limit):
        sql = "SELECT * FROM {language}_dictionary ORDER BY RANDOM() LIMIT {limit}".format(
            language=language,
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
        sql = "SELECT * FROM {language}_dictionary WHERE word LIKE '{word}%' LIMIT 10".format(
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