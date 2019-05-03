from .models import db, VoteHistory


class SqliteImpl(object):
    def __init__(self):
        pass

    def connect(self):
        db.connect()
        db.create_tables([VoteHistory])

    def close(self):
        db.close()

    def create_vote_history(self, vote_id, vote_date):
        VoteHistory(vote_id=vote_id, vote_date=vote_date).save()

    def get_vote(self, vote_id, vote_date):
        try:
            return VoteHistory.get(vote_id=vote_id, vote_date=vote_date)
        except:
            return None

    def get_last_vote(self):
        return VoteHistory.select().order_by(VoteHistory.vote_id.desc()).first()
