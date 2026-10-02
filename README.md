# MediFind — Medicine Availability & Verified Pharmacy Locator Platform

**MediFind** is a production-grade full-stack medicine discovery and verified pharmacy locator web application. It connects customers searching for essential medications with nearby licensed pharmacies, provides transparent inventory update timestamps, enables manual prescription verification, and orchestrates an order fulfillment state machine.

---

## 🚀 Key System Features

1. **Multi-Field Medicine Search Engine**: Search across brand names, generic chemical names, strength, dosage form, and therapeutic categories.
2. **Mandatory Inventory Timestamps**: Enforces explicit `"Last updated: <timestamp>"` disclosure for every stock record. Never assumes real-time inventory without stored store updates.
3. **Nearby Pharmacy List & Geolocation Discovery**: Browser geolocation combined with spherical Haversine distance calculation to discover and sort verified pharmacies by proximity (nearest first), displaying clean, lightweight pharmacy cards without map overhead.
4. **Licensure & Pharmacy Verification Workflow**: Pharmacy stores submit state drug license certificates (`PENDING`); platform administrators audit documents and approve (`APPROVED`) or reject with immutable audit logs.
5. **Medical Safety & Prescription System**:
   - Secure encrypted document uploads (PDF, PNG, JPG/JPEG).
   - Strict server-side MIME and magic-byte header validation.
   - **100% Manual Pharmacist Review**: Prohibits automated AI clinical diagnoses or auto-approvals.
6. **Order State Machine**:
   $$\text{PENDING} \longrightarrow \text{ACCEPTED} \longrightarrow \text{CONFIRMED} \longrightarrow \text{PREPARING} \longrightarrow \begin{matrix} \text{READY\_FOR\_PICKUP} \\ \text{OUT\_FOR\_DELIVERY} \end{matrix} \longrightarrow \text{COMPLETED}$$
   *(with strict cancellation and rejection state transitions)*.
7. **Role-Based Access Control (RBAC)**: Secure access partitions between **Customer**, **Pharmacy Store Owner**, and **Platform Administrator**.
8. **In-App Notification Center & Audit Logging**: Real-time alerts for customer order updates and compliance tracking of admin decisions.

---

## 📍 Nearby-Pharmacy Discovery & Distance Sorting Flow

MediFind employs a clean, fast **Nearby Pharmacy List System** instead of heavy frontend map tiles:

```
Search Medicine  ──►  Filter Pharmacies by Stock  ──►  Detect User Location  ──►  Calculate Haversine Distance  ──►  Sort Nearest First  ──►  View Pharmacy Profile
```

1. **Search Medicine**: Customer searches by brand or generic name (e.g. *Paracetamol*).
2. **Pharmacy Availability Filtering**: MediFind queries `PharmacyInventory` joined with verified `Pharmacy` records to identify licensed stores carrying the medicine.
3. **Browser Geolocation**: Uses the native HTML5 Geolocation API (`navigator.geolocation`) to securely retrieve user latitude and longitude with user consent, falling back gracefully if permission is denied.
4. **Haversine Distance Calculation**:
   $$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
   Computes exact surface distances ($R = 6371\text{ km}$) between the user and each store coordinate.
5. **Distance Sorting (Nearest First)**: Matching pharmacies are ordered with the nearest store first.
6. **Pharmacy Cards**: Displays store name, verified status badge, distance from user (e.g. `1.2 km away`), address, medicine stock status, price, mandatory inventory timestamp, pickup/delivery support, and opening hours.
7. **View Pharmacy**: Opens the dedicated store profile page showing comprehensive pharmacy details and full inventory without map distractions.

---

## 🏗️ Architecture & Technology Stack

```
MediFind Monolith (Modular Blueprint Architecture)
├── Backend:        Python 3.10+ / Flask / Flask-Login
├── ORM & Database: SQLAlchemy 2.0 / MySQL (Production) & SQLite (Local Fallback)
├── Migrations:     Flask-Migrate / Alembic
├── Frontend:       Jinja2 / Custom Healthcare CSS Design System / Modern Typography
├── Proximity:      Browser Geolocation API + Mathematical Haversine Distance Formula
├── Security:       Werkzeug Password Hashing, CSRF/XSS Protections, Secure File Vault
└── Testing:        pytest (100% test pass rate across 21 test suites)
```

---

## 📂 Project Structure

