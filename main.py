from flask import Flask, render_template, send_from_directory, redirect, request
from datetime import datetime, timedelta
import json
import os
from db.db import database, events, news, settings, officers

# TODO: Create a monthly anime recommendations page
    # TODO: Bot Commands
    # TODO: Create page for reviews
# TODO: BUG FIXES
    # TODO: BUG - index.html - fix no meeting date spacing on mobile
# TODO: Officers Page - Create re-ordering system
# TODO: Add contact information and proper, nice footer
# TODO: About Page
# TODO: Change the color of the registration button (?? header has been changed, maybe this isnt needed)
# TODO: Add a 404 page
# TODO: CLEAN UP CODE AND PAGES
# TODO: Add Resources Page - https://anime.mit.edu/resources/ inspired
# TODO: 

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


registration_form = "https://docs.google.com/forms/d/e/1FAIpQLSfI6Opr3IL-Gvt7f3go34lME8UWC0dMvBVzSx0HfaVezoRfwA/viewform?usp=dialog"
app = Flask(__name__)

DEFAULTS = ['default_dt', 'default_loc', 'default_why', 'default_what']

# Security headers
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # Only set HSTS when using HTTPS
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@app.route('/reg')
def reg():
    return redirect(registration_form)

@app.route('/', methods=['GET'])
def index():
    meeting_date = events.select().where(events.type == 'Meeting', events.date > datetime.now().date()).order_by(events.date.asc()).limit(1)
    if len(meeting_date) > 0:
        meeting_date = meeting_date[0].date.strftime('%B %d, %Y')
    else:
        meeting_date = None
    # get all the news from the database and sort it by date with the latest news first
    all_news = news.select().order_by(news.date.desc()).limit(10)
    # make an object with all the settings so i can do site_vars.default_dt and access the value
    site_vars = {}
    for setting in settings.select():
        site_vars[setting.name] = setting.value
    site_vars = type('obj', (object,), site_vars)
    return render_template('index.html', meeting_date=meeting_date, all_news=list(all_news), site_vars=site_vars)
@app.route('/media/<path:path>')
def media(path):
    # Prevent path traversal attacks
    return send_from_directory('media', path)
@app.route('/short/<name>')
def short(name):
    # Sanitize name parameter to prevent directory traversal
    # Check for path separators, parent directory references, null bytes, and dots
    if (not name or 
        os.path.sep in name or 
        name.startswith('.') or 
        '..' in name or 
        '\x00' in name):
        return "Invalid short link", 400
    
    try:
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'short.json')
        with open(json_path, 'r') as f:
            json_file = json.load(f)
        if name.lower() in json_file:
            return redirect(json_file[name.lower()]['url'])
        return "Short link not found", 404
    except IOError as e:
        # Log error for debugging but don't expose details to user
        app.logger.error(f"Error reading short.json: {e}")
        return "Error accessing short links", 500
    except json.JSONDecodeError as e:
        # Log error for debugging but don't expose details to user
        app.logger.error(f"Error parsing short.json: {e}")
        return "Error parsing short links", 500
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
@app.route('/news')
def news_page():
    all_news = news.select().order_by(news.date.desc())
    return render_template('news.html', all_news=list(all_news))
@app.route('/officers')
def officers_page():
    all_officers = officers.select().order_by(officers.order.asc())
    return render_template('officers.html', officers=list(all_officers))

@app.route("/resources")
def resources():
    return render_template("resources.html")
if __name__ == '__main__':
    # create base settings if not exist: default_dt, default_loc, default_why, default_what
    for setting in DEFAULTS:
        if not settings.get_or_none(name=setting):
            settings.create(name=setting, value="TBD")

    # SECURITY: Debug mode should NEVER be enabled in production
    # Set debug=False for production deployments
    app.run(debug=False)