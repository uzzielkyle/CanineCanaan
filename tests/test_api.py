import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import app, bcrypt, DogSchema
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token
from unittest.mock import patch, MagicMock
from unittest import mock
import pytest

load_dotenv(verbose=True, override=True)


def mock_jwt_required(*args, **kwargs):
    pass


@pytest.fixture
def client():
    """Set up a test client and mock MySQL."""
    app.config["TESTING"] = True
    app.config["DEBUG"] = True
    app.config["DISABLE_BLACKLIST_CHECK"] = True

    with patch("api.mysql") as mock_mysql:
        mock_cursor = MagicMock()
        mock_mysql.connection.cursor.return_value = mock_cursor

        with mock.patch('flask_jwt_extended.view_decorators.jwt_required', side_effect=mock_jwt_required):
            with app.app_context():
                yield app.test_client(), mock_mysql


def generate_token(identity, role):
    return create_access_token(identity=identity, additional_claims={"role": role})

def setup_mock_db(mock_mysql, query_result=None, rowcount=0, side_effect=None):
    # Mock the cursor returned by mock_mysql.connection.cursor
    mock_cursor = mock_mysql.connection.cursor.return_value
    # Mock fetchall return value
    mock_cursor.fetchall.return_value = query_result or []
    # Mock rowcount
    mock_cursor.rowcount = rowcount
    # Add side_effect to simulate errors in the execute method if needed
    if side_effect:
        mock_cursor.execute.side_effect = side_effect
    else:
        # Normal query execution logging
        mock_cursor.execute.side_effect = lambda query, params=None: print(f"Executing Query: {query}, Params: {params}")





##############################
### TESTS FOR AUTH ROUTES ###
##############################
def test_register_success(client):
    client, mock_mysql = client

    setup_mock_db(mock_mysql, rowcount=1)

    response = client.post(
        "/auth/register",
        json={"email": "test@example.com",
              "password": "password123", "role": "admin"},
    )

    print(f"Register Response: {response.json}")
    assert response.status_code == 201
    assert "account is registered successfully" in response.get_json()[
        "message"]


def test_login_success(client):
    client, mock_mysql = client

    hashed_password = bcrypt.generate_password_hash(
        "password123").decode("utf-8")
    setup_mock_db(mock_mysql, query_result=[
        {"email": "test@example.com", "password": hashed_password, "role": "admin"}
    ])

    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )

    print(f"Login Response: {response.json}")
    assert response.status_code == 200
    assert "access_token" in response.get_json()




#######################################################################
# THESE TESTS WON'T WORK UNLESS YOU COMMENT OUT api.check_if_token_in_blacklist() FUNCTION FIRST
# WILL SOON FIND A WAY TO WORK THIS OUT
#######################################################################


#######################################
### TESTS FOR CRUD ROUTES (SUCCESS) ###
#######################################
def test_get_dogs_success(client):
    client, mock_mysql = client

    # Mock dogs data
    dogs = [
        {"id": 1, "name": "Buddy", "gender": 0, "breed": "Labrador"},
        {"id": 2, "name": "Bella", "gender": 1, "breed": "Beagle"},
    ]
    setup_mock_db(mock_mysql, query_result=dogs)

    token = generate_token("admin", "admin")
    response = client.get(
        "/dogs", headers={"Authorization": f"Bearer {token}"})

    print(f"Get Dogs Response: {response.json}")
    assert response.status_code == 200
    assert len(response.get_json()) == len(dogs)


def test_add_dog_success(client):
    client, mock_mysql = client

    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.post(
        "/dogs",
        json={"name": "Buddy", "gender": 0, "breed": "Labrador"},
        headers={"Authorization": f"Bearer {token}"},
    )

    print(f"Add Dog Response: {response.json}")
    assert response.status_code == 201
    assert "entry added successfully" in response.get_json()["message"]


def test_update_dog_success(client):
    client, mock_mysql = client

    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.put(
        "/dogs/1",
        json={"name": "Buddy Updated", "gender": 0},
        headers={"Authorization": f"Bearer {token}"},
    )

    print(f"Update Dog Response: {response.json}")
    assert response.status_code == 200
    assert "entry updated successfully" in response.get_json()["message"]


