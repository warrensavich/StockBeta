import os

SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql://warren@localhost:5432/test_db")
