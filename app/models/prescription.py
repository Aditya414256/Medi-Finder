from datetime import datetime
from app.extensions import db

class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    file_path = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False) # In bytes
    
    # Status: 'PENDING_REVIEW', 'APPROVED', 'REJECTED'
    status = db.Column(db.String(30), default='PENDING_REVIEW', nullable=False, index=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Patient metadata entered by customer
    patient_name = db.Column(db.String(120), nullable=True)
    doctor_name = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Reviewer tracking (strictly manual review by staff/admin)
    reviewed_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    reviewer = db.relationship('User', foreign_keys=[reviewed_by_user_id], backref='reviewed_prescriptions')
    orders = db.relationship('Order', backref='prescription', lazy='dynamic')
    medicine_requests = db.relationship('MedicineRequest', backref='prescription', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name if self.customer else None,
            'original_filename': self.original_filename,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'status': self.status,
            'rejection_reason': self.rejection_reason,
            'patient_name': self.patient_name,
            'doctor_name': self.doctor_name,
            'notes': self.notes,
            'reviewed_by_name': self.reviewer.full_name if self.reviewer else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Prescription #{self.id} Customer:{self.customer_id} Status:{self.status}>'
