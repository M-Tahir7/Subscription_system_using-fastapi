#I have not tested this yet


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/checkout/{user_id}/{plan_id}")
def create_checkout_session(user_id: int, plan_id: int, db: Session = Depends(database.get_db)):
    try:
        # Mocking a payment success
        # In a real app, this is where you'd redirect to Stripe/PayPal
        plan = db.query(models.Subscription).filter(models.Subscription.id == plan_id).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")

        return {
            "status": "success",
            "message": f"Payment session created for {plan.name}",
            "checkout_url": "https://stripe.com/mock-checkout"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Payment gateway unreachable")