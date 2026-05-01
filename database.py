from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.getenv("DATABASE_URL")) #communicate with the database

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#autoflash means don't commit until commit is called
#autocommit means don't save changes until I say so must call session.commit()
#bind means which database engine to use
Base = declarative_base()
#base class for defining tables/modes as python classes



def get_db():
    db = SessionLocal()
    try:
        yield db#provide the session
    finally:
        db.close()#close the session after the request is done
       