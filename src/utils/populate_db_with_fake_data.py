import random
from faker import Faker
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# CREDENTIALS
HOSTNAME = os.getenv("HOSTNAME")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")

db = mysql.connector.connect(
    host=HOSTNAME,
    user=USERNAME,
    password=PASSWORD,
    database=DATABASE
)
cursor = db.cursor()

fake = Faker()
Faker.seed(0)

DOG_NAMES = [
    "Max", "Buddy", "Brownie", "Princess", "Bantay", "Choco", "Shadow", "Lucky",
    "King", "Queen", "Sasha", "Bella", "Rocky", "Coco", "Pepper", "Snowy", "Bruno",
    "Milo", "Mochi", "Toby", "Sky", "Panda", "Angel", "Sammy", "Cookie", "Chambe", "Chachi"
]

DOG_BREEDS = [
    "Aspin", "Shih Tzu", "Chihuahua", "Labrador", "Pomeranian", "Beagle",
    "Golden Retriever", "Bulldog", "Pug", "Dachshund", "Siberian Husky",
    "Poodle", "Rottweiler", "Jack Russell Terrier", "Maltese", "German Shepherd",
    "Doberman", "Pit Bull"
]

HEALTH_PROBLEMS = [
    "Ear Infection",
    "Fleas and Ticks",
    "Diarrhea",
    "Arthritis",
    "Skin Allergies",
    "Kennel Cough",
    "Dental Disease",
    "Hypothyroidism",
    "Heartworm Disease",
    "Urinary Tract Infection",
    "Pancreatitis",
    "Obesity"
]

HEALTH_PROBLEM_TREATMENTS = {
    "Ear Infection": "Antibiotics, Ear Drops, Antifungal Treatment, Steroid Therapy",
    "Fleas and Ticks": "Topical Flea Treatment, Oral Flea Medications, Tick Removal, Flea Collars",
    "Diarrhea": "Hydration Therapy, Probiotics, Antidiarrheal Medications, Prescription Diet",
    "Arthritis": "Non-steroidal Anti-inflammatory Drugs (NSAIDs), Joint Supplements, Physical Therapy, Acupuncture",
    "Skin Allergies": "Antihistamines, Steroid Injections, Topical Creams, Omega-3 Supplements",
    "Kennel Cough": "Antibiotics, Cough Suppressants, Rest, Humidifier Use",
    "Dental Disease": "Teeth Cleaning, Antibiotics, Dental Surgery, Dental Chews",
    "Hypothyroidism": "Thyroid Hormone Replacement, Regular Blood Tests, Diet Management",
    "Heartworm Disease": "Heartworm Preventatives, Immiticide Injections, Corticosteroids, Antibiotics for secondary infections",
    "Urinary Tract Infection": "Antibiotics, Urinary Acidifiers, Increased Water Intake, Specialized Diet",
    "Pancreatitis": "Fasting, Fluids and Electrolytes, Pain Relief, Antiemetic Drugs",
    "Obesity": "Calorie-Restricted Diet, Increased Exercise, Weight Management Medications, Behavioral Modifications"
}


def generate_filipino_name():
    firstnames = ["Juan", "Maria", "Jose", "Ana", "Jasmine",
                  "Miguel", "Carmela", "Carlos", "Grace", "Kyle"]
    lastnames = ["Reyes", "Santos", "Gomez", "Cruz", "Ynciong", "Libao",
                 "Garcia", "Morales", "Dela Cruz", "Ramos", "Heredero"]
    return random.choice(firstnames), random.choice(lastnames)


def populate_vet():
    vets = []
    for _ in range(25):
        firstname, lastname = generate_filipino_name()
        email = fake.email()
        phone = fake.phone_number()
        vets.append((firstname, lastname, email, phone))
    cursor.executemany(
        "INSERT INTO vet (firstname, lastname, email, phone) VALUES (%s, %s, %s, %s)", vets)
    cursor.execute("SELECT id FROM vet")
    return [row[0] for row in cursor.fetchall()]


def populate_dog():
    dogs = []
    for _ in range(50):
        name = random.choice(DOG_NAMES)
        gender = random.choice([0, 1])
        breed = random.choice(DOG_BREEDS)
        dogs.append((name, gender, breed))
    cursor.executemany(
        "INSERT INTO dog (name, gender, breed) VALUES (%s, %s, %s)", dogs)
    cursor.execute("SELECT id FROM dog")
    return [row[0] for row in cursor.fetchall()]


def populate_litter(dog_ids):
    litters = []
    for _ in range(25):
        sire_id = random.choice(dog_ids)
        dam_id = random.choice(dog_ids)
        while sire_id == dam_id:
            dam_id = random.choice(dog_ids)
        birthdate = fake.date_between(start_date='-3y', end_date='today')
        birthplace = fake.city()
        litters.append((sire_id, dam_id, birthdate, birthplace))
    cursor.executemany(
        "INSERT INTO litter (sire_id, dam_id, birthdate, birthplace) VALUES (%s, %s, %s, %s)", litters)
    cursor.execute("SELECT id FROM litter")
    return [row[0] for row in cursor.fetchall()]


def update_dog_litter_ids(dog_ids, litter_ids):
    updates = []
    for dog_id in dog_ids:
        litter_id = random.choice(litter_ids)
        updates.append((litter_id, dog_id))
    cursor.executemany("UPDATE dog SET litter_id = %s WHERE id = %s", updates)


def populate_health_record(dog_ids, vet_ids):
    records = []
    for _ in range(25):
        dog_id = random.choice(dog_ids)
        vet_id = random.choice(vet_ids)
        records.append((dog_id, vet_id))
    cursor.executemany(
        "INSERT INTO health_record (dog_id, vet_id) VALUES (%s, %s)", records)


def populate_health_problem():
    cursor.execute("SELECT id FROM health_record")
    health_record_ids = [row[0] for row in cursor.fetchall()]
    problems = []
    for _ in range(25):
        health_record_id = random.choice(health_record_ids)
        problem = random.choice(HEALTH_PROBLEMS)
        date = fake.date_between(start_date='-3y', end_date='today')
        treatment = HEALTH_PROBLEM_TREATMENTS[problem]
        problems.append((health_record_id, problem, date, treatment))
    cursor.executemany(
        "INSERT INTO health_problem (health_record_id, problem, date, treatment) VALUES (%s, %s, %s, %s)", problems)


try:
    db.start_transaction()

    vet_ids = populate_vet()
    dog_ids = populate_dog()
    litter_ids = populate_litter(dog_ids)
    update_dog_litter_ids(dog_ids, litter_ids)
    populate_health_record(dog_ids, vet_ids)
    populate_health_problem()

    db.commit()
    print("Database populated successfully!")

except mysql.connector.Error as err:
    print(f"Error occurred: {err}")
    db.rollback()

finally:
    cursor.close()
    db.close()
