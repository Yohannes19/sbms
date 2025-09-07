# import os
# import sys

# # ensure project root is on sys.path so "import app" works when running this script
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

# from app.db import SessionLocal, engine
# from app.models import Tenant, Room, Contract, Payment, User
# from sqlalchemy.orm import Session

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# if __name__ == "__main__":
#     db: Session = next(get_db())
#     print("Database session `db` is available. You can also import your models, e.g., `User` and `Post`.")
#     print("Example: user = db.query(User).first()")
#     import code
#     code.interact(local=globals())