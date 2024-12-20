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
from marshmallow import Schema, fields, validate, ValidationError
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


###################
### DB FUNCTION ###
###################
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


##############################
### GENERIC CRUD FUNCTIONS ###
##############################
def get_entities(query):
    try:
        data = data_fetch(query=query)
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


def get_entity(query, id):
    try:
        data = data_fetch(query=query, params=(id,))
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


def add_entity(request, entity, schema_class):
    try:
        schema = schema_class()
        info = schema.load(request.get_json())

        fields = list(info.keys())
        placeholders = ", ".join(["%s"] * len(fields))
        columns = ", ".join(fields)
        query = f"INSERT INTO {entity} ({columns}) VALUES ({placeholders})"

        cur = mysql.connection.cursor()
        cur.execute(query, [info[field] for field in fields])
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        return make_response(
            jsonify(
                {
                    "message": f"{' '.join(str(entity).split('_'))} entry added successfully",
                    "rows_affected": rows_affected,
                }
            ),
            201,
        )

    except ValidationError as ve:
        return make_response(
            jsonify({"message": "validation error", "errors": ve.messages}), 400
        )

    except mysql.connection.Error as e:
        return make_response(
            jsonify({"message": "a database error occurred", "error": str(e)}), 500
        )

    except Exception as e:
        return make_response(
            jsonify({"message": "an unexpected error occurred",
                    "error": str(e)}), 500
        )


def update_entity(request, entity, schema_class, id):
    try:
        schema = schema_class(partial=True)
        info = schema.load(request.get_json())

        if not info:
            return make_response(
                jsonify(
                    {"message": "At least one valid field must be provided to update"}), 400
            )

        fields = [f"{field} = %s" for field in info.keys()]
        params = list(info.values())
        params.append(id)

        query = f"UPDATE {entity} SET {', '.join(fields)} WHERE id = %s"

        cur = mysql.connection.cursor()
        cur.execute(query, tuple(params))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        if rows_affected == 0:
            return make_response(
                jsonify(
                    {"message": f"No {' '.join(str(entity).split('_'))} entry found with ID {id}"}
                ), 404
            )

        return make_response(
            jsonify(
                {
                    "message": f"{' '.join(str(entity).split('_'))} entry updated successfully",
                    "rows_affected": rows_affected,
                }
            ),
            200,
        )

    except ValidationError as ve:
        return make_response(
            jsonify({"message": "Validation error", "errors": ve.messages}), 400
        )

    except mysql.connection.Error as e:
        return make_response(
            jsonify({"message": "A database error occurred", "error": str(e)}), 500
        )

    except Exception as e:
        return make_response(
            jsonify({"message": "An unexpected error occurred",
                    "error": str(e)}), 500
        )


