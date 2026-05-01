#I have not tested this yet

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database

router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.post("/chat")
def chat_with_agent(user_id: int, message: str, db: Session = Depends(database.get_db)):
    # 1. Check Subscription Status
    sub = db.query(models.UserSubscription).filter(
        models.UserSubscription.user_id == user_id,
        models.UserSubscription.active == True
    ).first()

    if not sub:
        raise HTTPException(status_code=403, detail="Active subscription required to chat")

    # 2. Check Daily Limits (from your Subscription model)
    plan_details = db.query(models.Subscription).filter(models.Subscription.id == sub.subscription_id).first()
    
    # Logic: In a real app, you'd count today's messages in a 'Messages' table
    # For now, we stub the limit check
    if plan_details.daily_limit <= 0:
        raise HTTPException(status_code=429, detail="Daily message limit reached")

    return {
        "user_id": user_id,
        "agent_response": f"I received your message: '{message}'. How can I help with your home services?",
        "remaining_limit": plan_details.daily_limit - 1
    }