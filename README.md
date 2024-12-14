# CanineCanaan

CanineCanaan is a small Flask-based API for managing a dog breeding system. It tracks breeding records, health data, and vet visits. The project is named after the biblical "Promised Land," symbolizing an ideal environment for responsible dog breeding.

## Features

- **Dog Breeding Records:** Track litters, sire, and dam information.
- **Health Records:** Maintain medical history for each dog, including common health problems and treatments.
- **Vet Management:** Store vet details and link them to health records.
- **Flask API:** Expose endpoints to interact with the database and manage dog-related data.

## Project Setup

Follow these steps to set up and run the project locally.

### 1. Create a Virtual Environment

First, create a virtual environment to manage your project dependencies:

```bash
python -m venv .venv
```

Activate the virtual environment:

-   **On Windows:**

    ```bash
    .venv\Scripts\activate
    ```

-   **On macOS/Linux:**

    ```bash
    source venv/bin/activate
    ```

### 2\. Install Dependencies

Install the required dependencies by running the following command:

```bash
pip install -r requirements.txt
```

### 3\. Set Up Environment Variables

Create a `.env` file in the root directory of the project to store your database credentials.

Example:

```.env
HOSTNAME=localhost
USERNAME=your_username
PASSWORD=your_password
DATABASE=caninecanaan
PORT=3306
```

Make sure to replace with your actual database credentials.

### 4\. Run the Application

Start the Flask application with the following command:

```bash
flask --app api.py run
```

This will start the Flask development server, and you can access the API at `http://127.0.0.1:5000`.

### 5\. Populate the Database

Use the `utils/populate_db_with_fake_data.py` script to populate the database with random dog breeding data. The script will:

-   Generate random dogs with names and breeds.
-   Create litters for dogs and assign them.
-   Insert health records for dogs and link them to vets.

To populate the database, run:

```bash
python utils/populate_db_with_fake_data.py
```

File Structure
--------------

The project has the following structure:

```bash
caninecanaan/
├── .venv/                     # Virtual environment folder                       
├── tests/                 # Test cases for the Flask application
│   └── test_api.py        # API test cases
├── utils/                 # Utility scripts
│   └── populate_db_with_fake_data.py  # Script to populate the DB with fake data
├── .env                       # Environment variables for database credentials
├── .gitignore                 # List of files/folders to be ignored by Git
├── api.py                 # Flask application entry point (main API file)
├── LICENSE                    # Project license
├── README.md                  # Project documentation
└── requirements.txt           # List of project dependencies
```

API Endpoints
-------------

As of now, this project is set up with a Flask API to handle the following operations:

### Authentication Endpoints

| **Method** | **Endpoint** | **Description** | **Roles Required** |
| --- | --- | --- | --- |
| POST | /register | Register a new user (provide email, password, and role). | - |
| POST | /login | Login with credentials (email and password) and receive a JWT token. | - |
| POST | /logout | Logout the user by revoking the JWT token. | - |
| GET | /protected | Access a protected route that requires a valid JWT token. | - |

### Dog CRUD Endpoints

| **Method** | **Endpoint** | **Description** | **Roles Required** |
| --- | --- | --- | --- |
| GET | /dogs | Fetch all dogs. | `buyer`, `breeder`, `vet`, `admin` |
| GET | /dogs/<int:id> | Fetch details of a specific dog by ID. | `buyer`, `breeder`, `vet`, `admin` |
| POST | /dogs | Add a new dog to the database. | `admin`, `breeder` |
| PUT | /dogs/<int:id> | Update details of a specific dog by ID. | `admin`, `breeder` |
| DELETE | /dogs/<int:id> | Delete a dog by ID. | `admin` |

### Vet CRUD Endpoints

| **Method** | **Endpoint** | **Description** | **Roles Required** |
| --- | --- | --- | --- |
| GET | /vets | Fetch all vets. | `breeder`, `admin` |
| GET | /vets/<int:id> | Fetch details of a specific vet by ID. | `breeder`, `admin` |
| POST | /vets | Add a new vet to the database. | `admin` |
| PUT | /vets/<int:id> | Update details of a specific vet by ID. | `admin` |
| DELETE | /vets/<int:id> | Delete a vet by ID. | `admin` |

### Health Record CRUD Endpoints

| **Method** | **Endpoint** | **Description** | **Roles Required** |
| --- | --- | --- | --- |
| GET | /health_records | Fetch all health records. | `buyer`, `breeder`, `vet`, `admin` |
| GET | /health_records/<int:id> | Fetch details of a specific health record by ID. | `buyer`, `breeder`, `vet`, `admin` |
| POST | /health_records | Add a new health record. | `breeder`, `vet`, `admin` |
| PUT | /health_records/<int:id> | Update details of a specific health record by ID. | `breeder`, `vet`, `admin` |
| DELETE | /health_records/<int:id> | Delete a health record by ID. | `admin` |

### Litter CRUD Endpoints

| **Method** | **Endpoint** | **Description** | **Roles Required** |
| --- | --- | --- | --- |
| GET | /litters | Fetch all litters. | `buyer`, `breeder`, `admin` |
| GET | /litters/<int:id> | Fetch details of a specific litter by ID. | `buyer`, `breeder`, `admin` |
| POST | /litters | Add a new litter. | `breeder`, `admin` |
| PUT | /litters/<int:id> | Update details of a specific litter by ID. | `breeder`, `admin` |
| DELETE | /litters/<int:id> | Delete a litter by ID. | `admin` |

### Health Problem CRUD Endpoints

| **Method** | **Endpoint** | **Description** | **Roles Required** |
| --- | --- | --- | --- |
| GET | /health_problems | Fetch all health problems. | `buyer`, `breeder`, `vet`, `admin` |
| GET | /health_problems/<int:id> | Fetch details of a specific health problem by ID. | `buyer`, `breeder`, `vet`, `admin` |
| POST | /health_problems | Add a new health problem. | `vet`, `admin` |
| PUT | /health_problems/<int:id> | Update details of a specific health problem by ID. | `vet`, `admin` |
| DELETE | /health_problems/<int:id> | Delete a health problem by ID. | `admin` |


Troubleshooting
---------------

-   **Database Connection Error:**\
    Ensure that the `.env` file has the correct database credentials and that the MySQL server is running and accessible.

-   **Missing Dependencies:**\
    If any required package is missing, run `pip install -r requirements.txt` again.

Contributing
------------

We welcome contributions! If you have any improvements, bug fixes, or feature requests, feel free to fork the repository and create a pull request.

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature-name`).
3.  Make your changes and commit (`git commit -am 'Add new feature'`).
4.  Push to your branch (`git push origin feature-name`).
5.  Create a pull request.

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.