from sqlalchemy import Column, Integer, String, ForeignKey,TIMESTAMP,func,Boolean
from sqlalchemy.orm import relationship,declarative_base

Base = declarative_base()



class company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True, nullable=False)
    password = Column(String(255),nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now(), nullable=True)

    #func.now generates the current timestamp
    
class  User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False)
    role = Column(String(20), nullable=False) 
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now(), nullable=True)
    password = Column(String(255),nullable=False)

    
class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), nullable=False)
    price = Column(Integer, nullable=False)
    doc_limit = Column(Integer, nullable=False)
    daily_limit = Column(Integer, nullable=False)
    renewal_type = Column(String(20), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now(), nullable=True)

    
class UserSubscription(Base):
    __tablename__ = 'user_subscriptions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id', ondelete="CASCADE"))    
    start_date = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    expiry_date = Column(TIMESTAMP(timezone=True), nullable=False)
    docs_uploaded = Column(Integer, default=0)
    active = Column(Boolean, default=True)  #user currently is active or not
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now(), nullable=True)

    
#class Payment(Base):
#    __tablename__ = 'payments'
#    id = Column(Integer, primary_key=True, index=True)
#    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)    
#    subscription_id = Column(Integer, ForeignKey('subscriptions.id', ondelete="CASCADE"))

class Conversion(Base):
    __tablename__ = 'conversions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    pdf_name = Column(String(100), nullable=False)
    pages_converted = Column(Integer,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())