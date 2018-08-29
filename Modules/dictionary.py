from Db.dictionary import DictionaryQueries
from re import search


class Dictionary:
    def __init__(self, db, language="english"):
        self._language = language
        self._word = ''
        self._translate = ''
        self.DB_CONNECT = db

    @property
    def language(self):
        return self._language

    @property
    def word(self):
        return self._word

    @word.setter
    def word(self, val):
        self._word = val

    @property
    def translate(self):
        return self._translate

    @translate.setter
    def translate(self, val):
        self._translate = val

    @staticmethod
    def split_cmd(msg):
        return msg.split(' ')[1:]

    def gen_translate(self, msg):
        msg = self.split_cmd(msg)
        english = ''
        russian = ''

        for m in range(len(msg)):
            if search('^[a-z\s]+$', msg[m]):
                english += msg[m] + ' '
            elif search('^[а-я\s,]+$', msg[m]):
                russian += msg[m] + ' '

        if len(english) == 0 or len(russian) == 0:
            return False

        self.word = english.strip()
        self.translate = russian.strip()

        return True

    def get_by_word(self, word):
        query = DictionaryQueries(self.DB_CONNECT)
        response = query.get_word_by_word(
            language=self.language,
            word=word
        )
        return response

    def get_list(self, word='', limit=10):
        query = DictionaryQueries(self.DB_CONNECT)
        response = query.get_words_list(
            language=self.language,
            word=word,
            limit=limit
        )
        return response

    def get_random_list(self, limit=5):
        query = DictionaryQueries(self.DB_CONNECT)
        response = query.get_random_list(
            language=self.language,
            limit=limit
        )
        return response

    def insert(self, msg):
        parse = self.gen_translate(msg)

        if parse is False:
            return {
                'status': False,
                'data': 'Ошибка'
            }

        query = DictionaryQueries(self.DB_CONNECT)
        response = query.insert_word(
            language=self.language,
            word=self.word,
            word_translate=self.translate
        )
        return response
