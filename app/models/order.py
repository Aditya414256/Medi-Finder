import uuid
from datetime import datetime
from app.extensions import db

class Order(db.Model):
    __tablename__ = 'orders'

    # State Machine Constants
    STATUS_PENDING = 'PENDING'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_PREPARING = 'PREPARING'
    STATUS_READY_FOR_PICKUP = 'READY_FOR_PICKUP'
    STATUS_OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CANCELLED = 'CANCELLED'

    VALID_TRANSITIONS = {
        STATUS_PENDING: [STATUS_ACCEPTED, STATUS_REJECTED, STATUS_CANCELLED],
        STATUS_ACCEPTED: [STATUS_CONFIRMED, STATUS_CANCELLED],
        STATUS_CONFIRMED: [STATUS_PREPARING, STATUS_CANCELLED],
        STATUS_PREPARING: [STATUS_READY_FOR_PICKUP, STATUS_OUT_FOR_DELIVERY, STATUS_CANCELLED],
        STATUS_READY_FOR_PICKUP: [STATUS_COMPLETED, STATUS_CANCELLED],
        STATUS_OUT_FOR_DELIVERY: [STATUS_COMPLETED, STATUS_CANCELLED],
        STATUS_COMPLETED: [],
        STATUS_REJECTED: [],
        STATUS_CANCELLED: []
    }

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(32), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id', ondelete='CASCADE'), nullable=False, index=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id', ondelete='SET NULL'), nullable=True, index=True)
    
    # 'PICKUP' or 'DELIVERY'
    order_type = db.Column(db.String(20), default='PICKUP', nullable=False)
    delivery_address = db.Column(db.String(255), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=False)
    
    # Status
    status = db.Column(db.String(30), default=STATUS_PENDING, nullable=False, index=True)
    total_amount = db.Column(db.Float, default=0.0, nullable=False)
    
    customer_notes = db.Column(db.Text, nullable=True)
    pharmacy_notes = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # State change timestamps
    accepted_at = db.Column(db.DateTime, nullable=True)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    preparing_at = db.Column(db.DateTime, nullable=True)
    ready_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')

    @staticmethod
    def generate_order_number() -> str:
        date_str = datetime.utcnow().strftime('%Y%m%d')
        unique_suffix = uuid.uuid4().hex[:6].upper()
        return f"ORD-{date_str}-{unique_suffix}"

    def can_transition_to(self, new_status: str) -> bool:
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])

    def transition_to(self, new_status: str, notes: str = None, reason: str = None) -> bool:
        if not self.can_transition_to(new_status):
            return False
        
        now = datetime.utcnow()
        self.status = new_status
        if notes:
            self.pharmacy_notes = notes
        if reason:
            self.rejection_reason = reason

        if new_status == self.STATUS_ACCEPTED:
            self.accepted_at = now
        elif new_status == self.STATUS_CONFIRMED:
            self.confirmed_at = now
        elif new_status == self.STATUS_PREPARING:
            self.preparing_at = now
        elif new_status in (self.STATUS_READY_FOR_PICKUP, self.STATUS_OUT_FOR_DELIVERY):
            self.ready_at = now
        elif new_status == self.STATUS_COMPLETED:
            self.completed_at = now
        elif new_status in (self.STATUS_CANCELLED, self.STATUS_REJECTED):
            self.cancelled_at = now

        return True

    @property
    def status_badge_class(self) -> str:
        mapping = {
            self.STATUS_PENDING: 'badge-warning',
            self.STATUS_ACCEPTED: 'badge-info',
            self.STATUS_CONFIRMED: 'badge-primary',
            self.STATUS_PREPARING: 'badge-primary',
            self.STATUS_READY_FOR_PICKUP: 'badge-success',
            self.STATUS_OUT_FOR_DELIVERY: 'badge-success',
            self.STATUS_COMPLETED: 'badge-success',
            self.STATUS_REJECTED: 'badge-danger',
            self.STATUS_CANCELLED: 'badge-secondary'
        }
        return mapping.get(self.status, 'badge-secondary')

    def to_dict(self, include_items=True):
        data = {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else None,
            'pharmacy_id': self.pharmacy_id,
            'pharmacy_name': self.pharmacy.name if self.pharmacy else None,
            'prescription_id': self.prescription_id,
            'order_type': self.order_type,
            'delivery_address': self.delivery_address,
            'contact_phone': self.contact_phone,
            'status': self.status,
            'total_amount': self.total_amount,
            'customer_notes': self.customer_notes,
            'pharmacy_notes': self.pharmacy_notes,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        return data

    def __repr__(self):
        return f'<Order {self.order_number} ({self.status})>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id', ondelete='RESTRICT'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)

    def to_dict(self):
        return {
            'id': self.id,
            'medicine_id': self.medicine_id,
            'medicine_name': self.medicine.name if self.medicine else None,
            'generic_name': self.medicine.generic_name if self.medicine else None,
            'strength': self.medicine.strength if self.medicine else None,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'subtotal': self.subtotal
        }

    def __repr__(self):
        return f'<OrderItem Order:{self.order_id} Medicine:{self.medicine_id} Qty:{self.quantity}>'
