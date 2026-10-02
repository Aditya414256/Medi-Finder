from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.services.auth_service import AuthService
from app.services.pharmacy_service import PharmacyService
from app.services.audit_service import AuditService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_pharmacy:
            return redirect(url_for('pharmacy.dashboard'))
        return redirect(url_for('customer.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user, err = AuthService.authenticate(email, password)
        if err:
            flash(err, 'danger')
        else:
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.full_name}!", 'success')
            
            # Audit log
            AuditService.log(
                actor_user_id=user.id,
                action='USER_LOGIN',
                target_type='User',
                target_id=user.id,
                details=f"User {user.email} logged in ({user.role})",
                ip_address=request.remote_addr
            )

            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)

            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            elif user.is_pharmacy:
                return redirect(url_for('pharmacy.dashboard'))
            return redirect(url_for('customer.home'))

    return render_template('auth/login.html')


@auth_bp.route('/register')
def register_choice():
    if current_user.is_authenticated:
        return redirect(url_for('customer.home'))
    return render_template('auth/register_choice.html')


@auth_bp.route('/register/customer', methods=['GET', 'POST'])
@auth_bp.route('/register-customer', methods=['GET', 'POST'])
def register_customer():
    if current_user.is_authenticated:
        return redirect(url_for('customer.home'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()

        if password != confirm_password:
            flash("Passwords do not match.", 'danger')
            return render_template('auth/register_customer.html', form_data=request.form)

        user, err = AuthService.register_user(
            email=email,
            password=password,
            full_name=full_name,
            phone=phone,
            role='customer'
        )
        if err:
            flash(err, 'danger')
            return render_template('auth/register_customer.html', form_data=request.form)

        login_user(user)
        flash("Registration successful! Welcome to MediFind.", 'success')
        return redirect(url_for('customer.home'))

    return render_template('auth/register_customer.html', form_data={})


@auth_bp.route('/register/pharmacy', methods=['GET', 'POST'])
@auth_bp.route('/register-pharmacy', methods=['GET', 'POST'])
def register_pharmacy():
    if current_user.is_authenticated:
        return redirect(url_for('customer.home'))

    if request.method == 'POST':
        # Account info
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        owner_phone = request.form.get('phone', '').strip()

        # Pharmacy info
        pharmacy_name = request.form.get('pharmacy_name', '').strip()
        license_number = request.form.get('license_number', '').strip()
        pharmacy_phone = request.form.get('pharmacy_phone', '').strip() or owner_phone
        pharmacy_email = request.form.get('pharmacy_email', '').strip() or email
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        latitude = request.form.get('latitude', '0.0')
        longitude = request.form.get('longitude', '0.0')
        supports_pickup = bool(request.form.get('supports_pickup'))
        supports_delivery = bool(request.form.get('supports_delivery'))
        delivery_fee = request.form.get('delivery_fee', '0.0')

        if password != confirm_password:
            flash("Passwords do not match.", 'danger')
            return render_template('auth/register_pharmacy.html', form_data=request.form)

        if not pharmacy_name or not license_number or not address or not city or not pincode:
            flash("Please fill in all mandatory pharmacy details.", 'danger')
            return render_template('auth/register_pharmacy.html', form_data=request.form)

        user, err = AuthService.register_user(
            email=email,
            password=password,
            full_name=full_name,
            phone=owner_phone,
            role='pharmacy'
        )
        if err:
            flash(err, 'danger')
            return render_template('auth/register_pharmacy.html', form_data=request.form)

        # Create Pharmacy record
        pharmacy_data = {
            'name': pharmacy_name,
            'license_number': license_number,
            'phone': pharmacy_phone,
            'email': pharmacy_email,
            'address': address,
            'city': city,
            'state': state,
            'pincode': pincode,
            'latitude': latitude,
            'longitude': longitude,
            'supports_pickup': supports_pickup,
            'supports_delivery': supports_delivery,
            'delivery_fee': delivery_fee
        }
        pharmacy, p_err = PharmacyService.create_or_update_pharmacy(user.id, pharmacy_data)
        if p_err:
            flash(p_err, 'danger')
            return render_template('auth/register_pharmacy.html', form_data=request.form)

        login_user(user)
        flash("Pharmacy account created! Please upload your verification documents to complete activation.", 'info')
        return redirect(url_for('pharmacy.verification'))

    return render_template('auth/register_pharmacy.html', form_data={})


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been successfully logged out.", 'info')
    return redirect(url_for('customer.home'))
