import os
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.pharmacy import Pharmacy, VerificationDocument
from app.models.medicine import MedicineCategory, Medicine
from app.models.inventory import PharmacyInventory
from app.models.prescription import Prescription
from app.models.order import Order, OrderItem
from app.models.request import MedicineRequest
from app.models.notification import Notification
from app.models.audit import AuditLog

def seed_database():
    app = create_app('development')
    with app.app_context():
        print("Cleaning up old database tables...")
        db.drop_all()
        db.create_all()
        print("Tables created.")

        now = datetime.utcnow()

        # -------------------------------------------------------------
        # 1. USERS & ADMIN
        # -------------------------------------------------------------
        print("Seeding Users...")
        admin = User(
            email='admin@medifind.com',
            full_name='System Administrator',
            phone='+1-800-555-0199',
            role='admin',
            is_active=True
        )
        admin.set_password('Admin@12345')
        db.session.add(admin)

        owner1 = User(
            email='apollo@pharmacy.com',
            full_name='Dr. Rajiv Sharma',
            phone='+1-555-0101',
            role='pharmacy',
            is_active=True
        )
        owner1.set_password('Pharmacy@12345')
        db.session.add(owner1)

        owner2 = User(
            email='medplus@pharmacy.com',
            full_name='Ananya Gupta',
            phone='+1-555-0102',
            role='pharmacy',
            is_active=True
        )
        owner2.set_password('Pharmacy@12345')
        db.session.add(owner2)

        owner3 = User(
            email='guardian@pharmacy.com',
            full_name='Vikram Mehta',
            phone='+1-555-0103',
            role='pharmacy',
            is_active=True
        )
        owner3.set_password('Pharmacy@12345')
        db.session.add(owner3)

        owner_pending = User(
            email='wellness@pharmacy.com',
            full_name='Dr. Priya Patel',
            phone='+1-555-0104',
            role='pharmacy',
            is_active=True
        )
        owner_pending.set_password('Pharmacy@12345')
        db.session.add(owner_pending)

        customer1 = User(
            email='customer@medifind.com',
            full_name='John Doe',
            phone='+1-555-0201',
            role='customer',
            is_active=True
        )
        customer1.set_password('Customer@12345')
        db.session.add(customer1)

        customer2 = User(
            email='sarah@medifind.com',
            full_name='Sarah Jenkins',
            phone='+1-555-0202',
            role='customer',
            is_active=True
        )
        customer2.set_password('Customer@12345')
        db.session.add(customer2)

        db.session.flush()

        # -------------------------------------------------------------
        # 2. PHARMACIES & VERIFICATION DOCUMENTS
        # -------------------------------------------------------------
        print("Seeding Pharmacies...")
        pharmacy1 = Pharmacy(
            owner_id=owner1.id,
            name='Apollo HealthCare & Pharmacy',
            license_number='DL-2024-APL-8821',
            phone='+1-555-0101',
            email='contact@apollopharmacy.example.com',
            address='14 Central Avenue, Downtown Core',
            city='Metro City',
            state='Central',
            pincode='100001',
            latitude=28.6139,
            longitude=77.2090,
            verification_status='APPROVED',
            verification_notes='Drug license verified with State Pharmacy Council.',
            verified_at=now - timedelta(days=45),
            supports_pickup=True,
            supports_delivery=True,
            delivery_fee=2.50,
            opening_hours='8:00 AM - 11:00 PM',
            is_active=True
        )
        db.session.add(pharmacy1)

        pharmacy2 = Pharmacy(
            owner_id=owner2.id,
            name='MedPlus Express Pharmacy',
            license_number='DL-2024-MDP-1044',
            phone='+1-555-0102',
            email='support@medplusexpress.example.com',
            address='82 Market Road, Green Park',
            city='Metro City',
            state='Central',
            pincode='100016',
            latitude=28.6289,
            longitude=77.2180,
            verification_status='APPROVED',
            verification_notes='Verified valid council registration & storage license.',
            verified_at=now - timedelta(days=20),
            supports_pickup=True,
            supports_delivery=True,
            delivery_fee=1.50,
            opening_hours='24 Hours Open',
            is_active=True
        )
        db.session.add(pharmacy2)

        pharmacy3 = Pharmacy(
            owner_id=owner3.id,
            name='Guardian Care Pharmacy',
            license_number='DL-2024-GDC-7732',
            phone='+1-555-0103',
            email='care@guardiancare.example.com',
            address='205 North Ridge Blvd',
            city='Metro City',
            state='Central',
            pincode='100009',
            latitude=28.6448,
            longitude=77.2167,
            verification_status='APPROVED',
            verification_notes='Verified retail drugstore certification.',
            verified_at=now - timedelta(days=10),
            supports_pickup=True,
            supports_delivery=False,
            delivery_fee=0.00,
            opening_hours='9:00 AM - 9:30 PM',
            is_active=True
        )
        db.session.add(pharmacy3)

        pharmacy_pending = Pharmacy(
            owner_id=owner_pending.id,
            name='Wellness Direct Pharmacy',
            license_number='DL-2025-WDP-9901',
            phone='+1-555-0104',
            email='help@wellnessdirect.example.com',
            address='55 West Coast Highway',
            city='Metro City',
            state='Central',
            pincode='100028',
            latitude=28.6012,
            longitude=77.1950,
            verification_status='PENDING',
            verification_notes=None,
            verified_at=None,
            supports_pickup=True,
            supports_delivery=True,
            delivery_fee=3.00,
            opening_hours='9:00 AM - 8:00 PM',
            is_active=True
        )
        db.session.add(pharmacy_pending)
        db.session.flush()

        # Add verification documents for pending pharmacy
        doc1 = VerificationDocument(
            pharmacy_id=pharmacy_pending.id,
            document_type='State Drug License Form 20B/21B',
            file_path='demo_drug_license.pdf',
            original_filename='Drug_License_2025_Wellness.pdf',
            mime_type='application/pdf',
            file_size=245800
        )
        doc2 = VerificationDocument(
            pharmacy_id=pharmacy_pending.id,
            document_type='Pharmacist Registration Certificate',
            file_path='demo_pharmacist_cert.png',
            original_filename='Pharmacist_Reg_Cert.png',
            mime_type='image/png',
            file_size=512400
        )
        db.session.add(doc1)
        db.session.add(doc2)

        # -------------------------------------------------------------
        # 3. MEDICINE CATEGORIES
        # -------------------------------------------------------------
        print("Seeding Medicine Categories...")
        cat_pain = MedicineCategory(name='Pain Relief & Anti-inflammatory', slug='pain-relief', description='Analgesics, antipyretics, and NSAIDs for pain, fever, and inflammation.', icon='fa-hand-holding-medical')
        cat_antibiotics = MedicineCategory(name='Antibiotics & Antimicrobials', slug='antibiotics', description='Prescription antibiotics for bacterial infections.', icon='fa-bacteria')
        cat_cardio = MedicineCategory(name='Cardiovascular & Blood Pressure', slug='cardiovascular', description='Medicines for heart health, hypertension, and cholesterol management.', icon='fa-heart-pulse')
        cat_resp = MedicineCategory(name='Respiratory & Allergy', slug='respiratory', description='Inhalers, antihistamines, and bronchodilators for asthma and allergic rhinitis.', icon='fa-lungs')
        cat_diabetes = MedicineCategory(name='Diabetes & Endocrine', slug='diabetes', description='Oral hypoglycemic agents and insulin care products.', icon='fa-droplet')
        cat_gastro = MedicineCategory(name='Gastrointestinal & Digestion', slug='gastrointestinal', description='Antacids, proton pump inhibitors, and anti-emetics.', icon='fa-capsules')
        cat_vitamins = MedicineCategory(name='Vitamins & Supplements', slug='vitamins', description='Dietary supplements, multivitamins, and essential minerals.', icon='fa-shield-halved')

        db.session.add_all([cat_pain, cat_antibiotics, cat_cardio, cat_resp, cat_diabetes, cat_gastro, cat_vitamins])
        db.session.flush()

        # -------------------------------------------------------------
        # 4. MEDICINES CATALOG
        # -------------------------------------------------------------
        print("Seeding Medicines Catalog...")
        meds_data = [
            # Pain Relief
            {
                'category_id': cat_pain.id,
                'name': 'Paracetamol 500mg',
                'generic_name': 'Acetaminophen / Paracetamol',
                'brand_name': 'Crocin / Calpol',
                'strength': '500mg',
                'dosage_form': 'Tablet',
                'requires_prescription': False,
                'description': 'Standard antipyretic and analgesic used to relieve mild to moderate pain and reduce fever.',
                'manufacturer': 'GSK Pharmaceuticals',
                'usage_instructions': 'Take 1 tablet every 4-6 hours as needed. Do not exceed 4000mg in 24 hours.',
                'side_effects_warning': 'Avoid alcohol. Liver toxicity may occur with overdose.'
            },
            {
                'category_id': cat_pain.id,
                'name': 'Paracetamol 650mg',
                'generic_name': 'Acetaminophen / Paracetamol',
                'brand_name': 'Dolo 650',
                'strength': '650mg',
                'dosage_form': 'Tablet',
                'requires_prescription': False,
                'description': 'High-strength paracetamol for intense fever, body ache, and viral symptoms.',
                'manufacturer': 'Micro Labs Ltd',
                'usage_instructions': 'Take 1 tablet post-meals, maximum 3 times daily or as advised.',
                'side_effects_warning': 'Consult a physician if fever persists past 3 days.'
            },
            {
                'category_id': cat_pain.id,
                'name': 'Ibuprofen 400mg',
                'generic_name': 'Ibuprofen',
                'brand_name': 'Brufen / Advil',
                'strength': '400mg',
                'dosage_form': 'Tablet',
                'requires_prescription': False,
                'description': 'Nonsteroidal anti-inflammatory drug (NSAID) used for dental pain, arthritis, and swelling.',
                'manufacturer': 'Abbott Healthcare',
                'usage_instructions': 'Take with or after food with a full glass of water.',
                'side_effects_warning': 'May cause stomach upset or heartburn in sensitive individuals.'
            },
            {
                'category_id': cat_pain.id,
                'name': 'Tramadol 50mg',
                'generic_name': 'Tramadol Hydrochloride',
                'brand_name': 'Ultram',
                'strength': '50mg',
                'dosage_form': 'Capsule',
                'requires_prescription': True,
                'description': 'Opioid analgesic for moderate to severe acute postoperative or chronic pain.',
                'manufacturer': 'Sanofi Aventis',
                'usage_instructions': 'Take strictly as prescribed by your doctor.',
                'side_effects_warning': 'May cause dizziness and dependence. Strictly prescription-only.'
            },
            # Antibiotics
            {
                'category_id': cat_antibiotics.id,
                'name': 'Amoxicillin 500mg',
                'generic_name': 'Amoxicillin Trihydrate',
                'brand_name': 'Novamox / Amoxil',
                'strength': '500mg',
                'dosage_form': 'Capsule',
                'requires_prescription': True,
                'description': 'Broad-spectrum penicillin antibiotic for ear, throat, and chest infections.',
                'manufacturer': 'Cipla Ltd',
                'usage_instructions': 'Complete the full course as prescribed, usually 1 capsule every 8 hours.',
                'side_effects_warning': 'Do not take if allergic to penicillin.'
            },
            {
                'category_id': cat_antibiotics.id,
                'name': 'Azithromycin 500mg',
                'generic_name': 'Azithromycin',
                'brand_name': 'Azithral / Zithromax',
                'strength': '500mg',
                'dosage_form': 'Tablet',
                'requires_prescription': True,
                'description': 'Macrolide antibiotic used for respiratory tract, skin, and sinus infections.',
                'manufacturer': 'Alembic Pharmaceuticals',
                'usage_instructions': 'Take once daily 1 hour before or 2 hours after a meal.',
                'side_effects_warning': 'May cause mild stomach cramping or nausea.'
            },
            {
                'category_id': cat_antibiotics.id,
                'name': 'Ciprofloxacin 500mg',
                'generic_name': 'Ciprofloxacin Hydrochloride',
                'brand_name': 'Ciplox / Cipro',
                'strength': '500mg',
                'dosage_form': 'Tablet',
                'requires_prescription': True,
                'description': 'Fluoroquinolone antibiotic for urinary tract, gastrointestinal, and bacterial infections.',
                'manufacturer': 'Cipla Ltd',
                'usage_instructions': 'Take twice daily with plenty of fluids.',
                'side_effects_warning': 'Avoid dairy products or antacids within 2 hours of ingestion.'
            },
            # Respiratory & Allergy
            {
                'category_id': cat_resp.id,
                'name': 'Cetirizine 10mg',
                'generic_name': 'Cetirizine Dihydrochloride',
                'brand_name': 'Zyrtec / Cetzine',
                'strength': '10mg',
                'dosage_form': 'Tablet',
                'requires_prescription': False,
                'description': 'Non-sedating antihistamine for hay fever, allergic skin rashes, and runny nose.',
                'manufacturer': 'Dr. Reddy’s Laboratories',
                'usage_instructions': 'Take 1 tablet once daily, preferably in the evening.',
                'side_effects_warning': 'May cause mild drowsiness in a small percentage of patients.'
            },
            {
                'category_id': cat_resp.id,
                'name': 'Montelukast 10mg',
                'generic_name': 'Montelukast Sodium',
                'brand_name': 'Singulair / Montair',
                'strength': '10mg',
                'dosage_form': 'Tablet',
                'requires_prescription': True,
                'description': 'Leukotriene receptor antagonist for maintenance treatment of asthma and seasonal allergies.',
                'manufacturer': 'Sun Pharma',
                'usage_instructions': 'Take 1 tablet daily in the evening.',
                'side_effects_warning': 'Not intended for relief of acute sudden asthma attacks.'
            },
            {
                'category_id': cat_resp.id,
                'name': 'Salbutamol Inhaler 100mcg',
                'generic_name': 'Albuterol / Salbutamol',
                'brand_name': 'Ventolin / Asthalin',
                'strength': '100mcg/dose',
                'dosage_form': 'Inhaler',
                'requires_prescription': True,
                'description': 'Short-acting beta-2 agonist bronchodilator for rapid relief of asthma bronchospasm.',
                'manufacturer': 'GlaxoSmithKline',
                'usage_instructions': 'Inhale 1 to 2 puffs when experiencing shortness of breath or before exertion.',
                'side_effects_warning': 'May cause fine tremors or palpitations momentarily.'
            },
            # Cardiovascular
            {
                'category_id': cat_cardio.id,
                'name': 'Atorvastatin 20mg',
                'generic_name': 'Atorvastatin Calcium',
                'brand_name': 'Lipitor / Atorva',
                'strength': '20mg',
                'dosage_form': 'Tablet',
                'requires_prescription': True,
                'description': 'HMG-CoA reductase inhibitor (statin) to lower LDL cholesterol and reduce cardiovascular risk.',
                'manufacturer': 'Pfizer Inc',
                'usage_instructions': 'Take once daily at nighttime with or without food.',
                'side_effects_warning': 'Report unexplained muscle pain or weakness to doctor.'
            },
            {
                'category_id': cat_cardio.id,
                'name': 'Amlodipine 5mg',
                'generic_name': 'Amlodipine Besylate',
                'brand_name': 'Norvasc / Amlong',
                'strength': '5mg',
                'dosage_form': 'Tablet',
                'requires_prescription': True,
                'description': 'Calcium channel blocker to treat high blood pressure and chronic angina.',
                'manufacturer': 'Pfizer Inc',
                'usage_instructions': 'Take once daily at the same time each morning.',
                'side_effects_warning': 'May cause ankle swelling or mild flushing.'
            },
            {
                'category_id': cat_cardio.id,
                'name': 'Telmisartan 40mg',
                'generic_name': 'Telmisartan',
                'brand_name': 'Micardis / Telma',
                'strength': '40mg',
                'dosage_form': 'Tablet',
                'requires_prescription': True,
                'description': 'Angiotensin II receptor blocker (ARB) for arterial hypertension and renal protection.',
                'manufacturer': 'Glenmark Pharmaceuticals',
                'usage_instructions': 'Take 1 tablet daily with a glass of water.',
                'side_effects_warning': 'Monitor blood pressure regularly.'
            },
            # Diabetes
            {
                'category_id': cat_diabetes.id,
                'name': 'Metformin 500mg',
                'generic_name': 'Metformin Hydrochloride',
                'brand_name': 'Glucophage / Glycomet',
                'strength': '500mg',
                'dosage_form': 'Tablet',
                'requires_prescription': True,
                'description': 'First-line biguanide oral medication for type 2 diabetes glycemic management.',
                'manufacturer': 'Merck KGaA',
                'usage_instructions': 'Take with or immediately after meals to reduce GI distress.',
                'side_effects_warning': 'Avoid excessive alcohol consumption.'
            },
            {
                'category_id': cat_diabetes.id,
                'name': 'Glimepiride 2mg',
                'generic_name': 'Glimepiride',
                'brand_name': 'Amaryl / Glimestar',
                'strength': '2mg',
                'dosage_form': 'Tablet',
                'requires_prescription': True,
                'description': 'Sulfonylurea antidiabetic agent stimulating pancreatic insulin secretion.',
                'manufacturer': 'Sanofi India',
                'usage_instructions': 'Take immediately before or during the first main meal of the day.',
                'side_effects_warning': 'Carry fast-acting glucose in case of hypoglycemia.'
            },
            # Gastrointestinal
            {
                'category_id': cat_gastro.id,
                'name': 'Pantoprazole 40mg',
                'generic_name': 'Pantoprazole Sodium',
                'brand_name': 'Protonix / Pantocid',
                'strength': '40mg',
                'dosage_form': 'Tablet',
                'requires_prescription': False,
                'description': 'Proton pump inhibitor (PPI) for GERD, acid reflux, and peptic ulcers.',
                'manufacturer': 'Sun Pharma',
                'usage_instructions': 'Take 1 tablet in the morning 30 minutes before breakfast.',
                'side_effects_warning': 'Swallow whole, do not crush or chew.'
            },
            {
                'category_id': cat_gastro.id,
                'name': 'Omeprazole 20mg',
                'generic_name': 'Omeprazole',
                'brand_name': 'Prilosec / Omez',
                'strength': '20mg',
                'dosage_form': 'Capsule',
                'requires_prescription': False,
                'description': 'Reduces gastric acid production to heal esophagus and relieve persistent heartburn.',
                'manufacturer': 'Dr. Reddy’s Laboratories',
                'usage_instructions': 'Take 1 capsule daily before meals.',
                'side_effects_warning': 'Not for immediate relief of infrequent heartburn.'
            },
            {
                'category_id': cat_gastro.id,
                'name': 'Oral Rehydration Salts (ORS)',
                'generic_name': 'Electrolytes & Glucose',
                'brand_name': 'Electral',
                'strength': '21.8g sachet',
                'dosage_form': 'Powder',
                'requires_prescription': False,
                'description': 'WHO-formula electrolyte replacement solution for dehydration caused by diarrhea or fever.',
                'manufacturer': 'FDC Ltd',
                'usage_instructions': 'Dissolve entire packet in 1 liter of clean drinking water.',
                'side_effects_warning': 'Use prepared solution within 24 hours.'
            },
            # Vitamins
            {
                'category_id': cat_vitamins.id,
                'name': 'Vitamin C 500mg Chewable',
                'generic_name': 'Ascorbic Acid',
                'brand_name': 'Limcee / Celin',
                'strength': '500mg',
                'dosage_form': 'Tablet',
                'requires_prescription': False,
                'description': 'Immunity booster and essential antioxidant assisting tissue repair and collagen synthesis.',
                'manufacturer': 'Abbott Healthcare',
                'usage_instructions': 'Chew 1 tablet daily after food.',
                'side_effects_warning': 'Excessive doses may cause mild stomach upset.'
            },
            {
                'category_id': cat_vitamins.id,
                'name': 'Vitamin D3 60000 IU',
                'generic_name': 'Cholecalciferol',
                'brand_name': 'Calcirol / D-Rise',
                'strength': '60000 IU',
                'dosage_form': 'Capsule',
                'requires_prescription': False,
                'description': 'High-potency weekly supplement for severe Vitamin D deficiency and bone mineral density.',
                'manufacturer': 'Cadila Healthcare',
                'usage_instructions': 'Take 1 capsule once weekly with milk or fat-containing meal for 8 weeks.',
                'side_effects_warning': 'Do not exceed weekly recommended dosage.'
            }
        ]

        created_medicines = []
        for m_data in meds_data:
            med = Medicine(**m_data)
            db.session.add(med)
            created_medicines.append(med)

        db.session.flush()

        # -------------------------------------------------------------
        # 5. PHARMACY INVENTORIES (WITH MANDATORY DIFFERENT TIMESTAMPS)
        # -------------------------------------------------------------
        print("Seeding Pharmacy Inventories with diverse last_updated timestamps...")
        
        # Pharmacy 1 (Apollo) Inventory
        p1_items = [
            (created_medicines[0], 50, 2.50, 'AVAILABLE', now - timedelta(minutes=10)), # Paracetamol 500mg: 10 mins ago
            (created_medicines[1], 35, 3.20, 'AVAILABLE', now - timedelta(minutes=25)), # Paracetamol 650mg: 25 mins ago
            (created_medicines[2], 8, 4.00, 'LOW_STOCK', now - timedelta(hours=1, minutes=15)), # Ibuprofen 400mg: 1h 15m ago
            (created_medicines[4], 20, 9.50, 'AVAILABLE', now - timedelta(hours=3)), # Amoxicillin: 3 hrs ago
            (created_medicines[5], 15, 12.00, 'AVAILABLE', now - timedelta(hours=5)), # Azithromycin: 5 hrs ago
            (created_medicines[7], 60, 1.80, 'AVAILABLE', now - timedelta(minutes=40)), # Cetirizine: 40 mins ago
            (created_medicines[9], 4, 18.50, 'LOW_STOCK', now - timedelta(hours=2)), # Salbutamol Inhaler: 2 hrs ago
            (created_medicines[10], 25, 14.20, 'AVAILABLE', now - timedelta(days=1)), # Atorvastatin
            (created_medicines[13], 40, 5.00, 'AVAILABLE', now - timedelta(hours=6)), # Metformin
            (created_medicines[15], 30, 4.50, 'AVAILABLE', now - timedelta(hours=4)), # Pantoprazole
            (created_medicines[18], 100, 1.20, 'AVAILABLE', now - timedelta(minutes=5)), # Vitamin C
            (created_medicines[19], 45, 6.00, 'AVAILABLE', now - timedelta(hours=1)) # Vitamin D3
        ]

        for med, qty, price, status, updated_at in p1_items:
            inv = PharmacyInventory(
                pharmacy_id=pharmacy1.id,
                medicine_id=med.id,
                quantity=qty,
                price=price,
                stock_status=status,
                last_updated_at=updated_at,
                batch_number='APL-B2026-01'
            )
            db.session.add(inv)

        # Pharmacy 2 (MedPlus) Inventory
        p2_items = [
            (created_medicines[0], 5, 2.40, 'LOW_STOCK', now - timedelta(minutes=45)), # Paracetamol 500mg: 45 mins ago (Low stock)
            (created_medicines[1], 60, 3.00, 'AVAILABLE', now - timedelta(minutes=15)), # Paracetamol 650mg: 15 mins ago
            (created_medicines[2], 25, 3.80, 'AVAILABLE', now - timedelta(hours=2)),
            (created_medicines[3], 12, 16.00, 'AVAILABLE', now - timedelta(hours=8)), # Tramadol
            (created_medicines[4], 0, 9.00, 'OUT_OF_STOCK', now - timedelta(hours=1)), # Amoxicillin: Out of stock
            (created_medicines[5], 8, 11.50, 'LOW_STOCK', now - timedelta(minutes=30)), # Azithromycin
            (created_medicines[7], 40, 1.70, 'AVAILABLE', now - timedelta(hours=4)),
            (created_medicines[8], 18, 15.00, 'AVAILABLE', now - timedelta(hours=7)), # Montelukast
            (created_medicines[9], 10, 17.50, 'LOW_STOCK', now - timedelta(minutes=50)), # Salbutamol
            (created_medicines[11], 30, 6.50, 'AVAILABLE', now - timedelta(hours=12)), # Amlodipine
            (created_medicines[13], 50, 4.80, 'AVAILABLE', now - timedelta(hours=3)),
            (created_medicines[16], 20, 3.90, 'AVAILABLE', now - timedelta(hours=2)), # Omeprazole
            (created_medicines[17], 80, 0.80, 'AVAILABLE', now - timedelta(minutes=20)) # ORS
        ]

        for med, qty, price, status, updated_at in p2_items:
            inv = PharmacyInventory(
                pharmacy_id=pharmacy2.id,
                medicine_id=med.id,
                quantity=qty,
                price=price,
                stock_status=status,
                last_updated_at=updated_at,
                batch_number='MDP-B2026-99'
            )
            db.session.add(inv)

        # Pharmacy 3 (Guardian Care) Inventory
        p3_items = [
            (created_medicines[0], 0, 2.60, 'OUT_OF_STOCK', now - timedelta(hours=1, minutes=10)), # Paracetamol 500mg: 1 hr ago (Unavailable)
            (created_medicines[1], 15, 3.40, 'AVAILABLE', now - timedelta(hours=4)),
            (created_medicines[4], 14, 9.80, 'AVAILABLE', now - timedelta(hours=9)),
            (created_medicines[6], 22, 8.50, 'AVAILABLE', now - timedelta(hours=15)), # Ciprofloxacin
            (created_medicines[7], 15, 1.90, 'AVAILABLE', now - timedelta(hours=2)),
            (created_medicines[10], 18, 14.50, 'AVAILABLE', now - timedelta(days=2)),
            (created_medicines[12], 25, 11.00, 'AVAILABLE', now - timedelta(hours=5)), # Telmisartan
            (created_medicines[14], 15, 7.20, 'AVAILABLE', now - timedelta(hours=6)), # Glimepiride
            (created_medicines[15], 10, 4.60, 'LOW_STOCK', now - timedelta(hours=3)),
            (created_medicines[18], 50, 1.30, 'AVAILABLE', now - timedelta(hours=1))
        ]

        for med, qty, price, status, updated_at in p3_items:
            inv = PharmacyInventory(
                pharmacy_id=pharmacy3.id,
                medicine_id=med.id,
                quantity=qty,
                price=price,
                stock_status=status,
                last_updated_at=updated_at,
                batch_number='GDC-B2026-44'
            )
            db.session.add(inv)

        db.session.flush()

        # -------------------------------------------------------------
        # 6. PRESCRIPTIONS & ORDERS & REQUESTS
        # -------------------------------------------------------------
        print("Seeding Prescriptions, Orders, and Requests...")
        rx1 = Prescription(
            customer_id=customer1.id,
            file_path='demo_prescription_asthma.pdf',
            original_filename='Prescription_DrSmith_Asthma.pdf',
            mime_type='application/pdf',
            file_size=184300,
            status='APPROVED',
            doctor_name='Dr. Arthur Smith, MD',
            patient_name='John Doe',
            notes='Prescribed Salbutamol 100mcg & Montelukast 10mg for bronchial spasm.',
            reviewed_by_user_id=owner1.id,
            reviewed_at=now - timedelta(days=2)
        )
        db.session.add(rx1)

        rx2 = Prescription(
            customer_id=customer2.id,
            file_path='demo_prescription_antibiotic.png',
            original_filename='Rx_Amoxicillin_500mg.png',
            mime_type='image/png',
            file_size=324000,
            status='PENDING_REVIEW',
            doctor_name='Dr. Elena Rostova',
            patient_name='Sarah Jenkins',
            notes='For acute bacterial sinus infection.'
        )
        db.session.add(rx2)
        db.session.flush()

        # Demo Order 1: Completed Pickup Order
        order1 = Order(
            order_number='ORD-20260901-A109B2',
            customer_id=customer1.id,
            pharmacy_id=pharmacy1.id,
            prescription_id=rx1.id,
            order_type='PICKUP',
            contact_phone='+1-555-0201',
            status=Order.STATUS_COMPLETED,
            total_amount=21.00,
            customer_notes='Will pick up around 5 PM.',
            pharmacy_notes='Verified prescription with doctor office. Handed to customer.',
            accepted_at=now - timedelta(days=2, hours=4),
            confirmed_at=now - timedelta(days=2, hours=3),
            preparing_at=now - timedelta(days=2, hours=2),
            ready_at=now - timedelta(days=2, hours=1),
            completed_at=now - timedelta(days=2),
            created_at=now - timedelta(days=2, hours=5)
        )
        db.session.add(order1)
        db.session.flush()

        oi1 = OrderItem(order_id=order1.id, medicine_id=created_medicines[9].id, quantity=1, unit_price=18.50, subtotal=18.50)
        oi2 = OrderItem(order_id=order1.id, medicine_id=created_medicines[0].id, quantity=1, unit_price=2.50, subtotal=2.50)
        db.session.add_all([oi1, oi2])

        # Demo Order 2: Active Preparing Delivery Order
        order2 = Order(
            order_number='ORD-20260906-8F22C1',
            customer_id=customer2.id,
            pharmacy_id=pharmacy2.id,
            prescription_id=None,
            order_type='DELIVERY',
            delivery_address='45 Maple Street, Apt 3B, Metro City, 100016',
            contact_phone='+1-555-0202',
            status=Order.STATUS_PREPARING,
            total_amount=11.00,
            customer_notes='Please ring doorbell.',
            pharmacy_notes='Order confirmed and packed. Delivery rider dispatched soon.',
            accepted_at=now - timedelta(minutes=40),
            confirmed_at=now - timedelta(minutes=30),
            preparing_at=now - timedelta(minutes=15),
            created_at=now - timedelta(minutes=55)
        )
        db.session.add(order2)
        db.session.flush()

        oi3 = OrderItem(order_id=order2.id, medicine_id=created_medicines[1].id, quantity=2, unit_price=3.00, subtotal=6.00)
        oi4 = OrderItem(order_id=order2.id, medicine_id=created_medicines[7].id, quantity=2, unit_price=1.75, subtotal=3.50)
        db.session.add_all([oi3, oi4])

        # Demo Medicine Request
        req1 = MedicineRequest(
            customer_id=customer1.id,
            pharmacy_id=pharmacy2.id,
            medicine_id=created_medicines[4].id, # Amoxicillin (currently out of stock at pharmacy2)
            quantity=2,
            status='PENDING',
            notes='Looking for Novamox 500mg. When will new shipment arrive?'
        )
        db.session.add(req1)

        # -------------------------------------------------------------
        # 7. NOTIFICATIONS & AUDIT LOGS
        # -------------------------------------------------------------
        print("Seeding Notifications & Audit Logs...")
        n1 = Notification(
            user_id=customer1.id,
            title='Order Completed',
            message='Your order #ORD-20260901-A109B2 has been marked as completed. Thank you for using MediFind!',
            type='ORDER',
            is_read=True,
            link_url=f'/orders/{order1.id}',
            created_at=now - timedelta(days=2)
        )
        n2 = Notification(
            user_id=customer2.id,
            title='Order Preparing',
            message='Your order #ORD-20260906-8F22C1 is currently being prepared by MedPlus Express Pharmacy.',
            type='ORDER',
            is_read=False,
            link_url=f'/orders/{order2.id}',
            created_at=now - timedelta(minutes=15)
        )
        n3 = Notification(
            user_id=admin.id,
            title='New Pharmacy Verification Request',
            message='Wellness Direct Pharmacy submitted license documents for approval.',
            type='VERIFICATION',
            is_read=False,
            link_url=f'/admin/pharmacies/{pharmacy_pending.id}/verify',
            created_at=now - timedelta(hours=3)
        )
        db.session.add_all([n1, n2, n3])

        # Audit logs
        a1 = AuditLog(
            actor_user_id=admin.id,
            action='PHARMACY_APPROVED',
            target_type='Pharmacy',
            target_id=pharmacy1.id,
            details=f"Admin approved '{pharmacy1.name}' after drug license verification.",
            ip_address='127.0.0.1',
            created_at=now - timedelta(days=45)
        )
        a2 = AuditLog(
            actor_user_id=owner1.id,
            action='PRESCRIPTION_APPROVED',
            target_type='Prescription',
            target_id=rx1.id,
            details=f"Dr. Rajiv Sharma manually verified prescription #{rx1.id}.",
            ip_address='127.0.0.1',
            created_at=now - timedelta(days=2)
        )
        db.session.add_all([a1, a2])

        db.session.commit()
        print("Database seeded successfully with realistic demo data!")
        print("\n================ DEMO CREDENTIALS ================")
        print("1. Admin Account:     admin@medifind.com     / Admin@12345")
        print("2. Pharmacy 1:        apollo@pharmacy.com    / Pharmacy@12345 (Verified, Delivery+Pickup)")
        print("3. Pharmacy 2:        medplus@pharmacy.com   / Pharmacy@12345 (Verified, Delivery+Pickup)")
        print("4. Pharmacy 3:        guardian@pharmacy.com  / Pharmacy@12345 (Verified, Pickup Only)")
        print("5. Pharmacy 4:        wellness@pharmacy.com  / Pharmacy@12345 (Pending Verification)")
        print("6. Customer 1:        customer@medifind.com  / Customer@12345")
        print("7. Customer 2:        sarah@medifind.com     / Customer@12345")
        print("==================================================\n")

if __name__ == '__main__':
    seed_database()
