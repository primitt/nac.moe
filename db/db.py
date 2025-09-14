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
    class Meta:
        table_name = 'news'

class officers(BaseModel):
    id = AutoField()
    pfp = TextField()
    name = TextField()
    position = TextField()
    bio = TextField()
    favorite_anime_enabled = BooleanField(default=False)
    favorite_anime_name = TextField(null=True)
    favorite_anime_img = TextField(null=True)
    favorite_anime_genre = TextField(null=True)
    favorite_anime_season = TextField(null=True)
    favorite_anime_bio = TextField(null=True)
    favorite_anime_score_al = TextField(null=True)
    favorite_anime_score_mal = TextField(null=True)
    favorite_anime_url_al = TextField(null=True)
    class Meta:
        table_name = 'officers'

class settings(BaseModel):
    name = TextField(unique=True)
    value = TextField()
    class Meta:
        table_name = 'settings'

    
if not database.table_exists('events'):
    database.create_tables([events])
if not database.table_exists('news'):
    database.create_tables([news])
if not database.table_exists('settings'):
    database.create_tables([settings])
if not database.table_exists('officers'):
    database.create_tables([officers])

    

if __name__ == "__main__":
    # migration
    migrator = SqliteMigrator(database)
    