def delete_entity(entity, id):
    try:
        cur = mysql.connection.cursor()
        cur.execute(f"""DELETE FROM {entity} WHERE id = %s""", (id,))
        mysql.connection.commit()
        rows_affected = cur.rowcount
        cur.close()

        if rows_affected == 0:
            return make_response(
                jsonify(
                    {"message": f"no {' '.join(str(entity).split('_'))} found with ID {id}"}), 404
            )

        return make_response(
            jsonify(
                {"message": f"{' '.join(str(entity).split('_'))} deleted successfully",
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


######################
### ERROR HANDLERS ###
#####################
@app.errorhandler(Exception)
def handle_exception(e):
    return make_response(jsonify({"message": "an unexpected error occurred.", "error": str(e)}), 500)


@app.errorhandler(NoAuthorizationError)
def handle_no_authorization_error(e):
    return make_response(jsonify({"message": "authorization token is missing. Please include it in the header.", "error": str(e)}), 401)


@app.errorhandler(InvalidHeaderError)
def handle_invalid_header_error(e):
    return make_response(jsonify({"message": "invalid authorization header format. Ensure it's in the form 'Bearer <token>'.", "error": str(e)}), 401)


@app.errorhandler(JWTDecodeError)
def handle_jwt_decode_error(e):
    return make_response(jsonify({"message": "error decoding token. The token may be malformed.", "error": str(e)}), 401)


@app.errorhandler(RevokedTokenError)
def handle_revoked_token_error(e):
    return make_response(jsonify({"message": "token has been revoked. Please log in again.", "error": str(e)}), 401)


@app.errorhandler(WrongTokenError)
def handle_wrong_token_error(e):
    return make_response(jsonify({"message": "wrong token type used. Ensure you're using the correct token type.", "error": str(e)}), 401)


@app.errorhandler(FreshTokenRequired)
def handle_fresh_token_required_error(e):
    return make_response(jsonify({"message": "fresh token is required to access this resource.", "error": str(e)}), 401)


@app.errorhandler(UserLookupError)
def handle_user_lookup_error(e):
    return make_response(jsonify({"message": "user not found. Please verify your credentials.", "error": str(e)}), 404)


@app.errorhandler(UserClaimsVerificationError)
def handle_user_claims_error(e):
    return make_response(jsonify({"message": "user claims verification failed. Please contact support.", "error": str(e)}), 401)


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return make_response(
        jsonify({"message": "Token has expired, please log in again."}),
        401,
    )


##############
### ROUTES ###
##############
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
@app.route("/auth/register", methods=["POST"])
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


@app.route("/auth/login", methods=["POST"])
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


@app.route("/auth/logout", methods=["POST"])
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
class DogSchema(Schema):
    id = fields.Int(dump_only=True)
    litter_id = fields.Int(allow_none=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    gender = fields.Int(
        required=True,
        validate=validate.OneOf([0, 1])
    )
    breed = fields.Str(required=True, validate=validate.Length(min=1))


@app.route("/dogs", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "vet", "admin"])
def get_dogs():
    response = get_entities(query="""SELECT * FROM dog""")
    return response


@app.route("/dogs/<int:id>", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "vet", "admin"])
def get_dog(id):
    response = get_entity(
        query="""SELECT * FROM dog WHERE id = %s""",
        id=id
    )
    return response


@app.route("/dogs", methods=["POST"])
@jwt_required()
@role_required(["admin", "breeder"])
def add_dog():
    response = add_entity(
        request=request,
        entity="dog",
        schema_class=DogSchema
    )
    return response


@app.route("/dogs/<int:id>", methods=["PUT"])
@jwt_required()
@role_required(["admin", "breeder"])
def update_dog(id):
    response = update_entity(
        request=request,
        entity="dog",
        schema_class=DogSchema,
        id=id
    )
    return response


@app.route("/dogs/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def delete_dog(id):
    response = delete_entity(entity="dog", id=id)
    return response


################
### VET CRUD ###
################
class VetSchema(Schema):
    id = fields.Int(dump_only=True)
    firstname = fields.Str(
        required=True, validate=validate.Length(min=1, max=45))
    lastname = fields.Str(
        required=True, validate=validate.Length(min=1, max=45))
    email = fields.Email(allow_none=True, validate=validate.Length(max=45))
    phone = fields.Str(allow_none=True, validate=validate.Length(max=45))


@app.route("/vets", methods=["GET"])
@jwt_required()
@role_required(["breeder", "admin"])
def get_vets():
    response = get_entities(query="""SELECT * FROM vet""")
    return response


@app.route("/vets/<int:id>", methods=["GET"])
@jwt_required()
@role_required(["breeder", "admin"])
def get_vet(id):
    response = get_entity(
        query="""SELECT * FROM vet WHERE id = %s""",
        id=id
    )
    return response


@app.route("/vets", methods=["POST"])
@jwt_required()
@role_required(["admin"])
def add_vet():
    response = add_entity(
        request=request,
        entity="vet",
        schema_class=VetSchema
    )
    return response


@app.route("/vets/<int:id>", methods=["PUT"])
@jwt_required()
@role_required(["admin"])
def update_vet(id):
    response = update_entity(
        request=request,
        entity="vet",
        schema_class=VetSchema,
        id=id
    )
    return response


@app.route("/vets/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def delete_vet(id):
    response = delete_entity(entity="vet", id=id)
    return response


##########################
### HEALTH RECORD CRUD ###
##########################
class HealthRecordSchema(Schema):
    id = fields.Int(dump_only=True)
    dog_id = fields.Int(required=True)
    vet_id = fields.Int(required=True)


@app.route("/health_records", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "vet", "admin"])
def get_health_records():
    response = get_entities(
        query="""SELECT
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
    return response


@app.route("/health_records/<int:id>", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "vet", "admin"])
def get_health_record(id):
    response = get_entity(
        query="""SELECT
                    health_record.id,
                    health_record.vet_id,
                    CONCAT_WS(' ', vet.firstname, vet.lastname) AS vet,
                    health_record.dog_id,
                    dog.name AS dog,
                    dog.breed
                FROM health_record
                JOIN dog ON health_record.dog_id = dog.id
                JOIN vet ON health_record.vet_id = vet.id
                WHERE health_record.id = %s""",
        id=id
    )
    return response


@app.route("/health_records", methods=["POST"])
@jwt_required()
@role_required(["breeder", "vet", "admin"])
def add_health_record():
    response = add_entity(
        request=request,
        entity="health_record",
        schema_class=HealthRecordSchema
    )
    return response


@app.route("/health_records/<int:id>", methods=["PUT"])
@jwt_required()
@role_required(["breeder", "vet", "admin"])
def update_health_record(id):
    response = update_entity(
        request=request,
        entity="health_record",
        schema_class=HealthRecordSchema,
        id=id
    )
    return response


@app.route("/health_records/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def delete_health_record(id):
    response = delete_entity(entity="health_record", id=id)
    return response


###################
### LITTER CRUD ###
###################
class LitterSchema(Schema):
    id = fields.Int(dump_only=True)
    sire_id = fields.Int(required=True)
    dam_id = fields.Int(required=True)
    birthdate = fields.Date(required=True)
    birthplace = fields.Str(
        required=True, validate=validate.Length(min=1, max=135))


@app.route("/litters", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "admin"])
def get_litters():
    response = get_entities(
        query="""SELECT
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
    return response


@app.route("/litters/<int:id>", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "admin"])
def get_litter(id):
    response = get_entity(
        query="""SELECT
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
                WHERE litter.id = %s""",
        id=id
    )
    return response


@app.route("/litters", methods=["POST"])
@jwt_required()
@role_required(["breeder", "admin"])
def add_litter():
    response = add_entity(
        request=request,
        entity="litter",
        schema_class=LitterSchema
    )
    return response


@app.route("/litters/<int:id>", methods=["PUT"])
@jwt_required()
@role_required(["breeder", "admin"])
def update_litter(id):
    response = update_entity(
        request=request,
        entity="litter",
        schema_class=LitterSchema,
        id=id
    )
    return response


@app.route("/litters/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def delete_litter(id):
    response = delete_entity(entity="litter", id=id)
    return response


###########################
### HEALTH PROBLEM CRUD ###
###########################
class HealthProblemSchema(Schema):
    id = fields.Int(dump_only=True)
    health_record_id = fields.Int(required=True)
    problem = fields.Str(
        required=True, validate=validate.Length(min=1, max=135))
    date = fields.Date(required=True)
    treatment = fields.Str(allow_none=True, validate=validate.Length(max=135))


@app.route("/health_problems", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "vet", "admin"])
def get_health_problems():
    response = get_entities(
        query="""SELECT 
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
    return response


@app.route("/health_problems/<int:id>", methods=["GET"])
@jwt_required()
@role_required(["buyer", "breeder", "vet", "admin"])
def get_health_problem(id):
    response = get_entity(
        query="""SELECT 
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
            JOIN dog ON health_record.dog_id = dog.id WHERE health_problem.id = %s""",
        id=id
    )
    return response


@app.route("/health_problems", methods=["POST"])
@jwt_required()
@role_required(["vet", "admin"])
def add_health_problem():
    response = add_entity(
        request=request,
        entity="health_problem",
        schema_class=HealthProblemSchema
    )
    return response


@app.route("/health_problems/<int:id>", methods=["PUT"])
@jwt_required()
@role_required(["vet", "admin"])
def update_health_problem(id):
    response = update_entity(
        request=request,
        entity="health_problem",
        schema_class=HealthProblemSchema,
        id=id
    )
    return response


@app.route("/health_problems/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required(["admin"])
def delete_health_problem(id):
    response = delete_entity(entity="health_problem", id=id)
    return response


if __name__ == "__main__":
    app.run(debug=True)
