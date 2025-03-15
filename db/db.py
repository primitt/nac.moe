from peewee import *

database = SqliteDatabase('db/nac.sql')

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database 

class events(BaseModel):
    id = AutoField()
    type = TextField()
    name = TextField()
    date = DateField(null = True)
    date_end = DateField(null = True)
    time = TextField(null = True)
    location = TextField(null = True)
    url = TextField(null = True)

    class Meta:
        table_name = 'events'
        
if not database.table_exists('events'):
    database.create_tables([events])