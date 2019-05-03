from peewee import *


db = SqliteDatabase('my_database.db')


class BaseModel(Model):
    class Meta:
        database = db


class VoteHistory(BaseModel):
    vote_id = IntegerField()
    vote_date = TextField()
