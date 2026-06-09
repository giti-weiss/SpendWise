from models.base import Base
"""
from models import import_all 
 import models.import_all# רק כדי לטעון מודלים
"""

print("IMPORT ALL LOADED")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SERVER ='D403-013'
DATABASE ='smart_Encomy'
DRIVER = 'ODBC Driver 17 for SQL Server'

connection_string = (
    f"mssql+pyodbc://@{SERVER}/{DATABASE}"
    f"?driver={DRIVER.replace(' ', '+')}"
    f"&trusted_connection=yes"
)

engine = create_engine(connection_string, echo=True)
"""
Base.metadata.create_all(bind=engine)
"""


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

