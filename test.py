from db.db import database, events
import datetime

print(events.create(type="Meeting", name="Test Event", date=datetime.datetime.strptime("2025-03-10", "%Y-%m-%d"), time="12:00", location="Test Location", url="https://example.com"))
print(events.create(type="Meeting", name="Test Event", date=datetime.datetime.strptime("2025-03-25", "%Y-%m-%d"), time="12:00", location="Test Location", url="https://example.com"))
#events.delete().where(events.id < 20).execute()