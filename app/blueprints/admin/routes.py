from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models.user import User
from app.models.pharmacy import Pharmacy, VerificationDocument
from app.models.medicine import Medicine, MedicineCategory
from app.models.order import Order
from app.models.request import MedicineRequest
from app.models.audit import AuditLog
from app.services.pharmacy_service import PharmacyService
from app.services.medicine_service import MedicineService
from app.services.audit_service import AuditService
from app.utils.security import role_required
from app.extensions import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@role_required('admin')
def check_admin_access():
    pass


@admin_bp.route('/')
def dashboard():
    customer_count = User.query.filter_by(role='customer').count()
    pharmacy_owners_count = User.query.filter_by(role='pharmacy').count()
    total_pharmacies = Pharmacy.query.count()
    pending_verifications = Pharmacy.query.filter_by(verification_status='PENDING').count()
    verified_pharmacies = Pharmacy.query.filter_by(verification_status='APPROVED').count()
    total_medicines = Medicine.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status=Order.STATUS_PENDING).count()
    total_requests = MedicineRequest.query.count()

    pending_pharmacies_list = Pharmacy.query.filter_by(verification_status='PENDING').order_by(Pharmacy.created_at.asc()).limit(5).all()
    recent_orders_list = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    recent_audit_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(8).all()

    return render_template(
        'admin/dashboard.html',
        customer_count=customer_count,
        pharmacy_owners_count=pharmacy_owners_count,
        total_pharmacies=total_pharmacies,
        pending_verifications=pending_verifications,
        verified_pharmacies=verified_pharmacies,
        total_medicines=total_medicines,
        total_orders=total_orders,
        pending_orders=pending_orders,
        total_requests=total_requests,
        pending_pharmacies=pending_pharmacies_list,
        recent_orders=recent_orders_list,
        recent_audit_logs=recent_audit_logs
    )


@admin_bp.route('/pharmacies')
def pharmacies():
    status_filter = request.args.get('status', '')
    query = Pharmacy.query
    if status_filter:
        query = query.filter_by(verification_status=status_filter.upper())

    pharmacies_list = query.order_by(Pharmacy.created_at.desc()).all()
    return render_template('admin/pharmacies.html', pharmacies=pharmacies_list, current_status=status_filter)


@admin_bp.route('/pharmacies/<int:pharmacy_id>/verify', methods=['GET', 'POST'])
def verify_pharmacy(pharmacy_id: int):
    pharmacy = Pharmacy.query.get_or_404(pharmacy_id)
    documents = VerificationDocument.query.filter_by(pharmacy_id=pharmacy.id).all()

    if request.method == 'POST':
        decision = request.form.get('decision') # 'APPROVED' or 'REJECTED'
        notes = request.form.get('notes', '').strip()

        success, msg = PharmacyService.review_verification(
            pharmacy_id=pharmacy.id,
            admin_user_id=current_user.id,
            decision=decision,
            notes=notes,
            ip_address=request.remote_addr
        )

        if success:
            flash(msg, 'success')
        else:
            flash(msg, 'danger')

        return redirect(url_for('admin.pharmacies'))

    return render_template('admin/pharmacy_verify.html', pharmacy=pharmacy, documents=documents)


@admin_bp.route('/pharmacies/<int:pharmacy_id>/toggle-status', methods=['POST'])
def toggle_pharmacy_status(pharmacy_id: int):
    pharmacy = Pharmacy.query.get_or_404(pharmacy_id)
    pharmacy.is_active = not pharmacy.is_active
    db.session.commit()

    action_text = "activated" if pharmacy.is_active else "suspended"
    AuditService.log(
        actor_user_id=current_user.id,
        action=f"PHARMACY_{action_text.upper()}",
        target_type="Pharmacy",
        target_id=pharmacy.id,
        details=f"Admin {action_text} pharmacy '{pharmacy.name}'",
        ip_address=request.remote_addr
    )
    flash(f"Pharmacy has been {action_text}.", 'info')
    return redirect(url_for('admin.pharmacies'))


@admin_bp.route('/medicines')
def medicines():
    query_str = request.args.get('q', '')
    category_id = request.args.get('category_id', type=int)

    medicines_list = MedicineService.search_medicines(query_str=query_str, category_id=category_id, limit=100)
    categories = MedicineService.get_all_categories()

    return render_template('admin/medicines.html', medicines=medicines_list, categories=categories, query=query_str, selected_category=category_id)


