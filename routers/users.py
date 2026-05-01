from fastapi import FastAPI,Depends,HTTPException,APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import models 
import schemas
import auth
from database import engine , get_db
from datetime import datetime, timedelta, timezone
import uvicorn
#models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="USER Endpoints")


#roles = {"company_admin":"company_admin","user":"user"}

roles = {"admin":"admin","user":"user"}

#prefix means that every endpoint will start with it
router = APIRouter(prefix="/users",tags=["Users"])

@router.post("/register",response_model=schemas.UserOut)
def register(user:schemas.UserCreate,db:Session= Depends(get_db)):
    try:
        if user.role not in roles.values():
            raise HTTPException(status_code=400,detail="Invalid Role")
        #if user already exists of same name then raise the exception
        db_user = db.query(models.User).filter(models.User.name == user.name).first()
        if db_user:
            raise HTTPException(status_code=400,detail="User already exists")
        
        hashed_password = auth.get_password_hash(user.password)
        new_user = models.User(
            name = user.name,
            password = hashed_password,
            role = user.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=f"Database Error {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Unexpected Error:{str(e)}")
    
@router.post("/users/login",response_model=schemas.TokenResponse)
def login(form_data:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.name==form_data.username).first()
        if not user or not auth.verify_password(form_data.password,user.password):
            raise HTTPException(status_code=400,detail="Invalid username or password")
        access_token = auth.create_access_token(
            data={"sub":user.name,"role":user.role}
        )
        return {"access_token":access_token,"token_type":"Bearer"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail=f"Database Error : {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Unexpected Error : {str(e)}")
    
#ALL subscriptions which we are providing

@router.get("/subscriptions",response_model=list[schemas.SubscriptionOut])
def get_subscriptions(db:Session=Depends(get_db)):
    try:
        subscriptions = db.query(models.Subscription).all()
        if subscriptions:
            return subscriptions
        raise HTTPException(status_code=400,detail="Currently no subscriptions")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail=f"Database error while fetching Subscriptions {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Unexpected Error {str(e)}")

#Allowing users to subcribe 
@router.post("/users/subscribe",response_model = schemas.UserSubscriptionOut)
def subscribe(subscription_id:int,user:models.User = Depends(auth.get_current_user),db:Session=Depends(get_db)):
    subscription=None
    try:
        try:
        #fetch the subscription
            subscription = db.query(models.Subscription).filter(models.Subscription.id==subscription_id).first()
            if not subscription:
                raise HTTPException(status_code=404,detail="You are Entering wrong ID " )
            existing = db.query(models.UserSubscription).filter_by(user_id=user.id, subscription_id=subscription.id, active=True).first()
            if existing:
                raise HTTPException(status_code=400, detail="User already subscribed to this plan")
        #Creating the user subscription
            start_date = datetime.now(timezone.utc)
            if subscription.renewal_type == "monthly":
                expiry_date = start_date + timedelta(days=30)
            elif subscription.renewal_type == "yearly":
                expiry_date = start_date + timedelta(days=365)
            else:
                raise HTTPException(status_code=400,detail="Invalid renewal type")
            
            user_sub = models.UserSubscription(
            user_id = user.id,
            subscription_id = subscription.id,
            start_date = start_date,
            expiry_date = expiry_date,
            active = True
        )
            db.add(user_sub)
            db.commit()
            db.refresh(user_sub)
            return user_sub
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500,detail="Database Error while creating subscriptions")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500,detail=f"Unexpected Error {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"ERROR IS {str(e)}")

    
    
    
#Chceking that the user has subscribed or not to our services
@router.get("/users/subscribers",response_model=schemas.UserSubscriptionOut)
def get_user_subscribers(user:models.User=Depends(auth.get_current_user),db:Session=Depends(get_db)):
    try:
        subscriptions = db.query(models.UserSubscription).filter(
            models.UserSubscription.user_id == user.id,
            models.UserSubscription.active ==True).first()
        if not subscriptions:
            raise HTTPException(status_code=404,detail="No active susbcription")
        return subscriptions
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500,detail=f"Database Error while fetching user subscriptions : {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Unexpected Error : {str(e)}")

#Updating the password ,username
@router.put("/users/update",response_model=schemas.UserOut)
def update_user(update_data:schemas.Userupdate,db:Session=Depends(get_db),current_user:models.User=Depends(auth.get_current_user)):
    try:
        user = db.query(models.User).filter(models.User.id==current_user.id).first()
        if not user:
            raise HTTPException(status_code=401,detail="User Not Found")
        #Update the name if it is provided
        if update_data.name:
            user.name = update_data.name
        #update passowrd and also hash it
        if update_data.password:
            hashed_pw = auth.get_password_hash(update_data.password)
            user.password = hashed_pw
            
        db.commit()
        db.refresh(user)
        
        return user
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Unexpected Error {str(e)}")
    
    
if __name__=="__main__":
    uvicorn.run(app)
            
