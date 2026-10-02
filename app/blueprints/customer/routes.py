import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from app.models.medicine import Medicine, MedicineCategory
from app.models.pharmacy import Pharmacy
from app.models.inventory import PharmacyInventory
from app.models.order import Order
from app.models.request import MedicineRequest
from app.models.prescription import Prescription
from app.services.medicine_service import MedicineService
from app.services.location_service import LocationService
from app.services.order_service import OrderService
from app.services.prescription_service import PrescriptionService
from app.services.notification_service import NotificationService
from app.utils.security import validate_file_upload, save_secure_upload
from app.utils.helpers import humanize_time_ago, sanitize_search_query

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/')
def home():
    categories = MedicineService.get_all_categories()
    featured_medicines = Medicine.query.limit(8).all()
    verified_pharmacies_count = Pharmacy.query.filter_by(verification_status='APPROVED', is_active=True).count()
    medicines_count = Medicine.query.count()
    return render_template(
        'customer/home.html',
        categories=categories,
        featured_medicines=featured_medicines,
        verified_count=verified_pharmacies_count,
        medicines_count=medicines_count
    )


@customer_bp.route('/search')
def search():
    query_str = sanitize_search_query(request.args.get('q', ''))
    category_id = request.args.get('category_id', type=int)
    rx_filter = request.args.get('requires_prescription')
    
    prescription_only = None
    if rx_filter == '1':
        prescription_only = True
    elif rx_filter == '0':
        prescription_only = False

    medicines = MedicineService.search_medicines(
        query_str=query_str,
        category_id=category_id,
        prescription_only=prescription_only,
        limit=60
    )

    categories = MedicineService.get_all_categories()

    # Pre-fetch availability stats and price for each medicine
    medicine_stats = {}
    for med in medicines:
        inv_items = PharmacyInventory.query.filter_by(medicine_id=med.id).join(Pharmacy).filter(
            Pharmacy.verification_status == 'APPROVED',
            Pharmacy.is_active == True,
            PharmacyInventory.stock_status.in_(['AVAILABLE', 'LOW_STOCK'])
        ).all()
        verified_stock = len(inv_items)
        prices = [item.price for item in inv_items if item.price and item.price > 0]
        min_price = min(prices) if prices else None
        if not min_price:
            any_inv = PharmacyInventory.query.filter_by(medicine_id=med.id).filter(PharmacyInventory.price > 0).first()
            if any_inv:
                min_price = any_inv.price

        medicine_stats[med.id] = {
            'verified_pharmacies_count': verified_stock,
            'price': min_price
        }

    return render_template(
        'customer/search.html',
        query=query_str,
        medicines=medicines,
        categories=categories,
        selected_category=category_id,
        rx_filter=rx_filter,
        medicine_stats=medicine_stats
    )


@customer_bp.route('/medicine/<int:medicine_id>')
def medicine_detail(medicine_id: int):
    medicine = MedicineService.get_medicine_by_id(medicine_id)
    if not medicine:
        abort(404)

    # Location & filter queries
    user_lat = request.args.get('lat', type=float)
    user_lon = request.args.get('lon', type=float)
    max_radius = request.args.get('radius', 50.0, type=float)
    only_verified = request.args.get('verified', '0') == '1'
    only_available = request.args.get('available', '0') == '1'
    requires_pickup = request.args.get('pickup', '0') == '1'
    requires_delivery = request.args.get('delivery', '0') == '1'
    sort_by = request.args.get('sort', 'nearest')

    pharmacies = LocationService.get_nearby_pharmacies_for_medicine(
        medicine_id=medicine.id,
        customer_lat=user_lat,
        customer_lon=user_lon,
        max_radius_km=max_radius,
        only_verified=only_verified,
        only_available=only_available,
        requires_pickup=requires_pickup,
        requires_delivery=requires_delivery,
        sort_by=sort_by
    )

    return render_template(
        'customer/medicine_detail.html',
        medicine=medicine,
        pharmacies=pharmacies,
        user_lat=user_lat,
        user_lon=user_lon,
        max_radius=max_radius,
        only_verified=only_verified,
        only_available=only_available,
        requires_pickup=requires_pickup,
        requires_delivery=requires_delivery,
        sort_by=sort_by
    )


