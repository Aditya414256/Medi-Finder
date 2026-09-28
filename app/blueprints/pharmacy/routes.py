from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from app.models.medicine import Medicine, MedicineCategory
from app.models.pharmacy import Pharmacy, VerificationDocument
from app.models.inventory import PharmacyInventory
from app.models.order import Order
from app.models.request import MedicineRequest
from app.models.prescription import Prescription
from app.services.inventory_service import InventoryService
from app.services.pharmacy_service import PharmacyService
from app.services.order_service import OrderService
from app.services.prescription_service import PrescriptionService
from app.utils.security import role_required, validate_file_upload, save_secure_upload
from app.utils.helpers import humanize_time_ago

pharmacy_bp = Blueprint('pharmacy', __name__, url_prefix='/pharmacy')

@pharmacy_bp.before_request
@role_required('pharmacy', 'admin')
def check_pharmacy_access():
    pass


@pharmacy_bp.route('/dashboard')
def dashboard():
    pharmacy = current_user.pharmacy
    if not pharmacy:
        flash("Please complete your pharmacy registration.", 'warning')
        return redirect(url_for('pharmacy.profile'))

    stats = InventoryService.get_inventory_stats(pharmacy.id)
    pending_orders_count = Order.query.filter_by(pharmacy_id=pharmacy.id, status=Order.STATUS_PENDING).count()
    active_orders_count = Order.query.filter_by(pharmacy_id=pharmacy.id).filter(
        Order.status.in_([Order.STATUS_ACCEPTED, Order.STATUS_CONFIRMED, Order.STATUS_PREPARING, Order.STATUS_READY_FOR_PICKUP, Order.STATUS_OUT_FOR_DELIVERY])
    ).count()
    pending_requests_count = MedicineRequest.query.filter_by(pharmacy_id=pharmacy.id, status='PENDING').count()

    recent_orders = Order.query.filter_by(pharmacy_id=pharmacy.id).order_by(Order.created_at.desc()).limit(5).all()
    recent_requests = MedicineRequest.query.filter_by(pharmacy_id=pharmacy.id).order_by(MedicineRequest.created_at.desc()).limit(5).all()

    return render_template(
        'pharmacy/dashboard.html',
        pharmacy=pharmacy,
        stats=stats,
        pending_orders_count=pending_orders_count,
        active_orders_count=active_orders_count,
        pending_requests_count=pending_requests_count,
        recent_orders=recent_orders,
        recent_requests=recent_requests
    )


@pharmacy_bp.route('/inventory', methods=['GET', 'POST'])
def inventory():
    pharmacy = current_user.pharmacy
    if not pharmacy:
        return redirect(url_for('pharmacy.profile'))

    query_str = request.args.get('q', '')
    status_filter = request.args.get('status', '')

    if request.method == 'POST':
        # Add or update medicine in inventory
        action = request.form.get('action', 'add')
        
        if action == 'delete':
            inv_id = request.form.get('inventory_id', type=int)
            if InventoryService.delete_inventory_item(pharmacy.id, inv_id):
                flash("Medicine removed from inventory.", 'info')
            else:
                flash("Item not found or could not be removed.", 'danger')
            return redirect(url_for('pharmacy.inventory'))

        medicine_id = request.form.get('medicine_id', type=int)
        quantity = request.form.get('quantity', 0, type=int)
        price = request.form.get('price', 0.0, type=float)
        batch_number = request.form.get('batch_number', '').strip() or None
        notes = request.form.get('notes', '').strip() or None

        item, err = InventoryService.add_or_update_inventory_item(
            pharmacy_id=pharmacy.id,
            medicine_id=medicine_id,
            quantity=quantity,
            price=price,
            notes=notes,
            batch_number=batch_number
        )

        if err:
            flash(err, 'danger')
        else:
            flash(f"Inventory updated for {item.medicine.name}. (Timestamp refreshed: {humanize_time_ago(item.last_updated_at)})", 'success')

        return redirect(url_for('pharmacy.inventory'))

    inventory_items = InventoryService.get_pharmacy_inventory(pharmacy.id, query_str=query_str, status_filter=status_filter)
    all_medicines = Medicine.query.order_by(Medicine.name.asc()).all()

    return render_template(
        'pharmacy/inventory.html',
        pharmacy=pharmacy,
        inventory_items=inventory_items,
        all_medicines=all_medicines,
        query=query_str,
        status_filter=status_filter,
        humanize_time_ago=humanize_time_ago
    )


