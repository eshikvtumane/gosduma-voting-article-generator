from database_repository.sqlite.sqlite_impl import SqliteImpl


class DBRepository(object):
    def __init__(self):
        self._db = SqliteImpl()

    def connect(self):
        self._db.connect()

    def close(self):
        self._db.close()

    def create_vote_history(self, vote_id, vote_date):
        self._db.create_vote_history(vote_id, vote_date)

    def get_vote(self, vote_id, vote_date):
        return self._db.get_vote(vote_id=vote_id, vote_date=vote_date)

    def get_last_vote(self):
        return self._db.get_last_vote()