def test_delete_dog_success(client):
    client, mock_mysql = client

    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.delete(
        "/dogs/1", headers={"Authorization": f"Bearer {token}"})

    print(f"Delete Dog Response: {response.json}")
    assert response.status_code == 200
    assert "deleted successfully" in response.get_json()["message"]


def test_get_vets_success(client):
    client, mock_mysql = client

    vets = [
        {"id": 1, "firstname": "John", "lastname": "Doe",
            "email": "johndoe@example.com", "phone": "1234567890"},
        {"id": 2, "firstname": "Jane", "lastname": "Smith",
            "email": "janesmith@example.com", "phone": "9876543210"}
    ]
    setup_mock_db(mock_mysql, query_result=vets)

    token = generate_token("admin", "admin")
    response = client.get(
        "/vets", headers={"Authorization": f"Bearer {token}"})

    print(f"Get Vets Response: {response.json}")
    assert response.status_code == 200
    assert len(response.get_json()) == len(vets)


def test_add_vet_success(client):
    client, mock_mysql = client

    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.post(
        "/vets",
        json={"firstname": "John", "lastname": "Doe",
              "email": "johndoe@example.com", "phone": "1234567890"},
        headers={"Authorization": f"Bearer {token}"},
    )

    print(f"Add Vet Response: {response.json}")
    assert response.status_code == 201
    assert "vet entry added successfully" in response.get_json()["message"]


def test_update_vet_success(client):
    client, mock_mysql = client

    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.put(
        "/vets/1",
        json={"firstname": "John", "lastname": "Doe",
              "email": "newemail@example.com", "phone": "0987654321"},
        headers={"Authorization": f"Bearer {token}"},
    )

    print(f"Update Vet Response: {response.json}")
    assert response.status_code == 200
    assert "vet entry updated successfully" in response.get_json()["message"]


def test_delete_vet_success(client):
    client, mock_mysql = client

    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.delete(
        "/vets/1", headers={"Authorization": f"Bearer {token}"})

    print(f"Delete Vet Response: {response.json}")
    assert response.status_code == 200
    assert "vet deleted successfully" in response.get_json()["message"]


def test_get_health_records_success(client):
    client, mock_mysql = client

    health_records = [
        {"id": 1, "dog_id": 1, "vet_id": 1, "vet": "John Doe",
            "dog": "Buddy", "breed": "Labrador"},
        {"id": 2, "dog_id": 2, "vet_id": 2, "vet": "Jane Smith",
            "dog": "Bella", "breed": "Beagle"}
    ]
    setup_mock_db(mock_mysql, query_result=health_records)

    token = generate_token("admin", "admin")
    response = client.get(
        "/health_records", headers={"Authorization": f"Bearer {token}"})

    print(f"Get Health Records Response: {response.json}")
    assert response.status_code == 200
    assert len(response.get_json()) == len(health_records)


