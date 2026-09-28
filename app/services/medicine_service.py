from typing import List, Optional
from sqlalchemy import or_
from app.extensions import db
from app.models.medicine import Medicine, MedicineCategory

class MedicineService:
    @staticmethod
    def search_medicines(query_str: str, category_id: Optional[int] = None, prescription_only: Optional[bool] = None, limit: int = 50) -> List[Medicine]:
        """
        Searches medicines across Name, Generic Name, and Brand Name.
        """
        query = Medicine.query

        if query_str:
            term = f"%{query_str.strip()}%"
            query = query.filter(
                or_(
                    Medicine.name.ilike(term),
                    Medicine.generic_name.ilike(term),
                    Medicine.brand_name.ilike(term),
                    Medicine.strength.ilike(term),
                    Medicine.dosage_form.ilike(term)
                )
            )

        if category_id:
            query = query.filter(Medicine.category_id == category_id)

        if prescription_only is not None:
            query = query.filter(Medicine.requires_prescription == prescription_only)

        return query.order_by(Medicine.name.asc()).limit(limit).all()

    @staticmethod
    def get_medicine_by_id(medicine_id: int) -> Optional[Medicine]:
        return db.session.get(Medicine, medicine_id)

    @staticmethod
    def get_all_categories() -> List[MedicineCategory]:
        return MedicineCategory.query.order_by(MedicineCategory.name.asc()).all()

    @staticmethod
    def create_or_update_category(name: str, slug: str, description: str = None, icon: str = 'fa-pills', category_id: int = None) -> MedicineCategory:
        if category_id:
            category = db.session.get(MedicineCategory, category_id)
        else:
            category = MedicineCategory()
        
        category.name = name.strip()
        category.slug = slug.strip().lower()
        category.description = description
        category.icon = icon
        
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def create_or_update_medicine(data: dict, medicine_id: int = None) -> Medicine:
        if medicine_id:
            medicine = db.session.get(Medicine, medicine_id)
        else:
            medicine = Medicine()

        medicine.name = data['name'].strip()
        medicine.generic_name = data['generic_name'].strip()
        medicine.brand_name = data.get('brand_name', '').strip() or None
        medicine.strength = data['strength'].strip()
        medicine.dosage_form = data.get('dosage_form', 'Tablet').strip()
        medicine.requires_prescription = bool(data.get('requires_prescription', False))
        medicine.category_id = data.get('category_id') or None
        medicine.description = data.get('description')
        medicine.manufacturer = data.get('manufacturer')
        medicine.usage_instructions = data.get('usage_instructions')
        medicine.side_effects_warning = data.get('side_effects_warning')

        db.session.add(medicine)
        db.session.commit()
        return medicine