@customer_bp.route('/pharmacy/<int:pharmacy_id>')
def pharmacy_detail(pharmacy_id: int):
    pharmacy = Pharmacy.query.get_or_404(pharmacy_id)
    search_q = request.args.get('q', '').strip()
    
    query = PharmacyInventory.query.filter_by(pharmacy_id=pharmacy.id).join(Medicine)
    if search_q:
        term = f"%{search_q}%"
        query = query.filter((Medicine.name.ilike(term)) | (Medicine.generic_name.ilike(term)))
    
    inventory_records = query.order_by(PharmacyInventory.last_updated_at.desc()).all()

    return render_template(
        'customer/pharmacy_detail.html',
        pharmacy=pharmacy,
        inventory_records=inventory_records,
        search_query=search_q,
        humanize_time_ago=humanize_time_ago
    )


@customer_bp.route('/pharmacies')
@customer_bp.route('/map')
def map_view():
    user_lat = request.args.get('lat', type=float)
    user_lon = request.args.get('lon', type=float)
    max_radius = request.args.get('radius', 50.0, type=float)
    verified_only = request.args.get('verified', '0') == '1'
    search_q = request.args.get('q', '').strip()

    pharmacies = LocationService.get_all_nearby_pharmacies(
        customer_lat=user_lat,
        customer_lon=user_lon,
        max_radius_km=max_radius,
        only_verified=verified_only
    )

    if search_q:
        term = search_q.lower()
        pharmacies = [p for p in pharmacies if term in p['name'].lower() or term in p['city'].lower() or term in p['address'].lower()]

    return render_template(
        'customer/map.html',
        pharmacies=pharmacies,
        user_lat=user_lat,
        user_lon=user_lon,
        max_radius=max_radius,
        verified_only=verified_only,
        search_q=search_q
    )


@customer_bp.route('/request', methods=['GET', 'POST'])
@login_required
def create_request():
    med_id = request.args.get('medicine_id', type=int)
    pharmacy_id = request.args.get('pharmacy_id', type=int)
    
    selected_medicine = Medicine.query.get(med_id) if med_id else None
    selected_pharmacy = Pharmacy.query.get(pharmacy_id) if pharmacy_id else None

    user_prescriptions = PrescriptionService.get_prescriptions_for_customer(current_user.id)

    if request.method == 'POST':
        p_id = request.form.get('pharmacy_id', type=int)
        m_id = request.form.get('medicine_id', type=int)
        qty = request.form.get('quantity', 1, type=int)
        rx_id = request.form.get('prescription_id', type=int) or None
        notes = request.form.get('notes', '').strip()

        req, err = OrderService.create_medicine_request(
            customer_id=current_user.id,
            pharmacy_id=p_id,
            medicine_id=m_id,
            quantity=qty,
            prescription_id=rx_id,
            notes=notes
        )
        if err:
            flash(err, 'danger')
        else:
            flash("Your medicine availability request was sent to the pharmacy.", 'success')
            return redirect(url_for('customer.requests_list'))

    medicines = Medicine.query.order_by(Medicine.name.asc()).all()
    pharmacies = Pharmacy.query.filter_by(verification_status='APPROVED', is_active=True).order_by(Pharmacy.name.asc()).all()

    return render_template(
        'customer/request_form.html',
        selected_medicine=selected_medicine,
        selected_pharmacy=selected_pharmacy,
        medicines=medicines,
        pharmacies=pharmacies,
        prescriptions=user_prescriptions
    )


@customer_bp.route('/requests')
@login_required
def requests_list():
    requests = MedicineRequest.query.filter_by(customer_id=current_user.id).order_by(MedicineRequest.created_at.desc()).all()
    return render_template('customer/requests_list.html', requests=requests)


