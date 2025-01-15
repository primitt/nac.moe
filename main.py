from flask import Flask, render_template, send_from_directory
from datetime import datetime, timedelta

# TODO: Create admin panel
# TODO: Create a monthly manga recommendations page
# TODO: Create an events page
# TODO: Create a meet the board page
# TODO: Add contact information and proper, nice footer


skip_meeting = ["2025-01-21"]
def next_first_or_third_tuesday(start_date=None):
    if not start_date:
        start_date = datetime.now()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    first_day_of_next_month = (start_date.replace(day=1) + timedelta(days=31)).replace(day=1)
    first_day_of_current_month = start_date.replace(day=1)
    tuesday_count = 0
    
    for day in range(31):
        current_date = first_day_of_current_month + timedelta(days=day)
        if current_date.weekday() == 1:
            tuesday_count += 1
            if tuesday_count in [1, 3] and current_date >= start_date and current_date.strftime('%Y-%m-%d') not in skip_meeting:
                return current_date
    tuesday_count = 0
    for day in range(31): 
        current_date = first_day_of_next_month + timedelta(days=day)
        if current_date.weekday() == 1:
            tuesday_count += 1
            if tuesday_count in [1, 3]:
                return current_date


app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    next_tuesday = next_tuesday = next_first_or_third_tuesday().strftime('%m/%d/%Y').lstrip('0').replace('/0', '/')
    return render_template('index.html', next_tuesday=next_tuesday)
@app.route('/media/<path>')
def media(path):
    return send_from_directory('media', path)
if __name__ == '__main__':
    app.run(debug=True)