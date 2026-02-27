from app.database import init_db

if __name__ == "__main__":
    print("Enacting MIMS Pro Statutes... (Creating Tables)")
    init_db()
    print("tables created successfully!")