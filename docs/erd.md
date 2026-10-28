# Entity-Relationship Diagram (ERD)

The following Mermaid diagram visualizes all core entities, foreign key relationships, and cardinalities:

```mermaid
erDiagram
    Customer ||--o{ Order : places
    Customer ||--o{ ReturnRequest : submits
    
    Order ||--|{ OrderLine : contains
    Order ||--o{ ReturnRequest : referenced_by
    
    Product ||--o{ OrderLine : catalog_item
    Product ||--o{ ReturnLine : product_ref
    Product ||--o{ InventoryMovement : movement_ref
    
    ReturnPolicy ||--o{ ReturnLine : governs
    
    ReturnRequest ||--|{ ReturnLine : includes
    ReturnRequest ||--o| ReturnAuthorization : issues
    ReturnRequest ||--o{ ReturnShipment : transports
    ReturnRequest ||--o{ Refund : settles
    ReturnRequest ||--o{ RefundAttempt : tracks
    
    OrderLine ||--o{ ReturnLine : line_returned
    
    ReturnAuthorization ||--o{ ReturnShipment : authorizes
    
    ReturnShipment ||--o{ Inspection : inspected_at_dock
    
    ReturnLine ||--o{ Inspection : receives
    ReturnLine ||--o{ Refund : paid_for
    ReturnLine ||--o{ InventoryDisposition : routed_to
    
    Inspection ||--o{ InventoryDisposition : recommends
    
    InventoryDisposition ||--o{ InventoryMovement : triggers

    Customer {
        int id PK
        string customer_id UK
        string email UK
        string segment
        float risk_score
    }

    Product {
        int id PK
        string sku UK
        string category
        decimal price
        boolean is_returnable
        int default_return_window_days
    }

    Order {
        int id PK
        string order_id UK
        int customer_id FK
        datetime order_date
        datetime delivery_date
        decimal total_amount
        string status
    }

    OrderLine {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal unit_price
        decimal total_line_amount
        int returned_quantity
    }

    ReturnRequest {
        int id PK
        string rma_number UK
        int order_id FK
        int customer_id FK
        string status
        string overall_eligibility
        datetime requested_date
    }

    ReturnLine {
        int id PK
        string return_line_id UK
        int return_request_id FK
        int order_line_id FK
        int product_id FK
        int requested_quantity
        int eligible_quantity
        int approved_quantity
        string eligibility_status
        decimal estimated_refund_amount
        decimal actual_refund_amount
        string disposition_status
    }

    ReturnAuthorization {
        int id PK
        string authorization_number UK
        int return_request_id FK
        datetime authorized_date
        int authorized_quantity
        datetime valid_until
        string status
    }

    ReturnShipment {
        int id PK
        string shipment_id UK
        int return_request_id FK
        string carrier
        string tracking_number
        string status
        datetime received_date
    }

    Inspection {
        int id PK
        string inspection_id UK
        int return_shipment_id FK
        int return_line_id FK
        string item_condition
        string packaging_condition
        string result
        string recommended_disposition
    }

    Refund {
        int id PK
        string refund_id UK
        int return_request_id FK
        int return_line_id FK
        string idempotency_key UK
        decimal net_refund_amount
        string status
    }

    InventoryDisposition {
        int id PK
        string disposition_id UK
        int return_line_id FK
        int inspection_id FK
        string disposition_type
        int quantity
        string warehouse_location
        string status
    }

    InventoryMovement {
        int id PK
        string movement_id UK
        int product_id FK
        int inventory_disposition_id FK
        string movement_type
        int quantity
        string from_location
        string to_location
    }

    ReturnEvent {
        int id PK
        string event_id UK
        string entity_type
        string entity_id
        string event_type
        string actor
        datetime timestamp
    }

    AnomalyRecord {
        int id PK
        string anomaly_id UK
        string issue_type
        string affected_entity
        string affected_business_id
        string severity
        boolean detected
    }
```

---

## Cardinalities & Relational Constraints

1. **Customer 1:N Order**: A customer may place multiple orders; an order belongs to exactly one customer.
2. **Order 1:N OrderLine**: An order contains one or more line items (`cascade="all, delete-orphan"`).
3. **Order 1:N ReturnRequest**: A customer may initiate multiple return requests for an order (e.g. for different items or dates).
4. **ReturnRequest 1:N ReturnLine**: An RMA encompasses one or more return lines.
5. **ReturnRequest 0:1 ReturnAuthorization**: Exactly one authorization token per RMA (`unique=True, index=True`).
6. **ReturnAuthorization 1:N ReturnShipment**: An authorization may involve multiple shipments if split reverse logistics are required.
7. **ReturnShipment 1:N Inspection**: Physical items in a shipment are inspected individually.
8. **ReturnLine 1:N Refund**: Supports multiple refund installments or single complete payout.
9. **ReturnLine 0:N InventoryDisposition**: Supports split dispositions when inspected units have different physical conditions (e.g., 1 unit restocked, 1 unit scrapped).
10. **InventoryDisposition 1:N InventoryMovement**: Every inventory disposition generates auditable physical stock ledger movements.