@pharmacy_bp.route('/inventory/quick-update', methods=['POST'])
def inventory_quick_update():
    pharmacy = current_user.pharmacy
    if not pharmacy:
        abort(403)

    inv_id = request.form.get('inventory_id', type=int)
    item = PharmacyInventory.query.filter_by(id=inv_id, pharmacy_id=pharmacy.id).first_or_404()

    new_qty = request.form.get('quantity', item.quantity, type=int)
    new_price = request.form.get('price', item.price, type=float)

    item.update_stock(quantity=new_qty, price=new_price)
    from app.extensions import db
    db.session.commit()

    flash(f"Stock for '{item.medicine.name}' set to {item.quantity} ({item.stock_status}). Timestamp updated: {humanize_time_ago(item.last_updated_at)}", 'success')
    return redirect(url_for('pharmacy.inventory'))


@pharmacy_bp.route('/requests', methods=['GET', 'POST'])
def requests():
    pharmacy = current_user.pharmacy
    if not pharmacy:
        return redirect(url_for('pharmacy.profile'))

    if request.method == 'POST':
        req_id = request.form.get('request_id', type=int)
        decision = request.form.get('decision', 'ACCEPTED') # ACCEPTED / REJECTED / FULFILLED
        response_text = request.form.get('response', '').strip()

        req = MedicineRequest.query.filter_by(id=req_id, pharmacy_id=pharmacy.id).first_or_404()
        success, msg = OrderService.respond_to_request(req.id, decision, response_text)
        if success:
            flash(msg, 'success')
        else:
            flash(msg, 'danger')

        return redirect(url_for('pharmacy.requests'))

    medicine_requests = MedicineRequest.query.filter_by(pharmacy_id=pharmacy.id).order_by(MedicineRequest.created_at.desc()).all()
    return render_template('pharmacy/requests.html', pharmacy=pharmacy, requests=medicine_requests)


@pharmacy_bp.route('/orders')
def orders():
    pharmacy = current_user.pharmacy
    if not pharmacy:
        return redirect(url_for('pharmacy.profile'))

    status_filter = request.args.get('status', '')
    query = Order.query.filter_by(pharmacy_id=pharmacy.id)
    if status_filter:
        query = query.filter_by(status=status_filter)

    orders_list = query.order_by(Order.created_at.desc()).all()
    return render_template('pharmacy/orders.html', pharmacy=pharmacy, orders=orders_list, current_status=status_filter)


@pharmacy_bp.route('/orders/<int:order_id>', methods=['GET', 'POST'])
def order_detail(order_id: int):
    pharmacy = current_user.pharmacy
    order = Order.query.filter_by(id=order_id, pharmacy_id=pharmacy.id).first_or_404()

    if request.method == 'POST':
        new_status = request.form.get('new_status')
        pharmacy_notes = request.form.get('pharmacy_notes', '').strip()
        rejection_reason = request.form.get('rejection_reason', '').strip()

        success, msg = OrderService.transition_order_status(
            order_id=order.id,
            new_status=new_status,
            actor_user_id=current_user.id,
            notes=pharmacy_notes,
            reason=rejection_reason,
            ip_address=request.remote_addr
        )

        if success:
            flash(msg, 'success')
        else:
            flash(msg, 'danger')

        return redirect(url_for('pharmacy.order_detail', order_id=order.id))

    return render_template('pharmacy/order_detail.html', pharmacy=pharmacy, order=order)


