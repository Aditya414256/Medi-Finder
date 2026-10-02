from datetime import datetime
from app.extensions import db

class PharmacyInventory(db.Model):
    __tablename__ = 'pharmacy_inventory'
    __table_args__ = (
        db.UniqueConstraint('pharmacy_id', 'medicine_id', name='uq_pharmacy_medicine'),
    )

    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id', ondelete='CASCADE'), nullable=False, index=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id', ondelete='CASCADE'), nullable=False, index=True)
    
    quantity = db.Column(db.Integer, default=0, nullable=False)
    price = db.Column(db.Float, default=0.0, nullable=False)
    
    # Stock status: 'AVAILABLE', 'LOW_STOCK', 'OUT_OF_STOCK', 'UNKNOWN'
    stock_status = db.Column(db.String(20), default='AVAILABLE', nullable=False, index=True)
    
    # Mandatory last_updated_at explicit timestamp
    last_updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    batch_number = db.Column(db.String(50), nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def update_stock(self, quantity: int, price: float = None, notes: str = None, batch_number: str = None, expiry_date = None) -> None:
        """Update stock quantity, recalculate status, and explicitly touch last_updated_at."""
        self.quantity = max(0, quantity)
        if price is not None:
            self.price = max(0.0, price)
        if notes is not None:
            self.notes = notes
        if batch_number is not None:
            self.batch_number = batch_number
        if expiry_date is not None:
            self.expiry_date = expiry_date

        if self.quantity == 0:
            self.stock_status = 'OUT_OF_STOCK'
        elif self.quantity <= 10:
            self.stock_status = 'LOW_STOCK'
        else:
            self.stock_status = 'AVAILABLE'

        self.last_updated_at = datetime.utcnow()

    @property
    def status_badge_class(self) -> str:
        mapping = {
            'AVAILABLE': 'badge-success',
            'LOW_STOCK': 'badge-warning',
            'OUT_OF_STOCK': 'badge-danger',
            'UNKNOWN': 'badge-secondary'
        }
        return mapping.get(self.stock_status, 'badge-secondary')

    def to_dict(self):
        return {
            'id': self.id,
            'pharmacy_id': self.pharmacy_id,
            'medicine_id': self.medicine_id,
            'medicine_name': self.medicine.name if self.medicine else None,
            'generic_name': self.medicine.generic_name if self.medicine else None,
            'strength': self.medicine.strength if self.medicine else None,
            'dosage_form': self.medicine.dosage_form if self.medicine else None,
            'quantity': self.quantity,
            'price': self.price,
            'stock_status': self.stock_status,
            'last_updated_at': self.last_updated_at.isoformat() if self.last_updated_at else None,
            'batch_number': self.batch_number,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'notes': self.notes
        }

    def __repr__(self):
        return f'<PharmacyInventory Pharmacy:{self.pharmacy_id} Medicine:{self.medicine_id} Status:{self.stock_status} Updated:{self.last_updated_at}>'
