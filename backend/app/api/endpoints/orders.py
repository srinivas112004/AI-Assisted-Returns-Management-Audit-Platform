from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.entities import Order, OrderLine, Customer, Product

router = APIRouter()

@router.get("")
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    customer_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Order)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(Order.order_id.ilike(search_filter))
    if status:
        query = query.filter(Order.status == status)
    if customer_id:
        cust = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if cust:
            query = query.filter(Order.customer_id == cust.id)

    total = query.count()
    items = query.order_by(Order.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [
            {
                "id": o.id,
                "order_id": o.order_id,
                "customer_id": o.customer.customer_id if o.customer else None,
                "customer_name": f"{o.customer.first_name} {o.customer.last_name}" if o.customer else None,
                "order_date": o.order_date.isoformat(),
                "delivery_date": o.delivery_date.isoformat() if o.delivery_date else None,
                "status": o.status,
                "subtotal": float(o.subtotal),
                "discount_amount": float(o.discount_amount),
                "tax_amount": float(o.tax_amount),
                "shipping_amount": float(o.shipping_amount),
                "total_amount": float(o.total_amount),
                "payment_method": o.payment_method,
                "lines_count": len(o.lines),
                "returns_count": len(o.return_requests)
            }
            for c in [o] for o in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 1
    }

@router.get("/{order_id}")
def get_order_details(order_id: str, db: Session = Depends(get_db)):
    if order_id.isdigit():
        order = db.query(Order).filter(Order.id == int(order_id)).first()
    else:
        order = db.query(Order).filter(Order.order_id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    lines_data = []
    for ol in order.lines:
        p = ol.product
        lines_data.append({
            "id": ol.id,
            "line_number": ol.line_number,
            "product_id": p.id if p else None,
            "sku": p.sku if p else None,
            "product_name": p.name if p else None,
            "category": p.category if p else None,
            "quantity": ol.quantity,
            "unit_price": float(ol.unit_price),
            "line_subtotal": float(ol.line_subtotal),
            "allocated_discount": float(ol.allocated_discount),
            "line_tax": float(ol.line_tax),
            "total_line_amount": float(ol.total_line_amount),
            "returned_quantity": ol.returned_quantity,
            "available_quantity": ol.quantity - ol.returned_quantity,
            "is_returnable": p.is_returnable if p else False,
            "return_window_days": p.default_return_window_days if p else 30
        })

    return {
        "id": order.id,
        "order_id": order.order_id,
        "customer": {
            "customer_id": order.customer.customer_id,
            "name": f"{order.customer.first_name} {order.customer.last_name}",
            "email": order.customer.email,
            "phone": order.customer.phone,
            "segment": order.customer.segment
        } if order.customer else None,
        "order_date": order.order_date.isoformat(),
        "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None,
        "status": order.status,
        "subtotal": float(order.subtotal),
        "discount_amount": float(order.discount_amount),
        "tax_amount": float(order.tax_amount),
        "shipping_amount": float(order.shipping_amount),
        "total_amount": float(order.total_amount),
        "payment_method": order.payment_method,
        "shipping_address": order.shipping_address,
        "lines": lines_data,
        "return_requests": [
            {
                "id": r.id,
                "rma_number": r.rma_number,
                "status": r.status,
                "overall_eligibility": r.overall_eligibility,
                "requested_date": r.requested_date.isoformat()
            }
            for r in order.return_requests
        ]
    }
