from whoatmozilla import search

from flask import Flask, request, render_template
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def http_search():
    if request.method == 'POST':
        query = request.form['query']
        results = search(query)
    else:
        results = []

    return render_template("index.html", **locals())

if __name__ == "__main__":
    app.debug = True
    app.run()