```
pro demo/
├── app/
│   ├── __init__.py                 # Flask App Factory & Error Handlers
│   ├── extensions.py               # db, migrate, login_manager
│   ├── models/                     # SQLAlchemy Relational Models
│   │   ├── __init__.py
│   │   ├── user.py                 # User (Customer, Pharmacy, Admin)
│   │   ├── pharmacy.py             # Pharmacy & VerificationDocument
│   │   ├── medicine.py             # Medicine & MedicineCategory
│   │   ├── inventory.py            # PharmacyInventory (Mandatory Timestamp)
│   │   ├── prescription.py         # Prescription (Manual Review Workflow)
│   │   ├── order.py                # Order & OrderItem (State Machine)
│   │   ├── request.py              # MedicineRequest
│   │   ├── notification.py         # Notification
│   │   └── audit.py                # AuditLog
│   ├── services/                   # Business Logic & Service Layer
│   │   ├── auth_service.py
│   │   ├── medicine_service.py
│   │   ├── location_service.py     # Haversine distance & nearby queries
│   │   ├── pharmacy_service.py
│   │   ├── inventory_service.py
│   │   ├── prescription_service.py
│   │   ├── order_service.py
│   │   ├── notification_service.py
│   │   └── audit_service.py
│   ├── utils/                      # Helpers & Security Validators
│   │   ├── security.py             # Role decorators & file validators
│   │   └── helpers.py              # Haversine & humanize time
│   ├── blueprints/
│   │   ├── auth/                   # /auth (Login, Register Customer, Register Store)
│   │   ├── customer/               # / (Search, Medicine details, Map, Orders, Rx)
│   │   ├── pharmacy/               # /pharmacy (Dashboard, Inventory, Rx Review)
│   │   ├── admin/                  # /admin (Licensure review, Catalog CRUD, Audits)
│   │   └── api/                    # /api (REST JSON endpoints & secure file streaming)
│   ├── templates/                  # Modern responsive Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── errors/
│   │   ├── auth/
│   │   ├── customer/
│   │   ├── pharmacy/
│   │   └── admin/
│   └── static/
│       ├── css/style.css           # Custom Healthcare CSS Design System
│       └── js/                     # Client autocomplete & geolocation sorting scripts
├── tests/                          # Pytest Unit & End-to-End Test Suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_search.py
│   ├── test_location.py
│   ├── test_inventory.py
│   ├── test_prescription.py
│   ├── test_orders.py
│   ├── test_admin.py
│   └── test_e2e.py
├── uploads/                        # Secure storage outside web root
├── seed.py                         # Realistic database seeder
├── run.py                          # Server launcher
├── config.py                       # App configuration
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
└── README.md
```

---

## 🗄️ Database Schema & Relationships

- **`users`**: Master user authentication table supporting `CUSTOMER`, `PHARMACY`, and `ADMIN` roles.
- **`pharmacies`**: 1-to-1 relationship with `User` (store owner). Stores license number, address, GPS coordinates, verification status, and pickup/delivery capabilities.
- **`verification_documents`**: 1-to-many relationship with `Pharmacy`. Contains uploaded official licenses and certificates.
- **`medicine_categories`**: Classification tags for therapeutic indications.
- **`medicines`**: Master medicine repository with generic names, brand names, dosage form, strength, and `requires_prescription` flag.
- **`pharmacy_inventory`**: Many-to-many relationship linking `Pharmacy` and `Medicine`. Tracks quantity, retail price, stock status (`AVAILABLE`, `LOW_STOCK`, `OUT_OF_STOCK`), and mandatory explicit `last_updated_at` timestamps.
- **`prescriptions`**: Belongs to `User` (Customer). Stores file metadata, medical notes, review status (`PENDING_REVIEW`, `APPROVED`, `REJECTED`), and reviewer ID.
- **`orders`**: Belongs to `User` (Customer) and `Pharmacy`. Manages delivery/pickup fulfillment, total cost, customer/pharmacy notes, and status transitions.
- **`order_items`**: Line items in an order with snapshot unit price and quantity.
- **`medicine_requests`**: Direct customer inquiries for medicine availability.
- **`notifications`**: In-app alert queue for customers and store owners.
- **`audit_logs`**: Immutable security log for admin approvals, prescription reviews, and logins.

---

## ⚙️ Quick Start & Local Setup (Windows 11 / Linux / macOS)

### 1. Clone & Setup Virtual Environment
```powershell
# In PowerShell:
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
*(By default, `DATABASE_URL=sqlite:///medifind.db` is configured for instant local testing. For MySQL, set `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` or provide a MySQL URI in `.env`)*.

### 4. Seed Database with Realistic Demo Data
```powershell
python seed.py
```

### 5. Run the Server
```powershell
python run.py
```
Open your browser at: **`http://127.0.0.1:5000`**

### 6. Run Automated Tests
```powershell
python -m pytest -v
```

---

## 🔑 Demo Login Credentials

| Role | Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@medifind.com` | `Admin@12345` | Global control, pharmacy verification queue, catalog CRUD, audit trail |
| **Verified Pharmacy 1** | `apollo@pharmacy.com` | `Pharmacy@12345` | Apollo HealthCare & Pharmacy (Verified, Pickup + Delivery) |
| **Verified Pharmacy 2** | `medplus@pharmacy.com` | `Pharmacy@12345` | MedPlus Express Pharmacy (Verified, 24 Hours) |
| **Verified Pharmacy 3** | `guardian@pharmacy.com` | `Pharmacy@12345` | Guardian Care Pharmacy (Verified, Pickup Only) |
| **Pending Pharmacy** | `wellness@pharmacy.com` | `Pharmacy@12345` | Wellness Direct Pharmacy (Pending admin approval) |
| **Customer 1** | `customer@medifind.com` | `Customer@12345` | John Doe (Has active prescription and completed order history) |
| **Customer 2** | `sarah@medifind.com` | `Customer@12345` | Sarah Jenkins (Has order in preparation) |

---

## 🛡️ Security & Medical Safety Considerations

1. **Explicit Timestamps**: Avoids false real-time claims by timestamping all stock changes.
2. **Manual Rx Review**: Prevents unauthorized dispensing of Schedule H / prescription medicines.
3. **Upload Security**: Uploaded files receive randomized UUID server filenames, undergo strict MIME/header inspection, and are stored strictly outside public web roots.
4. **Role Isolation**: RBAC decorators `@role_required` prevent horizontal and vertical privilege escalation.
5. **Audit Logging**: All admin verifications, prescription decisions, and status transitions create permanent audit records.

---

## 🔮 Future Improvements
- SMS / WhatsApp / WebPush notifications for out-for-delivery alerts.
- OCR optical text extraction assistant for pharmacist reference (while maintaining human review).
- Route optimization for pharmacy delivery riders.
