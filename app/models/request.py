from datetime import datetime
from app.extensions import db

class MedicineRequest(db.Model):
    __tablename__ = 'medicine_requests'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id', ondelete='CASCADE'), nullable=False, index=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id', ondelete='CASCADE'), nullable=False, index=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id', ondelete='SET NULL'), nullable=True, index=True)
    
    quantity = db.Column(db.Integer, nullable=False, default=1)
    # Status: 'PENDING', 'ACCEPTED', 'REJECTED', 'FULFILLED', 'CANCELLED'
    status = db.Column(db.String(30), default='PENDING', nullable=False, index=True)
    
    notes = db.Column(db.Text, nullable=True)
    pharmacy_response = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def status_badge_class(self) -> str:
        mapping = {
            'PENDING': 'badge-warning',
            'ACCEPTED': 'badge-success',
            'REJECTED': 'badge-danger',
            'FULFILLED': 'badge-primary',
            'CANCELLED': 'badge-secondary'
        }
        return mapping.get(self.status, 'badge-secondary')

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else None,
            'pharmacy_id': self.pharmacy_id,
            'pharmacy_name': self.pharmacy.name if self.pharmacy else None,
            'medicine_id': self.medicine_id,
            'medicine_name': self.medicine.name if self.medicine else None,
            'generic_name': self.medicine.generic_name if self.medicine else None,
            'strength': self.medicine.strength if self.medicine else None,
            'quantity': self.quantity,
            'status': self.status,
            'notes': self.notes,
            'pharmacy_response': self.pharmacy_response,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<MedicineRequest #{self.id} Status:{self.status}>'
