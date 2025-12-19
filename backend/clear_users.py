from db import SessionLocal, engine
from models import Base, User  

def clear_users():
    Base.metadata.create_all(bind=engine)  
    db = SessionLocal()
    try:
        deleted = db.query(User).delete()  
        db.commit()
        print(f"Deleted {deleted} users.")
    finally:
        db.close()

if __name__ == "__main__":
    clear_users()