@pharmacy_bp.route('/prescriptions', methods=['GET', 'POST'])
def prescriptions():
    """
    Manual prescription review portal for pharmacy staff.
    CRITICAL: Automated AI approval is strictly prohibited.
    """
    pharmacy = current_user.pharmacy
    if not pharmacy:
        return redirect(url_for('pharmacy.profile'))

    if request.method == 'POST':
        rx_id = request.form.get('prescription_id', type=int)
        decision = request.form.get('decision') # 'APPROVED' or 'REJECTED'
        reason = request.form.get('rejection_reason', '').strip()

        success, msg = PrescriptionService.manual_review_prescription(
            prescription_id=rx_id,
            reviewer_user_id=current_user.id,
            decision=decision,
            rejection_reason=reason,
            ip_address=request.remote_addr
        )

        if success:
            flash(msg, 'success')
        else:
            flash(msg, 'danger')

        return redirect(url_for('pharmacy.prescriptions'))

    # Find prescriptions associated with orders or requests for this pharmacy
    order_rx_ids = [o.prescription_id for o in Order.query.filter_by(pharmacy_id=pharmacy.id).filter(Order.prescription_id.isnot(None)).all()]
    req_rx_ids = [r.prescription_id for r in MedicineRequest.query.filter_by(pharmacy_id=pharmacy.id).filter(MedicineRequest.prescription_id.isnot(None)).all()]
    all_rx_ids = list(set(order_rx_ids + req_rx_ids))

    prescriptions_list = Prescription.query.filter(Prescription.id.in_(all_rx_ids)).order_by(Prescription.created_at.desc()).all() if all_rx_ids else []

    return render_template('pharmacy/prescriptions.html', pharmacy=pharmacy, prescriptions=prescriptions_list)


@pharmacy_bp.route('/verification', methods=['GET', 'POST'])
def verification():
    pharmacy = current_user.pharmacy
    if not pharmacy:
        return redirect(url_for('pharmacy.profile'))

    if request.method == 'POST':
        if 'document_file' not in request.files:
            flash("Please choose a document file.", 'danger')
            return redirect(url_for('pharmacy.verification'))

        file = request.files['document_file']
        doc_type = request.form.get('document_type', 'Drug License').strip()

        is_valid, err, ext = validate_file_upload(file)
        if not is_valid:
            flash(err, 'danger')
            return redirect(url_for('pharmacy.verification'))

        target_dir = current_app.config['VERIFICATION_DOCS_DIR']
        saved_filename, orig_filename, mime_type, file_size = save_secure_upload(file, target_dir, prefix='verif')

        PharmacyService.add_verification_document(
            pharmacy_id=pharmacy.id,
            doc_type=doc_type,
            file_path=saved_filename,
            original_filename=orig_filename,
            mime_type=mime_type,
            file_size=file_size
        )

        flash(f"Verification document '{doc_type}' uploaded. Our admin team will review it shortly.", 'success')
        return redirect(url_for('pharmacy.verification'))

    documents = VerificationDocument.query.filter_by(pharmacy_id=pharmacy.id).order_by(VerificationDocument.uploaded_at.desc()).all()
    return render_template('pharmacy/verification.html', pharmacy=pharmacy, documents=documents)


@pharmacy_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    pharmacy = current_user.pharmacy

    if request.method == 'POST':
        data = {
            'name': request.form.get('name', '').strip(),
            'license_number': request.form.get('license_number', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'email': request.form.get('email', '').strip(),
            'address': request.form.get('address', '').strip(),
            'city': request.form.get('city', '').strip(),
            'state': request.form.get('state', '').strip(),
            'pincode': request.form.get('pincode', '').strip(),
            'latitude': request.form.get('latitude', '0.0'),
            'longitude': request.form.get('longitude', '0.0'),
            'supports_pickup': bool(request.form.get('supports_pickup')),
            'supports_delivery': bool(request.form.get('supports_delivery')),
            'delivery_fee': request.form.get('delivery_fee', '0.0'),
            'opening_hours': request.form.get('opening_hours', '9:00 AM - 9:00 PM')
        }

        pharmacy, err = PharmacyService.create_or_update_pharmacy(
            owner_id=current_user.id,
            data=data,
            pharmacy_id=pharmacy.id if pharmacy else None
        )

        if err:
            flash(err, 'danger')
        else:
            flash("Pharmacy settings updated successfully.", 'success')

        return redirect(url_for('pharmacy.profile'))

    return render_template('pharmacy/profile.html', pharmacy=pharmacy)
