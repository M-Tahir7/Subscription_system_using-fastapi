from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import models, schemas, database
from typing import List
import logging

# Set up logging to catch errors in your terminal/Docker logs
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

# --- PLAN MANAGEMENT (Admin level) ---

@router.post("/plans", response_model=schemas.SubscriptionOut)
def create_subscription_plan(plan: schemas.SubscriptionOut, db: Session = Depends(database.get_db)):
    try:
        new_plan = models.Subscription(**plan.dict(exclude={'id'}))
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
        return new_plan
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to create subscription plan"
        )

@router.get("/plans", response_model=List[schemas.SubscriptionOut])
def get_all_plans(db: Session = Depends(database.get_db)):
    try:
        return db.query(models.Subscription).all()
    except Exception as e:
        logger.error(f"Error fetching plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Could not retrieve plans"
        )

# --- USER SUBSCRIPTIONS ---

@router.post("/subscribe/{user_id}/{plan_id}", response_model=schemas.UserSubscriptionOut)
def subscribe_user(user_id: int, plan_id: int, db: Session = Depends(database.get_db)):
    try:
        # 1. Verify Plan
        plan = db.query(models.Subscription).filter(models.Subscription.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Selected plan does not exist")

        # 2. Handle Existing Subscriptions
        existing_sub = db.query(models.UserSubscription).filter(
            models.UserSubscription.user_id == user_id, 
            models.UserSubscription.active == True
        ).first()
        
        if existing_sub:
            existing_sub.active = False 

        # 3. Logic for Expiry
        days = 365 if plan.renewal_type.lower() == "yearly" else 30
        expiry = datetime.now() + timedelta(days=days)

        # 4. Create New Entry
        user_sub = models.UserSubscription(
            user_id=user_id,
            subscription_id=plan.id,
            expiry_date=expiry,
            active=True,
            docs_uploaded=0
        )

        db.add(user_sub)
        db.commit()
        db.refresh(user_sub)
        return user_sub

    except HTTPException as http_ex:
        # Re-raise known HTTP exceptions (like 404) so they aren't caught by the general Exception
        raise http_ex
    except Exception as e:
        db.rollback()
        logger.error(f"Subscription Error for User {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An error occurred while processing the subscription"
        )

@router.get("/my-status/{user_id}", response_model=schemas.UserSubscriptionOut)
def get_user_subscription_status(user_id: int, db: Session = Depends(database.get_db)):
    try:
        sub = db.query(models.UserSubscription).filter(
            models.UserSubscription.user_id == user_id,
            models.UserSubscription.active == True
        ).first()

        if not sub:
            raise HTTPException(status_code=404, detail="No active subscription found for this user")

        # Logic for auto-expiring old records
        if sub.expiry_date < datetime.now():
            sub.active = False
            db.commit()
            raise HTTPException(status_code=403, detail="Your subscription has expired. Please renew.")

        return sub

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"Status Check Error for User {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal server error checking subscription status"
        )