def test_add_health_record_success(client):
    client, mock_mysql = client

    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.post(
        "/health_records",
        json={"dog_id": 1, "vet_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )

    print(f"Add Health Record Response: {response.json}")
    assert response.status_code == 201
    assert "health record entry added successfully" in response.get_json()[
        "message"]


def test_update_health_record_success(client):
    client, mock_mysql = client

    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.put(
        "/health_records/1",
        json={"dog_id": 2, "vet_id": 2},
        headers={"Authorization": f"Bearer {token}"},
    )

    print(f"Update Health Record Response: {response.json}")
    assert response.status_code == 200
    assert "health record entry updated successfully" in response.get_json()[
        "message"]


def test_delete_health_record_success(client):
    client, mock_mysql = client

    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.delete(
        "/health_records/1", headers={"Authorization": f"Bearer {token}"})

    print(f"Delete Health Record Response: {response.json}")
    assert response.status_code == 200
    assert "health record deleted successfully" in response.get_json()[
        "message"]


def test_get_litters_success(client):
    client, mock_mysql = client

    litters = [
        {"id": 1, "sire_id": 1, "dam_id": 2,
            "birthdate": "2024-12-01", "birthplace": "Kennel A"},
        {"id": 2, "sire_id": 3, "dam_id": 4,
            "birthdate": "2024-12-05", "birthplace": "Kennel B"}
    ]
    setup_mock_db(mock_mysql, query_result=litters)

    token = generate_token("admin", "admin")
    response = client.get(
        "/litters", headers={"Authorization": f"Bearer {token}"})

    print(f"Get Litters Response: {response.json}")
    assert response.status_code == 200
    assert len(response.get_json()) == len(litters)


def test_add_litter_success(client):
    client, mock_mysql = client

    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.post(
        "/litters",
        json={"sire_id": 1, "dam_id": 2,
              "birthdate": "2024-12-01", "birthplace": "Kennel A"},
        headers={"Authorization": f"Bearer {token}"},
    )

    print(f"Add Litter Response: {response.json}")
    assert response.status_code == 201
    assert "litter entry added successfully" in response.get_json()["message"]


def test_update_litter_success(client):
    client, mock_mysql = client

    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.put(
        "/litters/1",
        json={"sire_id": 2, "dam_id": 3,
              "birthdate": "2024-12-02", "birthplace": "Kennel B"},
        headers={"Authorization": f"Bearer {token}"},
    )

    print(f"Update Litter Response: {response.json}")
    assert response.status_code == 200
    assert "litter entry updated successfully" in response.get_json()[
        "message"]


def test_delete_litter_success(client):
    client, mock_mysql = client

    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.delete(
        "/litters/1", headers={"Authorization": f"Bearer {token}"})

    print(f"Delete Litter Response: {response.json}")
    assert response.status_code == 200
    assert "litter deleted successfully" in response.get_json()["message"]


def test_get_health_problems_success(client):
    client, mock_mysql = client

    health_problems = [
        {"id": 1, "health_record_id": 1, "problem": "Fever",
            "date": "2024-12-01", "treatment": "Antibiotics"},
        {"id": 2, "health_record_id": 2, "problem": "Cough",
            "date": "2024-12-05", "treatment": "Cough Syrup"}
    ]
    setup_mock_db(mock_mysql, query_result=health_problems)

    token = generate_token("admin", "admin")
    response = client.get("/health_problems",
                          headers={"Authorization": f"Bearer {token}"})

    print(f"Get Health Problems Response: {response.json}")
    assert response.status_code == 200
    assert len(response.get_json()) == len(health_problems)


def test_add_health_problem_success(client):
    client, mock_mysql = client

    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.post(
        "/health_problems",
        json={"health_record_id": 1, "problem": "Fever",
              "date": "2024-12-01", "treatment": "Antibiotics"},
        headers={"Authorization": f"Bearer {token}"},
    )

    print(f"Add Health Problem Response: {response.json}")
    assert response.status_code == 201
    assert "health problem entry added successfully" in response.get_json()[
        "message"]


def test_update_health_problem_success(client):
    client, mock_mysql = client

    # Simulate successful update
    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.put(
        "/health_problems/1",
        json={"health_record_id": 1, "problem": "Cough",
              "date": "2024-12-01", "treatment": "Cough Syrup"},
        headers={"Authorization": f"Bearer {token}"},
    )

    print(f"Update Health Problem Response: {response.json}")
    assert response.status_code == 200
    assert "health problem entry updated successfully" in response.get_json()[
        "message"]


def test_delete_health_problem_success(client):
    client, mock_mysql = client

    # Simulate successful deletion
    setup_mock_db(mock_mysql, rowcount=1)

    token = generate_token("admin", "admin")
    response = client.delete("/health_problems/1",
                             headers={"Authorization": f"Bearer {token}"})

    print(f"Delete Health Problem Response: {response.json}")
    assert response.status_code == 200
    assert "health problem deleted successfully" in response.get_json()[
        "message"]


############################################
### TESTS FOR CRUD ROUTES (UNAUTHORIZED) ###
############################################
def test_get_dogs_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.get(
            "/dogs", headers={"Authorization": f"Bearer {token}"})

    print(f"Get Dogs Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_add_dog_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.post(
            "/dogs",
            json={"name": "Buddy", "gender": 0, "breed": "Labrador"},
            headers={"Authorization": f"Bearer {token}"},
        )

    print(f"Add Dog Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_update_dog_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.put(
            "/dogs/1",
            json={"name": "Buddy Updated", "gender": 0},
            headers={"Authorization": f"Bearer {token}"},
        )

    print(f"Update Dog Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_delete_dog_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.delete(
            "/dogs/1", headers={"Authorization": f"Bearer {token}"})

    print(f"Delete Dog Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_get_vets_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        # Assuming 'user' role is not authorized
        token = generate_token("user", "user")
        response = client.get(
            "/vets", headers={"Authorization": f"Bearer {token}"})

    print(f"Get Vets Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_add_vet_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.post(
            "/vets",
            json={"firstname": "Dr. John", "lastname": "Doe",
                  "email": "johndoe@example.com", "phone": "123456789"},
            headers={"Authorization": f"Bearer {token}"},
        )

    print(f"Add Vet Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_update_vet_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.put(
            "/vets/1",
            json={"firstname": "Dr. John", "lastname": "Doe Updated",
                  "email": "johndoe@example.com", "phone": "987654321"},
            headers={"Authorization": f"Bearer {token}"},
        )

    print(f"Update Vet Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_delete_vet_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.delete(
            "/vets/1", headers={"Authorization": f"Bearer {token}"})

    print(f"Delete Vet Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_get_health_records_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        # Assuming 'user' role is not authorized
        token = generate_token("user", "user")
        response = client.get(
            "/health_records", headers={"Authorization": f"Bearer {token}"})

    print(f"Get Health Records Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_add_health_record_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.post(
            "/health_records",
            json={"dog_id": 1, "vet_id": 1},
            headers={"Authorization": f"Bearer {token}"},
        )

    print(f"Add Health Record Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_update_health_record_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.put(
            "/health_records/1",
            json={"dog_id": 1, "vet_id": 2},
            headers={"Authorization": f"Bearer {token}"},
        )

    print(f"Update Health Record Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_delete_health_record_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.delete(
            "/health_records/1", headers={"Authorization": f"Bearer {token}"})

    print(f"Delete Health Record Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_get_litters_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        # Assuming 'user' role is not authorized
        token = generate_token("user", "user")
        response = client.get(
            "/litters", headers={"Authorization": f"Bearer {token}"})

    print(f"Get Litters Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_add_litter_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.post(
            "/litters",
            json={"sire_id": 1, "dam_id": 2,
                  "birthdate": "2024-12-14", "birthplace": "Kennel"},
            headers={"Authorization": f"Bearer {token}"},
        )

    print(f"Add Litter Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_update_litter_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.put(
            "/litters/1",
            json={"sire_id": 2, "dam_id": 3,
                  "birthdate": "2024-12-15", "birthplace": "Clinic"},
            headers={"Authorization": f"Bearer {token}"},
        )

    print(f"Update Litter Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_delete_litter_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.delete(
            "/litters/1", headers={"Authorization": f"Bearer {token}"})

    print(f"Delete Litter Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_get_health_problems_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        # Assuming 'user' role is not authorized
        token = generate_token("user", "user")
        response = client.get("/health_problems",
                              headers={"Authorization": f"Bearer {token}"})

    print(f"Get Health Problems Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_add_health_problem_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.post(
            "/health_problems",
            json={"health_record_id": 1,
                  "problem": "Cough", "date": "2024-12-14"},
            headers={"Authorization": f"Bearer {token}"},
        )

    print(f"Add Health Problem Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_update_health_problem_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.put(
            "/health_problems/1",
            json={"health_record_id": 2,
                  "problem": "Cough Updated", "date": "2024-12-15"},
            headers={"Authorization": f"Bearer {token}"},
        )

    print(f"Update Health Problem Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]


def test_delete_health_problem_unauthorized(client):
    client, mock_mysql = client

    with patch("api.role_required", side_effect=lambda allowed_roles: lambda fn: fn):
        token = generate_token("user", "user")
        response = client.delete("/health_problems/1",
                                headers={"Authorization": f"Bearer {token}"})

    print(f"Delete Health Problem Unauthorized Response: {response.json}")
    assert response.status_code == 403
    assert "access forbidden: insufficient permissions" in response.get_json()[
        "message"]

