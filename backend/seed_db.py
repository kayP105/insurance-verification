from main import SessionLocal, MockInsurerPolicy, Base, engine # <-- Add Base and engine
import os # <-- Add os import

def seed_database():
    # --- ADD THIS LINE ---
    # Explicitly create tables if they don't exist (this creates the file)
    Base.metadata.create_all(bind=engine) 
    # --- END ADDITION ---

    # --- Print where it thinks the DB file is ---
    db_path = os.path.abspath("./project.db")
    print(f"Attempting to seed database at: {db_path}")
    # --- END PRINT ---
    
    db = SessionLocal()
    
    print("Deleting existing data...")
    db.query(MockInsurerPolicy).delete()
    print("Existing data deleted.")

    print("Adding new policy data...")
    policies = [
        MockInsurerPolicy(
            policy_number="HO 39-001234-5", 
            policy_holder_name="John A. Smith and Jane B. Smith", 
            coverage_type="Home", 
            coverage_limit=500000,
            is_active=True
        ),
        MockInsurerPolicy(
            policy_number="AU 40-004567-8", 
            policy_holder_name="John A. Smith and Jane B. Smith", 
            coverage_type="Auto", 
            coverage_limit=300000,
            is_active=True
        ),
        MockInsurerPolicy(
            policy_number="UB 50-007890-1", 
            policy_holder_name="John A. Smith and Jane B. Smith", 
            coverage_type="Umbrella", 
            coverage_limit=1000000,
            is_active=True
        ),
    ]
    
    db.add_all(policies)
    print("New data added to session.")
    
    try:
        db.commit()
        print("✅ Database commit successful.")
    except Exception as e:
        print(f"❌ Database commit FAILED: {e}")
        db.rollback() # Rollback changes if commit fails
    finally:
        db.close()
        print("Database session closed.")

if __name__ == "__main__":
    seed_database()