from flask import Flask, make_response, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_jwt_extended.exceptions import (
    NoAuthorizationError,
    InvalidHeaderError,
    JWTDecodeError,
    RevokedTokenError,
    WrongTokenError,
    FreshTokenRequired,
    UserLookupError,
    UserClaimsVerificationError
)
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from datetime import timedelta, datetime
from functools import wraps
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

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
jwt = JWTManager(app)

bcrypt = Bcrypt(app)


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


######################
### ERROR HANDLER ###
#####################
@app.errorhandler(Exception)
def handle_exception(e):
    return make_response(jsonify({"message": "An unexpected error occurred."}), 500)


@app.errorhandler(NoAuthorizationError)
def handle_no_authorization_error(e):
    return make_response(jsonify({"message": "Authorization token is missing. Please include it in the header."}), 401)


@app.errorhandler(InvalidHeaderError)
def handle_invalid_header_error(e):
    return make_response(jsonify({"message": "Invalid authorization header format. Ensure it's in the form 'Bearer <token>'."}), 401)


@app.errorhandler(JWTDecodeError)
def handle_jwt_decode_error(e):
    return make_response(jsonify({"message": "Error decoding token. The token may be malformed."}), 401)


@app.errorhandler(RevokedTokenError)
def handle_revoked_token_error(e):
    return make_response(jsonify({"message": "Token has been revoked. Please log in again."}), 401)


@app.errorhandler(WrongTokenError)
def handle_wrong_token_error(e):
    return make_response(jsonify({"message": "Wrong token type used. Ensure you're using the correct token type."}), 401)


@app.errorhandler(FreshTokenRequired)
def handle_fresh_token_required_error(e):
    return make_response(jsonify({"message": "Fresh token is required to access this resource."}), 401)


@app.errorhandler(UserLookupError)
def handle_user_lookup_error(e):
    return make_response(jsonify({"message": "User not found. Please verify your credentials."}), 404)


@app.errorhandler(UserClaimsVerificationError)
def handle_user_claims_error(e):
    return make_response(jsonify({"message": "User claims verification failed. Please contact support."}), 401)


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return make_response(
        jsonify({"message": "Token has expired, please log in again."}),
        401,
    )


@app.route("/")
def index():
    return make_response(
        jsonify(
            {"message": "Welcome to Canine Canaan!"}
        ),
        200
    )


