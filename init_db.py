import os
from models.db_helper import init_db, seed_sample_data

if __name__ == "__main__":
    print("Initializing SQLite Database...")
    init_db()
    print("Seeding Sample Data...")
    seed_sample_data()
    print("Database setup complete! Default Admin login: admin / admin123")
