from datetime import datetime,timedelta,timezone
from jose import JWTError,jwt
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from fastapi import Depends,HTTPException,status
from sqlalchemy.orm import Session
from database import get_db
from dotenv import load_dotenv
load_dotenv()

import bcrypt
import models
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = HTTPBearer()

def create_access_token(data:dict,expires_delta:timedelta | None = None):
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token creation failed: {str(e)}")
    
    
def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str = payload.get("sub")   
        if username is None:
            raise HTTPException(status_code = 401,detail = "Invalid Token")
    except JWTError:
        raise HTTPException(status_code = 401,detail = "Invalid Token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token validation failed: {str(e)}")
    
    try:
        user = db.query(models.User).filter(models.User.name ==username).first()
        if user is None:
            raise HTTPException(status_code = 401,detail = "User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error while fetching User {str(e)}")     

def role_required(required_roles:list[str]):
    def wrapper(user:models.User=Depends(get_current_user)):
        try:
            if user.role not in required_roles:
                raise HTTPException(status_code=403,detail="Access forbidden for your role")
            return user
        except AttributeError:
            raise HTTPException(status_code=403,detail="User object missing role attribute")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Role verification failed: {str(e)}")
    return wrapper #this line will  return the current authenticated user 

def verify_password(plain_password,hashed_password):
    try:
        if not plain_password or not hashed_password:
            raise HTTPException(status_code=401,detail="Password values can't be empty")
        return bcrypt.checkpw(plain_password.encode("utf-8"),hashed_password.encode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=401,detail=f"Invalid password input {str(e)}")
    
def get_password_hash(password):
    try:
        if not password:
            raise ValueError("Password can't be empty")
        hashed = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )    
        return hashed.decode("utf-8")
    except ValueError as ve:
        raise HTTPException(status_code=400,detail=f"Invalid password input {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Password hashing failed{str(e)}")
    
def admin_required(current_user:models.User=Depends(get_current_user)):
    try:
        if current_user.role!="admin":
            raise HTTPException(status_code=400,detail="Admin access Required")
        return current_user
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Unexpected Error {str(e)}")
        
    
    
    
    


        



