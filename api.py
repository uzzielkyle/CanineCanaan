from flask import Flask, make_response, jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

load_dotenv(verbose=True, override=True)

app = Flask(__name__)
app.config["MYSQL_HOST"] = os.getenv("HOSTNAME")
app.config["MYSQL_USER"] = os.getenv("USERNAME")
app.config["MYSQL_PASSWORD"] = os.getenv("PASSWORD")
app.config["MYSQL_DB"] = os.getenv("DATABASE")
app.config["MYSQL_PORT"] = int(os.getenv("PORT"))

app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


def data_fetch(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data


@app.route("/")
def index():
    return "<p>Hello World!</p>"


@app.route("/dogs", methods=["GET"])
def get_dogs():
    data = data_fetch("""SELECT * FROM dog""")
    return make_response(jsonify(data), 200)


if __name__ == "__main__":
    app.run(debug=True)
