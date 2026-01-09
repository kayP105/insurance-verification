import os
from models import Base, MockInsurerPolicy
from db import SessionLocal, engine

def seed_database(): 
    
    
    Base.metadata.create_all(bind=engine) 
    
    db_path = os.path.abspath("./project.db")
    print(f" Database location: {db_path}")
   
    db = SessionLocal()
    
    print("Deleting existing policy data...")
    db.query(MockInsurerPolicy).delete()
    print(" Existing data deleted.")

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
        MockInsurerPolicy(
            policy_number="HO-41-002345-6",
            policy_holder_name="Emily R. Johnson",
            coverage_type="Home",
            coverage_limit=750000,
            is_active=True
        ),
        MockInsurerPolicy(
            policy_number="AU-42-005678-9",
            policy_holder_name="Michael Chen",
            coverage_type="Auto",
            coverage_limit=250000,
            is_active=True
        ),
        MockInsurerPolicy(
            policy_number="HO-43-008901-2",
            policy_holder_name="Sarah Williams",
            coverage_type="Home",
            coverage_limit=600000,
            is_active=False  # Inactive policy for testing
        ),
        MockInsurerPolicy(
            policy_number="AU-44-001122-3",
            policy_holder_name="David Martinez",
            coverage_type="Auto",
            coverage_limit=350000,
            is_active=True
        ),
        MockInsurerPolicy(
            policy_number="UB-45-003344-5",
            policy_holder_name="Lisa Anderson",
            coverage_type="Umbrella",
            coverage_limit=2000000,
            is_active=True
        ),
        MockInsurerPolicy(
            policy_number="HO-46-009988-7",
            policy_holder_name="Robert Taylor",
            coverage_type="Home",
            coverage_limit=450000,
            is_active=True
        ),
        MockInsurerPolicy(
            policy_number="AU-47-007766-4",
            policy_holder_name="Jennifer Brown",
            coverage_type="Auto",
            coverage_limit=400000,
            is_active=True
        ),
    ]
    
    db.add_all(policies)
    print("Added policies to session")
    
    try:
        db.commit()
        print("\nDATABASE SEEDING SUCCESSFUL")
        print("\nSeeded policies:")
        for p in policies:
            print(f"  • {p.policy_number} ({p.coverage_type}) - ${p.coverage_limit:,}")
    except Exception as e:
        print(f"\n DATABASE COMMIT FAILED: {e}")
        db.rollback() 
    finally:
        db.close()
        print("\nDatabase session closed.\n")


if __name__ == "__main__":
    seed_database()
