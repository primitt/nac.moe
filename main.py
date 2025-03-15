from flask import Flask, render_template, send_from_directory, redirect
from datetime import datetime, timedelta
import json
from db.db import database, events

# TODO: Create a monthly manga recommendations page
# TODO: Create an events page
# TODO: Create a meet the board page
# TODO: Add contact information and proper, nice footer


# DEPRECATED
# def next_first_or_third_tuesday(start_date=None):
#     if not start_date:
#         start_date = datetime.now()
#     else:
#         start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
#     first_day_of_next_month = (start_date.replace(day=1) + timedelta(days=31)).replace(day=1)
#     first_day_of_current_month = start_date.replace(day=1)
#     tuesday_count = 0
    
#     for day in range(31):
#         current_date = first_day_of_current_month + timedelta(days=day)
#         if current_date.weekday() == 1:
#             tuesday_count += 1
#             if tuesday_count in [1, 3] and current_date >= start_date and current_date.strftime('%Y-%m-%d') not in skip_meeting:
#                 return current_date
#     tuesday_count = 0
#     for day in range(31): 
#         current_date = first_day_of_next_month + timedelta(days=day)
#         if current_date.weekday() == 1:
#             tuesday_count += 1
#             if tuesday_count in [1, 3]:
#                 return current_date


app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    meeting_date = events.select().where(events.type == 'Meeting', events.date > datetime.now().date()).order_by(events.date.asc()).limit(1)
    if len(meeting_date) > 0:
        meeting_date = meeting_date[0].date.strftime('%B %d, %Y')
    else:
        meeting_date = None
    return render_template('index.html', meeting_date=meeting_date)
@app.route('/media/<path>')
def media(path):
    return send_from_directory('media', path)
@app.route('/short/<name>')
def short(name):
    json_file = json.load(open('short.json'))
    if name.lower() in json_file:
        return redirect(json_file[name.lower()]['url'])
    return "Short link not found", 404
@app.route('/events')
def event():
    even = events.select()
    parsed_events = {}
    for event in even:
        if event.date and event.date_end:
            if event.date >= datetime.now().date() or event.date_end >= datetime.now().date():
                get_month = event.date.strftime('%B')
                event.date = event.date.strftime('%B %d, %Y')
                event.date_end = event.date_end.strftime('%B %d, %Y')
                if get_month not in parsed_events:
                    parsed_events[get_month] = []
                parsed_events[get_month].append(event)
        elif event.date:
             if event.date >= datetime.now().date():
                get_month = event.date.strftime('%B')
                event.date = event.date.strftime('%B %d, %Y')
                if get_month not in parsed_events:
                    parsed_events[get_month] = []
                parsed_events[get_month].append(event)
        else:
            if 'No Date' not in parsed_events:
                parsed_events['No Date'] = []
            parsed_events['No Date'].append(event)
    # sort the months in order putting No Date at the end
    parsed_events = dict(sorted(parsed_events.items(), key=lambda x: datetime.strptime(x[0], '%B') if x[0] != 'No Date' else datetime.strptime('December', '%B')))
    return render_template('events.html', parsed_events=parsed_events)
if __name__ == '__main__':
    app.run(debug=True)