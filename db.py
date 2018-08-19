import postgresql.driver as pg_driver
import config


class DB:
    def __init__(self):
        self.db = pg_driver.connect(
            host=config.DB_HOST,
            user=config.DB_USERNAME,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            port=config.DB_PORT
        )

    def select(self):
        pass

    def insert(self):
        pass

    def remove(self):
        pass

    def update(self):
        pass


class Queries(DB):
    def get_remind(self):
        pass

    def insert_remind(self):
        pass

    def update_remind(self):
        pass