############
### AUTH ###
############
@app.route("/register", methods=["POST"])
def register():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    role = request.json.get("role", None)

    if not email or not password or not role:
        return make_response(jsonify({"message": "email, password, and role are required"}), 400)

    try:
        hashed_password = bcrypt.generate_password_hash(
            password).decode('utf-8')

        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO user (email, password, role) VALUES (%s, %s, %s)""",
            (email, hashed_password, role),
        )
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        access_token = create_access_token(
            identity=email,
            additional_claims={"role": role},
            expires_delta=app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        )

        return make_response(
            jsonify(
                {
                    "message": "account is registered successfully",
                    "rows_affected": rows_affected,
                    "access_token": access_token
                }
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


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if not email or not password:
        return make_response(jsonify({"message": "email and password are required"}), 400)

    try:
        query = "SELECT * FROM user WHERE email = %s"
        result = data_fetch(query, (email,))

        if not result:
            return make_response(jsonify({"message": "user not found"}), 404)

        user = result[0]

        if not bcrypt.check_password_hash(user["password"], password):
            return make_response(jsonify({"message": "invalid password"}), 401)

        access_token = create_access_token(
            identity=user["email"],
            additional_claims={"role": user["role"]},
            expires_delta=app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        )
        return make_response(jsonify({"access_token": access_token}), 200)

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


@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]
        expiration = datetime.now(
        ) + app.config["JWT_ACCESS_TOKEN_EXPIRES"]

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO token_blacklist (jti, expiration) VALUES (%s, %s)",
            (jti, expiration),
        )
        mysql.connection.commit()
        cur.close()

        return make_response(jsonify({"message": "successfully logged out"}), 200)
    except Exception as e:
        return make_response(jsonify({"message": "An error occurred during logout", "error": str(e)}), 500)


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    try:
        jti = jwt_payload["jti"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1 FROM token_blacklist WHERE jti = %s", (jti,))
        result = cur.fetchone()
        cur.close()
        return result is not None
    except Exception as e:
        return False


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    claims = get_jwt()
    role = claims.get("role", None)
    return make_response(jsonify({"logged_in_as": current_user, "role": role}), 200)


def role_required(allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get("role")

            if user_role not in allowed_roles:
                return jsonify({"message": "access forbidden: insufficient permissions"}), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper


################
### DOG CRUD ###
################
@app.route("/dogs", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "vet", "admin"])
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
@jwt_required()
@role_required(["buyer", "breeder", "vet", "admin"])
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
@jwt_required()
@role_required(["admin", "breeder"])
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
@jwt_required()
@role_required(["admin", "breeder"])
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
@jwt_required()
@role_required(["admin"])
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


################
### VET CRUD ###
################
@app.route("/vets", methods=["GET"])
@jwt_required()
@role_required(["breeder", "admin"])
def get_vets():
    try:
        data = data_fetch("""SELECT * FROM vet""")
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


@app.route("/vets/<int:id>", methods=["GET"])
@jwt_required()
@role_required(["breeder", "admin"])
def get_vet(id):
    try:
        data = data_fetch("""SELECT * FROM vet WHERE id = %s""", (id,))
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


@app.route("/vets", methods=["POST"])
@jwt_required()
@role_required(["admin"])
def add_vet():
    try:
        info = request.get_json()
        if not info:
            return make_response(jsonify({"message": "Invalid JSON input"}), 400)

        try:
            firstname = info["firstname"]
            lastname = info["lastname"]
            email = info.get("email")
            phone = info.get("phone")

            if not (email or phone):
                return make_response(jsonify({"message": "Either email or phone is required"}), 400)

        except KeyError as e:
            return make_response(jsonify({"message": f"Missing field: {str(e)}"}), 400)

        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO vet (firstname, lastname, email, phone) VALUES (%s, %s, %s, %s)""",
            (firstname, lastname, email, phone),
        )
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        return make_response(
            jsonify(
                {"message": "vet added successfully",
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


@app.route("/vets/<int:id>", methods=["PUT"])
@jwt_required()
@role_required(["admin"])
def update_vet(id):
    try:
        info = request.get_json()

        if not info or not isinstance(info, dict):
            return make_response(
                jsonify({"message": "Invalid JSON input"}), 400
            )

        fields = []
        params = []
        for field, value in info.items():
            if field in {"firstname", "lastname", "email", "phone"}:
                fields.append(f"{field} = %s")
                params.append(value)

        if not fields:
            return make_response(
                jsonify(
                    {"message": "at least one field must be provided to update"}), 400
            )

        params.append(id)

        query = f"UPDATE vet SET {', '.join(fields)} WHERE id = %s"

        cur = mysql.connection.cursor()
        cur.execute(query, tuple(params))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        if rows_affected == 0:
            return make_response(
                jsonify({"message": f"no vet found with ID {id}"}), 404
            )

        return make_response(
            jsonify(
                {"message": "vet updated successfully",
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


@app.route("/vets/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def delete_vet(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""DELETE FROM vet WHERE id = %s""", (id,))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        if rows_affected == 0:
            return make_response(
                jsonify({"message": f"no vet found with ID {id}"}), 404
            )

        return make_response(
            jsonify(
                {"message": "vet deleted successfully",
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


##########################
### HEALTH RECORD CRUD ###
##########################
@app.route("/health_records", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "vet", "admin"])
def get_health_records():
    try:
        data = data_fetch(
            """SELECT
                    health_record.id,
                    health_record.vet_id,
                    CONCAT_WS(' ', vet.firstname, vet.lastname) AS vet,
                    health_record.dog_id,
                    dog.name AS dog,
                    dog.breed
                FROM health_record
                JOIN dog ON health_record.dog_id = dog.id
                JOIN vet ON health_record.vet_id = vet.id"""
        )
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


@app.route("/health_records/<int:id>", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "vet", "admin"])
def get_health_record(id):
    try:
        data = data_fetch(
            """SELECT
                    health_record.id,
                    health_record.vet_id,
                    CONCAT_WS(' ', vet.firstname, vet.lastname) AS vet,
                    health_record.dog_id,
                    dog.name AS dog,
                    dog.breed
                FROM health_record
                JOIN dog ON health_record.dog_id = dog.id
                JOIN vet ON health_record.vet_id = vet.id
                WHERE health_record.id = %s""", (id,)
        )
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


@app.route("/health_records", methods=["POST"])
@jwt_required()
@role_required(["breeder", "vet", "admin"])
def add_health_record():
    try:
        info = request.get_json()
        if not info:
            return make_response(
                jsonify({"message": "Invalid JSON input"}), 400
            )

        try:
            vet_id = info["vet_id"]
            dog_id = info["dog_id"]

        except KeyError as e:
            return make_response(
                jsonify({"message": f"Missing field: {str(e)}"}), 400
            )

        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO health_record (vet_id, dog_id) VALUES (%s, %s)""",
            (vet_id, dog_id),
        )
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        return make_response(
            jsonify(
                {"message": "health record added successfully",
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


@app.route("/health_records/<int:id>", methods=["PUT"])
@jwt_required()
@role_required(["breeder", "vet", "admin"])
def update_health_record(id):
    try:
        info = request.get_json()

        if not info or not isinstance(info, dict):
            return make_response(
                jsonify({"message": "Invalid JSON input"}), 400
            )

        fields = []
        params = []
        for field, value in info.items():
            if field in {"vet_id", "dog_id"}:
                fields.append(f"{field} = %s")
                params.append(value)

        if not fields:
            return make_response(
                jsonify(
                    {"message": "at least one field must be provided to update"}), 400
            )

        params.append(id)

        query = f"UPDATE health_record SET {', '.join(fields)} WHERE id = %s"

        cur = mysql.connection.cursor()
        cur.execute(query, tuple(params))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        if rows_affected == 0:
            return make_response(
                jsonify({"message": f"no health record found with ID {id}"}), 404
            )

        return make_response(
            jsonify(
                {"message": "health record updated successfully",
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


@app.route("/health_records/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def delete_health_record(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""DELETE FROM health_record WHERE id = %s""", (id,))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        if rows_affected == 0:
            return make_response(
                jsonify({"message": f"no health record found with ID {id}"}), 404
            )

        return make_response(
            jsonify(
                {"message": "health record deleted successfully",
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


###################
### LITTER CRUD ###
###################
@app.route("/litters", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "admin"])
def get_litters():
    try:
        data = data_fetch(
            """SELECT
                    litter.id,
                    litter.sire_id,
                    sire.name as sire_name,
                    sire.breed as sire_breed,
                    litter.dam_id,
                    dam.name as dam_name,
                    dam.breed as dam_breed,
                    litter.birthdate,
                    litter.birthplace
                FROM litter
                JOIN dog sire ON sire.id = litter.sire_id
                JOIN dog dam ON dam.id = litter.dam_id"""
        )
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


@app.route("/litters/<int:id>", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "admin"])
def get_litter(id):
    try:
        data = data_fetch(
            """SELECT
                    litter.id,
                    litter.sire_id,
                    sire.name as sire_name,
                    sire.breed as sire_breed,
                    litter.dam_id,
                    dam.name as dam_name,
                    dam.breed as dam_breed,
                    litter.birthdate,
                    litter.birthplace
                FROM litter
                JOIN dog sire ON sire.id = litter.sire_id
                JOIN dog dam ON dam.id = litter.dam_id
                WHERE litter.id = %s""", (id,))
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


@app.route("/litters", methods=["POST"])
@jwt_required()
@role_required(["breeder", "admin"])
def add_litter():
    try:
        info = request.get_json()
        if not info:
            return make_response(
                jsonify({"message": "Invalid JSON input"}), 400
            )

        try:
            sire_id = info["sire_id"]
            dam_id = info["dam_id"]
            birthdate = info["birthdate"]
            birthplace = info["birthplace"]

        except KeyError as e:
            return make_response(
                jsonify({"message": f"Missing field: {str(e)}"}), 400
            )

        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO litter (sire_id, dam_id, birthdate, birthplace) VALUES (%s, %s, %s, %s)""",
            (sire_id, dam_id, birthdate, birthplace),
        )
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        return make_response(
            jsonify(
                {"message": "litter added successfully",
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


@app.route("/litters/<int:id>", methods=["PUT"])
@jwt_required()
@role_required(["breeder", "admin"])
def update_litter(id):
    try:
        info = request.get_json()

        if not info or not isinstance(info, dict):
            return make_response(
                jsonify({"message": "Invalid JSON input"}), 400
            )

        fields = []
        params = []
        for field, value in info.items():
            if field in {"sire_id", "dam_id", "birthdate", "birthplace"}:
                fields.append(f"{field} = %s")
                params.append(value)

        if not fields:
            return make_response(
                jsonify(
                    {"message": "at least one field must be provided to update"}), 400
            )

        params.append(id)

        query = f"UPDATE litter SET {', '.join(fields)} WHERE id = %s"

        cur = mysql.connection.cursor()
        cur.execute(query, tuple(params))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        if rows_affected == 0:
            return make_response(
                jsonify({"message": f"no litter found with ID {id}"}), 404
            )

        return make_response(
            jsonify(
                {"message": "litter updated successfully",
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


@app.route("/litters/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def delete_litter(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""DELETE FROM litter WHERE id = %s""", (id,))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        if rows_affected == 0:
            return make_response(
                jsonify({"message": f"no litter found with ID {id}"}), 404
            )

        return make_response(
            jsonify(
                {"message": "litter deleted successfully",
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


###########################
### HEALTH PROBLEM CRUD ###
###########################
@app.route("/health_problems", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "vet", "admin"])
def get_health_problems():
    try:
        data = data_fetch(
            """SELECT 
                health_problem.id,
                vet.id as vet_id,
                CONCAT_WS(' ', vet.firstname, vet.lastname) AS vet_name,
                dog.id as dog_id,
                dog.name as dog_name,
                dog.breed as dog_breed,
                health_problem.health_record_id,
                health_problem.problem,
                health_problem.date,
                health_problem.treatment
            FROM health_problem
            JOIN health_record ON health_record.id = health_problem.health_record_id
            JOIN vet ON health_record.vet_id = vet.id
            JOIN dog ON health_record.dog_id = dog.id"""
        )
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


@app.route("/health_problems/<int:id>", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "vet", "admin"])
def get_health_problem(id):
    try:
        data = data_fetch(
            """SELECT 
                health_problem.id,
                vet.id as vet_id,
                CONCAT_WS(' ', vet.firstname, vet.lastname) AS vet_name,
                dog.id as dog_id,
                dog.name as dog_name,
                dog.breed as dog_breed,
                health_problem.health_record_id,
                health_problem.problem,
                health_problem.date,
                health_problem.treatment
            FROM health_problem
            JOIN health_record ON health_record.id = health_problem.health_record_id
            JOIN vet ON health_record.vet_id = vet.id
            JOIN dog ON health_record.dog_id = dog.id WHERE health_problem.id = %s""", (id,))
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


@app.route("/health_problems", methods=["POST"])
@jwt_required()
@role_required(["vet", "admin"])
def add_health_problem():
    try:
        info = request.get_json()
        if not info:
            return make_response(
                jsonify({"message": "Invalid JSON input"}), 400
            )

        try:
            health_record_id = info["health_record_id"]
            problem = info["problem"]
            date = info["date"]
            treatment = info["treatment"]

        except KeyError as e:
            return make_response(
                jsonify({"message": f"Missing field: {str(e)}"}), 400
            )

        cur = mysql.connection.cursor()
        cur.execute(
            """INSERT INTO health_problem (health_record_id, problem, date, treatment) VALUES (%s, %s, %s, %s)""",
            (health_record_id, problem, date, treatment),
        )
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        return make_response(
            jsonify(
                {"message": "health problem added successfully",
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


@app.route("/health_problems/<int:id>", methods=["PUT"])
@jwt_required()
@role_required(["vet", "admin"])
def update_health_problem(id):
    try:
        info = request.get_json()

        if not info or not isinstance(info, dict):
            return make_response(
                jsonify({"message": "Invalid JSON input"}), 400
            )

        fields = []
        params = []
        for field, value in info.items():
            if field in {"health_record_id", "problem", "date", "treatment"}:
                fields.append(f"{field} = %s")
                params.append(value)

        if not fields:
            return make_response(
                jsonify(
                    {"message": "at least one field must be provided to update"}), 400
            )

        params.append(id)

        query = f"UPDATE health_problem SET {', '.join(fields)} WHERE id = %s"

        cur = mysql.connection.cursor()
        cur.execute(query, tuple(params))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        if rows_affected == 0:
            return make_response(
                jsonify({"message": f"no health problem found with ID {id}"}), 404
            )

        return make_response(
            jsonify(
                {"message": "health problem updated successfully",
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


@app.route("/health_problems/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def delete_health_problem(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""DELETE FROM health_problem WHERE id = %s""", (id,))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        if rows_affected == 0:
            return make_response(
                jsonify({"message": f"no health problem found with ID {id}"}), 404
            )

        return make_response(
            jsonify(
                {"message": "health problem deleted successfully",
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
