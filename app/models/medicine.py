from datetime import datetime
from app.extensions import db

class MedicineCategory(db.Model):
    __tablename__ = 'medicine_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default='fa-pills')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    medicines = db.relationship('Medicine', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'medicine_count': self.medicines.count()
        }

    def __repr__(self):
        return f'<MedicineCategory {self.name}>'


class Medicine(db.Model):
    __tablename__ = 'medicines'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('medicine_categories.id', ondelete='SET NULL'), nullable=True, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    generic_name = db.Column(db.String(150), nullable=False, index=True)
    brand_name = db.Column(db.String(150), nullable=True, index=True)
    strength = db.Column(db.String(50), nullable=False) # e.g. "500mg", "10mg/5ml", "250mcg"
    dosage_form = db.Column(db.String(50), nullable=False, index=True) # Tablet, Capsule, Syrup, Injection, Ointment, Drops
    requires_prescription = db.Column(db.Boolean, default=False, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    manufacturer = db.Column(db.String(150), nullable=True)
    usage_instructions = db.Column(db.Text, nullable=True)
    side_effects_warning = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    inventory_records = db.relationship('PharmacyInventory', backref='medicine', lazy='dynamic', cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='medicine', lazy='dynamic')
    medicine_requests = db.relationship('MedicineRequest', backref='medicine', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'name': self.name,
            'generic_name': self.generic_name,
            'brand_name': self.brand_name,
            'strength': self.strength,
            'dosage_form': self.dosage_form,
            'requires_prescription': self.requires_prescription,
            'description': self.description,
            'manufacturer': self.manufacturer,
            'usage_instructions': self.usage_instructions,
            'side_effects_warning': self.side_effects_warning,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Medicine {self.name} ({self.strength})>'
