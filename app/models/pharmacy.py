from datetime import datetime
from app.extensions import db

class Pharmacy(db.Model):
    __tablename__ = 'pharmacies'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    license_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    
    # Location fields
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False, default=0.0)
    longitude = db.Column(db.Float, nullable=False, default=0.0)

    # Verification status: 'PENDING', 'APPROVED', 'REJECTED'
    verification_status = db.Column(db.String(20), default='PENDING', nullable=False, index=True)
    verification_notes = db.Column(db.Text, nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)

    # Services
    supports_pickup = db.Column(db.Boolean, default=True, nullable=False)
    supports_delivery = db.Column(db.Boolean, default=False, nullable=False)
    delivery_fee = db.Column(db.Float, default=0.0, nullable=False)
    opening_hours = db.Column(db.String(100), default='9:00 AM - 9:00 PM')
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    inventory_items = db.relationship('PharmacyInventory', backref='pharmacy', lazy='dynamic', cascade='all, delete-orphan')
    verification_documents = db.relationship('VerificationDocument', backref='pharmacy', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='pharmacy', lazy='dynamic')
    medicine_requests = db.relationship('MedicineRequest', backref='pharmacy', lazy='dynamic')

    @property
    def is_verified(self) -> bool:
        return self.verification_status == 'APPROVED'

    def to_dict(self, include_owner=False):
        data = {
            'id': self.id,
            'owner_id': self.owner_id,
            'name': self.name,
            'license_number': self.license_number,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'verification_status': self.verification_status,
            'is_verified': self.is_verified,
            'supports_pickup': self.supports_pickup,
            'supports_delivery': self.supports_delivery,
            'delivery_fee': self.delivery_fee,
            'opening_hours': self.opening_hours,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_owner and self.owner:
            data['owner_name'] = self.owner.full_name
        return data

    def __repr__(self):
        return f'<Pharmacy {self.name} ({self.verification_status})>'


class VerificationDocument(db.Model):
    __tablename__ = 'verification_documents'

    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id', ondelete='CASCADE'), nullable=False, index=True)
    document_type = db.Column(db.String(100), nullable=False) # 'Drug License', 'Registration Certificate', 'Govt ID'
    file_path = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False) # bytes
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'pharmacy_id': self.pharmacy_id,
            'document_type': self.document_type,
            'original_filename': self.original_filename,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

    def __repr__(self):
        return f'<VerificationDocument {self.document_type} for Pharmacy #{self.pharmacy_id}>'
