from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Order, Product, User
from app.schemas import OrderCreate, OrderResponse, OrderUpdate

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=List[OrderResponse])
def get_orders(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return db.query(Order).filter(Order.user_id == current_user.id).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(
        Order.id == order_id, Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < order.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    total_price = product.price * order.quantity
    product.stock -= order.quantity
    db_order = Order(
        user_id=current_user.id,
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=total_price,
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_order = db.query(Order).filter(
        Order.id == order_id, Order.user_id == current_user.id
    ).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db_order.status = order.status
    db.commit()
    db.refresh(db_order)
    return db_order


@router.delete("/{order_id}", status_code=204)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(
        Order.id == order_id, Order.user_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
