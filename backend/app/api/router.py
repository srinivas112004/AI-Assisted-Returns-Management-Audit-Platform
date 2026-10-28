from fastapi import APIRouter
from app.api.endpoints import (
    dashboard, customers, orders, returns, shipments,
    inspections, refunds, dispositions, exceptions,
    audit, analytics, validation, exports, admin, data_dictionary
)

api_router = APIRouter()

api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(returns.router, prefix="/returns", tags=["Returns"])
api_router.include_router(shipments.router, prefix="/shipments", tags=["Shipments"])
api_router.include_router(inspections.router, prefix="/inspections", tags=["Inspections"])
api_router.include_router(refunds.router, prefix="/refunds", tags=["Refunds"])
api_router.include_router(dispositions.router, prefix="/dispositions", tags=["Inventory Dispositions"])
api_router.include_router(exceptions.router, prefix="/exceptions", tags=["Exceptions"])
api_router.include_router(audit.router, prefix="/audit-events", tags=["Audit Trail"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Evaluation"])
api_router.include_router(validation.router, prefix="/validation", tags=["Data Validation"])
api_router.include_router(exports.router, prefix="/exports", tags=["Data Exports"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administration"])
api_router.include_router(data_dictionary.router, prefix="/data-dictionary", tags=["Data Dictionary"])