@admin_bp.route('/medicines/new', methods=['GET', 'POST'])
def create_medicine():
    categories = MedicineService.get_all_categories()

    if request.method == 'POST':
        data = {
            'name': request.form.get('name', '').strip(),
            'generic_name': request.form.get('generic_name', '').strip(),
            'brand_name': request.form.get('brand_name', '').strip(),
            'strength': request.form.get('strength', '').strip(),
            'dosage_form': request.form.get('dosage_form', 'Tablet').strip(),
            'category_id': request.form.get('category_id', type=int),
            'requires_prescription': bool(request.form.get('requires_prescription')),
            'description': request.form.get('description', '').strip(),
            'manufacturer': request.form.get('manufacturer', '').strip(),
            'usage_instructions': request.form.get('usage_instructions', '').strip(),
            'side_effects_warning': request.form.get('side_effects_warning', '').strip()
        }

        if not data['name'] or not data['generic_name'] or not data['strength']:
            flash("Name, generic name, and strength are mandatory.", 'danger')
            return render_template('admin/medicine_form.html', medicine=None, categories=categories)

        med = MedicineService.create_or_update_medicine(data)
        AuditService.log(
            actor_user_id=current_user.id,
            action="MEDICINE_CREATED",
            target_type="Medicine",
            target_id=med.id,
            details=f"Admin added medicine '{med.name} ({med.strength})'",
            ip_address=request.remote_addr
        )

        flash(f"Medicine '{med.name}' added to catalog.", 'success')
        return redirect(url_for('admin.medicines'))

    return render_template('admin/medicine_form.html', medicine=None, categories=categories)


@admin_bp.route('/medicines/<int:medicine_id>/edit', methods=['GET', 'POST'])
def edit_medicine(medicine_id: int):
    medicine = Medicine.query.get_or_404(medicine_id)
    categories = MedicineService.get_all_categories()

    if request.method == 'POST':
        data = {
            'name': request.form.get('name', '').strip(),
            'generic_name': request.form.get('generic_name', '').strip(),
            'brand_name': request.form.get('brand_name', '').strip(),
            'strength': request.form.get('strength', '').strip(),
            'dosage_form': request.form.get('dosage_form', 'Tablet').strip(),
            'category_id': request.form.get('category_id', type=int),
            'requires_prescription': bool(request.form.get('requires_prescription')),
            'description': request.form.get('description', '').strip(),
            'manufacturer': request.form.get('manufacturer', '').strip(),
            'usage_instructions': request.form.get('usage_instructions', '').strip(),
            'side_effects_warning': request.form.get('side_effects_warning', '').strip()
        }

        MedicineService.create_or_update_medicine(data, medicine_id=medicine.id)
        AuditService.log(
            actor_user_id=current_user.id,
            action="MEDICINE_UPDATED",
            target_type="Medicine",
            target_id=medicine.id,
            details=f"Admin updated medicine '{medicine.name}'",
            ip_address=request.remote_addr
        )

        flash(f"Medicine '{medicine.name}' updated successfully.", 'success')
        return redirect(url_for('admin.medicines'))

    return render_template('admin/medicine_form.html', medicine=medicine, categories=categories)


@admin_bp.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        slug = request.form.get('slug', '').strip() or name.lower().replace(' ', '-')
        desc = request.form.get('description', '').strip()
        icon = request.form.get('icon', 'fa-pills').strip()

        if not name:
            flash("Category name is required.", 'danger')
        else:
            MedicineService.create_or_update_category(name, slug, desc, icon)
            flash(f"Category '{name}' saved.", 'success')
            return redirect(url_for('admin.categories'))

    categories_list = MedicineService.get_all_categories()
    return render_template('admin/categories.html', categories=categories_list)


@admin_bp.route('/users')
def users():
    role_filter = request.args.get('role', '')
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)

    users_list = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list, current_role=role_filter)


@admin_bp.route('/orders')
def orders():
    status_filter = request.args.get('status', '')
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    orders_list = query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders_list, current_status=status_filter)


@admin_bp.route('/audit-logs')
def audit_logs():
    logs = AuditService.get_recent_logs(limit=150)
    return render_template('admin/audit_logs.html', logs=logs)
