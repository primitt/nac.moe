from peewee import *

database = SqliteDatabase('db/nac.sql')

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Ar(BaseModel):
    anilisturl = TextField(null=True)
    animetitle = TextField(null=True)
    coverurl = TextField(null=True)
    id = IntegerField(null=True)
    month = IntegerField(null=True)
    recommender = TextField(null=True)
    recseries = IntegerField(null=True)

    class Meta:
        table_name = 'ar'
        primary_key = False

class Config(BaseModel):
    ccheckinurl = IntegerField(null=True)
    cnomeetdays = IntegerField(null=True)
    crecseries = IntegerField(null=True)
    id = IntegerField(null=True)

    class Meta:
        table_name = 'config'
        primary_key = False

class Recseries(BaseModel):
    id = IntegerField(null=True)
    recseries = IntegerField(null=True)

    class Meta:
        table_name = 'recseries'
        primary_key = False

class Sessions(BaseModel):
    session = TextField(null=True)
    sessionholder = IntegerField(null=True)
    valid_until = IntegerField(null=True)

    class Meta:
        table_name = 'sessions'
        primary_key = False

class Users(BaseModel):
    id = IntegerField(null=True)
    password = TextField(null=True)
    username = TextField(null=True)

    class Meta:
        table_name = 'users'
        primary_key = False
