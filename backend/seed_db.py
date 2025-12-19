import os
from models import Base, MockInsurerPolicy
from db import SessionLocal, engine

def seed_database(): 
    
    
    Base.metadata.create_all(bind=engine) 
    
    db_path = os.path.abspath("./project.db")
    print(f"✓ Database location: {db_path}")
   
    db = SessionLocal()
    
    print("Deleting existing policy data...")
    db.query(MockInsurerPolicy).delete()
    print("✓ Existing data deleted.")

    print("\nAdding new policy data with normalized policy numbers...")
    
    
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
    print("✓ Added 3 policies to session")
    
    try:
        db.commit()
        print("\n✓✓✓ DATABASE SEEDING SUCCESSFUL ✓✓✓")
        print("\nSeeded policies:")
        for p in policies:
            print(f"  • {p.policy_number} ({p.coverage_type}) - ${p.coverage_limit:,}")
    except Exception as e:
        print(f"\n❌ DATABASE COMMIT FAILED: {e}")
        db.rollback() 
    finally:
        db.close()
        print("\n✓ Database session closed.\n")


if __name__ == "__main__":
    seed_database()
