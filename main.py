from collections import OrderedDict
from datetime import datetime
import json
import os

from flask import Flask, redirect, render_template, request, send_from_directory

from db.db import events, news, officers, reviews, settings

# for future: i don't care that these are hardcoded -- this is a single-use website that needs to be simple to deploy and maintain.
registration_form = "https://docs.google.com/forms/d/e/1FAIpQLSfI6Opr3IL-Gvt7f3go34lME8UWC0dMvBVzSx0HfaVezoRfwA/viewform?usp=dialog"
app = Flask(__name__)

DEFAULTS = ['default_dt', 'default_loc', 'default_why', 'default_what']
SHORT_JSON_PATH = os.path.join(app.root_path, 'short.json')

for setting_name in DEFAULTS:
    settings.get_or_create(name=setting_name, defaults={'value': 'TBD'})


def is_valid_short_name(name):
    """Reject short-link names that could be interpreted as paths."""
    return bool(name and '/' not in name and '\\' not in name and
                not name.startswith('.') and '..' not in name and '\x00' not in name)


@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    if request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


@app.route('/reg')
def reg():
    return redirect(registration_form)


@app.route('/')
def index():
    next_meeting = (events.select()
                    .where((events.type == 'Meeting') &
                           (events.date >= datetime.now().date()))
                    .order_by(events.date.asc())
                    .first())
    meeting_date = next_meeting.date.strftime('%B %d, %Y') if next_meeting else None
    all_news = news.select().order_by(news.date.desc()).limit(10)
    site_vars = type('SiteSettings', (), {
        setting.name: setting.value for setting in settings.select()
    })
    return render_template('index.html', meeting_date=meeting_date,
                           all_news=list(all_news), site_vars=site_vars)


@app.route('/media/<path:path>')
def media(path):
    return send_from_directory(os.path.join(app.root_path, 'media'), path)


@app.route('/short/<name>')
def short(name):
    if not is_valid_short_name(name):
        return "Invalid short link", 400
    try:
        with open(SHORT_JSON_PATH, 'r', encoding='utf-8') as short_file:
            links = json.load(short_file)
        link = links.get(name.lower())
        return redirect(link['url']) if link else ("Short link not found", 404)
    except OSError as error:
        app.logger.error("Error reading short.json: %s", error)
        return "Error accessing short links", 500
    except json.JSONDecodeError as error:
        app.logger.error("Error parsing short.json: %s", error)
        return "Error parsing short links", 500


@app.route('/events')
def events_page():
    today = datetime.now().date()
    dated_events = []
    undated_events = []
    for event_item in events.select().order_by(events.date.asc()):
        if event_item.date is None:
            undated_events.append(event_item)
        elif event_item.date >= today or (event_item.date_end and event_item.date_end >= today):
            dated_events.append(event_item)

    parsed_events = OrderedDict()
    for event_item in dated_events:
        parsed_events.setdefault(event_item.date.strftime('%B %Y'), []).append(event_item)
    if undated_events:
        parsed_events['No Date'] = undated_events
    return render_template('events.html', parsed_events=parsed_events)


@app.route('/news')
def news_page():
    all_news = news.select().order_by(news.date.desc())
    return render_template('news.html', all_news=list(all_news))


@app.route('/officers')
def officers_page():
    current_officers = (officers.select()
                        .where(officers.current == True)
                        .order_by(officers.order.asc(nulls='LAST'), officers.id.asc()))
    return render_template('officers.html', officers=list(current_officers))


@app.route('/officers/past')
def past_officers_page():
    past_officers = (officers.select()
                     .where(officers.current == False)
                     .order_by(officers.year.desc(nulls='LAST'),
                               officers.order.asc(nulls='LAST'), officers.id.asc()))
    grouped_officers = OrderedDict()
    for officer in past_officers:
        grouped_officers.setdefault(officer.year or 'Unknown', []).append(officer)
    return render_template('past_officers.html', grouped_officers=grouped_officers)


@app.route('/recommendations')
@app.route('/reviews')
def monthly_picks_page():
    entries = reviews.select().order_by(reviews.date.desc(), reviews.id.desc())
    return render_template('reviews.html', reviews=list(entries))


@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route('/resources')
def resources_page():
    return render_template('resources.html')


@app.errorhandler(404)
def page_not_found(_error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG') == '1', port=5001)