@customer_bp.route('/orders/new', methods=['GET', 'POST'])
@login_required
def create_order():
    pharmacy_id = request.args.get('pharmacy_id', type=int)
    medicine_id = request.args.get('medicine_id', type=int)

    pharmacy = Pharmacy.query.get_or_404(pharmacy_id)
    medicine = Medicine.query.get_or_404(medicine_id)

    inventory_item = PharmacyInventory.query.filter_by(pharmacy_id=pharmacy.id, medicine_id=medicine.id).first()
    if not inventory_item or inventory_item.stock_status == 'OUT_OF_STOCK':
        flash("This medicine is currently out of stock at this pharmacy.", 'warning')

    user_prescriptions = PrescriptionService.get_prescriptions_for_customer(current_user.id)

    if request.method == 'POST':
        order_type = request.form.get('order_type', 'PICKUP')
        delivery_address = request.form.get('delivery_address', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip() or (current_user.phone or '')
        prescription_id = request.form.get('prescription_id', type=int) or None
        customer_notes = request.form.get('customer_notes', '').strip()
        quantity = request.form.get('quantity', 1, type=int)

        if not contact_phone:
            flash("A valid contact phone number is required.", 'danger')
            return render_template(
                'customer/order_create.html',
                pharmacy=pharmacy,
                medicine=medicine,
                inventory_item=inventory_item,
                prescriptions=user_prescriptions
            )

        items_data = [{'medicine_id': medicine.id, 'quantity': quantity}]

        order, err = OrderService.create_order(
            customer_id=current_user.id,
            pharmacy_id=pharmacy.id,
            order_type=order_type,
            contact_phone=contact_phone,
            items_data=items_data,
            delivery_address=delivery_address,
            prescription_id=prescription_id,
            customer_notes=customer_notes
        )

        if err:
            flash(err, 'danger')
        else:
            flash(f"Order #{order.order_number} placed successfully! The pharmacy will review it shortly.", 'success')
            return redirect(url_for('customer.order_detail', order_id=order.id))

    return render_template(
        'customer/order_create.html',
        pharmacy=pharmacy,
        medicine=medicine,
        inventory_item=inventory_item,
        prescriptions=user_prescriptions
    )


@customer_bp.route('/orders')
@login_required
def orders_list():
    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('customer/orders_list.html', orders=orders)


@customer_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id: int):
    order = Order.query.get_or_404(order_id)
    if order.customer_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template('customer/order_detail.html', order=order)


@customer_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id: int):
    order = Order.query.get_or_404(order_id)
    if order.customer_id != current_user.id:
        abort(403)

    if order.status not in (Order.STATUS_PENDING, Order.STATUS_ACCEPTED):
        flash("Orders cannot be cancelled once they are in preparation or ready.", 'danger')
        return redirect(url_for('customer.order_detail', order_id=order.id))

    reason = request.form.get('reason', 'Cancelled by customer')
    success, msg = OrderService.transition_order_status(
        order_id=order.id,
        new_status=Order.STATUS_CANCELLED,
        actor_user_id=current_user.id,
        reason=reason,
        ip_address=request.remote_addr
    )
    if success:
        flash("Your order has been cancelled.", 'info')
    else:
        flash(msg, 'danger')

    return redirect(url_for('customer.order_detail', order_id=order.id))


@customer_bp.route('/prescriptions')
@login_required
def prescriptions():
    user_prescriptions = PrescriptionService.get_prescriptions_for_customer(current_user.id)
    return render_template('customer/prescriptions.html', prescriptions=user_prescriptions)


@customer_bp.route('/prescriptions/upload', methods=['POST'])
@login_required
def upload_prescription():
    if 'prescription_file' not in request.files:
        flash("No file provided.", 'danger')
        return redirect(url_for('customer.prescriptions'))

    file = request.files['prescription_file']
    is_valid, err, ext = validate_file_upload(file)
    if not is_valid:
        flash(err, 'danger')
        return redirect(url_for('customer.prescriptions'))

    patient_name = request.form.get('patient_name', '').strip()
    doctor_name = request.form.get('doctor_name', '').strip()
    notes = request.form.get('notes', '').strip()

    target_dir = current_app.config['PRESCRIPTIONS_DIR']
    saved_filename, orig_filename, mime_type, file_size = save_secure_upload(file, target_dir, prefix='rx')

    PrescriptionService.create_prescription(
        customer_id=current_user.id,
        file_path=saved_filename,
        original_filename=orig_filename,
        mime_type=mime_type,
        file_size=file_size,
        patient_name=patient_name,
        doctor_name=doctor_name,
        notes=notes
    )

    flash("Prescription uploaded successfully. It will be reviewed manually when placed with an order.", 'success')
    return redirect(url_for('customer.prescriptions'))


@customer_bp.route('/notifications')
@login_required
def notifications():
    user_notifications = NotificationService.get_user_notifications(current_user.id)
    return render_template('customer/notifications.html', notifications=user_notifications)


@customer_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    NotificationService.mark_all_as_read(current_user.id)
    flash("All notifications marked as read.", 'info')
    return redirect(url_for('customer.notifications'))


@customer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        if not full_name:
            flash("Full name cannot be empty.", 'danger')
        else:
            current_user.full_name = full_name
            current_user.phone = phone
            from app.extensions import db
            db.session.commit()
            flash("Profile updated successfully.", 'success')

    return render_template('customer/profile.html', user=current_user)
