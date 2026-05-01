from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import models, schemas
import logging

logger = logging.getLogger(__name__)

# --- USER OPERATIONS ---
def get_user_by_name(db: Session, name: str):
    return db.query(models.User).filter(models.User.name == name).first()

# --- SUBSCRIPTION PLAN OPERATIONS (Admin) ---
def create_subscription_plan(db: Session, plan: schemas.SubscriptionOut):
    try:
        db_plan = models.Subscription(**plan.dict(exclude={'id'}))
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return db_plan
    except Exception as e:
        db.rollback()
        logger.error(f"CRUD Error (create_plan): {e}")
        raise e

# --- USER SUBSCRIPTION LOGIC ---
def get_active_user_subscription(db: Session, user_id: int):
    """Retrieves the current active subscription for a user."""
    return db.query(models.UserSubscription).filter(
        models.UserSubscription.user_id == user_id,
        models.UserSubscription.active == True
    ).first()

def create_user_subscription(db: Session, user_id: int, plan_id: int):
    """Deactivates old plans and creates a new one based on the chosen Subscription plan."""
    try:
        # 1. Fetch Plan Details
        plan = db.query(models.Subscription).filter(models.Subscription.id == plan_id).first()
        if not plan:
            return None

        # 2. Deactivate any currently active subscriptions
        db.query(models.UserSubscription).filter(
            models.UserSubscription.user_id == user_id,
            models.UserSubscription.active == True
        ).update({"active": False})

        # 3. Calculate Expiry
        days = 365 if plan.renewal_type.lower() == "yearly" else 30
        expiry = datetime.now() + timedelta(days=days)

        # 4. Create new record
        new_sub = models.UserSubscription(
            user_id=user_id,
            subscription_id=plan.id,
            expiry_date=expiry,
            active=True,
            docs_uploaded=0
        )
        
        db.add(new_sub)
        db.commit()
        db.refresh(new_sub)
        return new_sub
    except Exception as e:
        db.rollback()
        logger.error(f"CRUD Error (create_user_sub): {e}")
        raise e

# --- USAGE TRACKING (For your RAG Agent) ---
def update_doc_count(db: Session, user_id: int):
    """Increments the uploaded document count when a user converts a PDF."""
    sub = get_active_user_subscription(db, user_id)
    if sub:
        sub.docs_uploaded += 1
        db.commit()
        db.refresh(sub)
    return sub

def log_conversion(db: Session, user_id: int, pdf_name: str, pages: int):
    """Records a conversion event in the history table."""
    try:
        new_conv = models.Conversion(
            user_id=user_id,
            pdf_name=pdf_name,
            pages_converted=pages
        )
        db.add(new_conv)
        db.commit()
        return new_conv
    except Exception as e:
        db.rollback()
        return None