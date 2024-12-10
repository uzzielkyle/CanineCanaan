from flask import Flask, make_response, jsonify, request
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


def data_fetch(query, params=None):
    try:
        cur = mysql.connection.cursor()

        if params:
            cur.execute(query, params)

        else:
            cur.execute(query)

        data = cur.fetchall()
        return data

    except mysql.connection.Error as e:
        raise

    finally:
        cur.close()


@app.route("/")
def index():
    return "<p>Hello World!</p>"


@app.route("/dogs", methods=["GET"])
def get_dogs():
    try:
        data = data_fetch("""SELECT * FROM dog""")
        return make_response(jsonify(data), 200)

    except mysql.connection.Error as e:
        return make_response(
            jsonify(
                {
                    "message": "database error occurred",
                    "error": str(e),
                }
            ),
            500,
        )

    except Exception as e:
        return make_response(
            jsonify(
                {
                    "message": "an unexpected error occurred",
                    "error": str(e),
                }
            ),
            500,
        )


@app.route("/dogs/<int:id>", methods=["GET"])
def get_dog(id):
    try:
        data = data_fetch("""SELECT * FROM dog WHERE id = %s""", (id,))
        return make_response(jsonify(data), 200)

    except mysql.connection.Error as e:
        return make_response(
            jsonify(
                {"message": "database error occurred", "error": str(e)}
            ),
            500
        )

    except Exception as e:
        return make_response(
            jsonify(
                {"message": "an unexpected error occurred", "error": str(e)}
            ),
            500
        )


@app.route("/dogs", methods=["POST"])
def add_dog():
    try:
        info = request.get_json()
        if not info:
            return make_response(
                jsonify({"message": "Invalid JSON input"}), 400
            )

        try:
            name = info["name"]
            litter_id = info["litter_id"]
            gender = info["gender"]
            breed = info["breed"]

        except KeyError as e:
            return make_response(
                jsonify({"message": f"Missing field: {str(e)}"}), 400
            )

        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO dog (name, litter_id, gender, breed) VALUES (%s, %s, %s, %s)""",
            (name, litter_id, gender, breed),
        )
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        return make_response(
            jsonify(
                {"message": "dog added successfully",
                    "rows_affected": rows_affected}
            ),
            201,
        )

    except mysql.connection.Error as e:
        return make_response(
            jsonify(
                {
                    "message": "database error occurred",
                    "error": str(e),
                }
            ),
            500,
        )

    except Exception as e:
        return make_response(
            jsonify(
                {
                    "message": "an unexpected error occurred",
                    "error": str(e),
                }
            ),
            500,
        )


@app.route("/dogs/<int:id>", methods=["PUT"])
def update_dog(id):
    try:
        info = request.get_json()

        if not info or not isinstance(info, dict):
            return make_response(
                jsonify({"message": "Invalid JSON input"}), 400
            )

        fields = []
        params = []
        for field, value in info.items():
            if field in {"name", "litter_id", "gender", "breed"}:
                fields.append(f"{field} = %s")
                params.append(value)

        if not fields:
            return make_response(
                jsonify(
                    {"message": "at least one field must be provided to update"}), 400
            )

        params.append(id)

        query = f"UPDATE dog SET {', '.join(fields)} WHERE id = %s"

        cur = mysql.connection.cursor()
        cur.execute(query, tuple(params))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        if rows_affected == 0:
            return make_response(
                jsonify({"message": f"no dog found with ID {id}"}), 404
            )

        return make_response(
            jsonify(
                {"message": "dog updated successfully",
                    "rows_affected": rows_affected}
            ),
            200,
        )

    except mysql.connection.Error as e:
        return make_response(
            jsonify(
                {"message": "database error occurred",
                    "error": str(e)}
            ),
            500,
        )

    except Exception as e:
        return make_response(
            jsonify(
                {"message": "an unexpected error occurred", "error": str(e)}
            ),
            500,
        )


@app.route("/dogs/<int:id>", methods=["DELETE"])
def delete_dog(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""DELETE FROM dog WHERE id = %s""", (id,))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        if rows_affected == 0:
            return make_response(
                jsonify({"message": f"no dog found with ID {id}"}), 404
            )

        return make_response(
            jsonify(
                {"message": "dog deleted successfully",
                    "rows_affected": rows_affected}
            ),
            200,
        )

    except mysql.connection.Error as e:
        return make_response(
            jsonify(
                {"message": "database error occurred",
                    "error": str(e)}
            ),
            500,
        )
    except Exception as e:
        return make_response(
            jsonify(
                {"message": "an unexpected error occurred.", "error": str(e)}
            ),
            500,
        )


if __name__ == "__main__":
    app.run(debug=True)
