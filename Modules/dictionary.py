from Db.dictionary import DictionaryQueries
from re import search

class Dictionary:
    def __init__(self, language="english"):
        self._language = language
        self._word = ''
        self._translate = ''

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
        english = msg[0].lower()
        russian = ' '.join(msg[1:]).lower()

        if search('^[a-z\s]+$', english) and search('^[а-я\s,]+$', russian):
            self.word = english
            self.translate = russian
            return True

        return False

    def get_by_word(self, word):
        query = DictionaryQueries()
        response = query.get_word_by_word(
            language=self.language,
            word=word
        )
        return response

    def get_list(self, word='', limit=10):
        query = DictionaryQueries()
        response = query.get_words_list(
            language=self.language,
            word=word,
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

        query = DictionaryQueries()
        response = query.insert_word(
            language=self.language,
            word=self.word,
            word_translate=self.translate
        )
        return response
