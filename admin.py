from flask import Flask, render_template, send_from_directory
import anilist

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('admin.html', text="<p></p>")


if __name__ == '__main__':
    app.run(debug=True)
    