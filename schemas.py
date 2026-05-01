from pydantic import BaseModel,Field,constr
from typing import Optional
from datetime import datetime
#this schemas .py defines pydantic models for data validation 
# so we can't expose sensitive db information
#i.e when we send a request to create a company your input must look like this name and password because i have 
# define the created company endpoint like this 
class UserCreate(BaseModel):
    name:str
    password:str
    role:str

class UserOut(BaseModel):
    id:int
    name:str
    role:str
    created_at:datetime
    
    class Config:
        from_attributes = True
        #orm_mode = True means that the pydantic model can work with ORM objects directly means query results from sqlalchemy

class LoginRequest(BaseModel):
    name:str
    password:str

class TokenResponse(BaseModel):
    access_token:str
    token_type:str

#Subscription
class SubscriptionOut(BaseModel):
    id:int 
    name:str
    price:int
    doc_limit:int
    daily_limit:int
    renewal_type:str
    
    class Config:
        from_attributes = True

#User Subscription

class UserSubscriptionOut(BaseModel):
    id:int
    user_id:int
    subscription_id:int
    start_date:datetime
    expiry_date:datetime
    active:bool
    
    class Config:
        from_attributes = True
        
        
class Userupdate(BaseModel):
    name:Optional[str] = Field(None,min_length=4,max_length=50)
    password:Optional[str] = Field(None,min_length=4)
    
    
class AllUsers(BaseModel):
    id:int
    name:str
    role:str
    subscribed:bool
    
    class config:
        from_attributes = True

            

class ConversionOut(BaseModel):
    id:int
    pdf_name:str
    pages_converted:int
    created_at:datetime
    
    class Config:
        from_attributes = True                   
        
        
        
        
        
        