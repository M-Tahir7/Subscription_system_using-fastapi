#APIROUTER is used to group related endpoints together to keep the code clean organized and scalable.
from fastapi import APIRouter,Depends,HTTPException
#Depends is used in FastAPI to “inject” a function’s output into an endpoint, so you can reuse logic (like authentication, validation, or database access) across multiple endpoints without repeating code.
#HTTPException lets FastAPI return a clear HTTP error response instead of crashing when something goes wrong.
import schemas
import models
import auth
#it means we are using schemas.py models.py and auth.py
#ORM: Object relational mapping which is used to interact with database using python objects not query
#Session in SQLAlchemy is a workspace that tracks database changes and commits them
from sqlalchemy.orm import Session
#List means we are importing the list type hint so we can specify that the return type is a list of certain type 
# def get(names)->(List[str] means that the function returns list of string type
from typing import List
#here we are importing get_db function which is used in every endpoint to give them session 
from database import get_db
#we are importing sqlalchemyerror so we can catch and hanle any database related exceptions without crashing the app
#sqlalchemy catches specifically database-related errors while HTTPEception can't detect or handle
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/admins",tags=["For Admins"])

@router.get("/admins/All_users",response_model=list[schemas.AllUsers])
def all_users(db:Session=Depends(get_db),admin:models.User=Depends(auth.admin_required)):
    try:
        users = db.query(models.User).all()
        result=[]
        for user in users:
            subscription = db.query(models.UserSubscription).filter_by(user_id=user.id,active=True).first()
            result.append({
                "id":user.id,
                "name":user.name,
                "role":user.role,
                "subscribed":bool(subscription)
            })
            
        return result
    except SQLAlchemyError as e:
        raise HTTPException(status_code=401,detail=f"Database error while fetching users and subscriptions {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Unexpected Error {str(e)}")
    