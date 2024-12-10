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
```

Make sure to replace with your actual database credentials.

### 4\. Run the Application

Start the Flask application with the following command:

```bash
flask --app src/api.py run
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
├── app.py                  # Flask application entry point
├── populate_db.py          # Script to populate the database with fake data
├── requirements.txt        # List of project dependencies
├── .env                    # Environment variables for database credentials
├── README.md               # This file
├── LICENSE                 # Project license
└── venv/                   # Virtual environment folder (generated after setup)
```

API Endpoints
-------------

As of now, this project is set up with a Flask API to handle the following operations:

-   **GET /dogs**: Fetch all dogs.
-   **POST /dogs**: Add a new dog to the database.
-   **GET /dogs/<dog_id>**: Get details for a specific dog.
-   **GET /vets**: Get all vets.
-   **POST /vets**: Add a new vet.
-   **GET /health-problems**: Get all health problems.
-   **POST /health-problems**: Add a new health problem.

These are just the basic endpoints that can be expanded to handle more specific features such as updating records, deleting entries, etc.

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