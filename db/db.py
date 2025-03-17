from peewee import *
from playhouse.migrate import *

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

class news(BaseModel):
    id = AutoField()
    title = TextField()
    content = TextField()
    date = DateField()
    author = TextField()
    
if not database.table_exists('events'):
    database.create_tables([events])

if not database.table_exists('news'):
    database.create_tables([news])

    

if __name__ == "__main__":
    # migration
    migrator = SqliteMigrator(database)
    