import pytest
from app.models.user import User
from app.services.auth_service import AuthService

def test_user_registration_and_password_hashing(app):
    with app.app_context():
        user, err = AuthService.register_user(
            email='newuser@example.com',
            password='SecretPassword123',
            full_name='New Test User',
            role='customer'
        )
        assert err is None
        assert user is not None
        assert user.check_password('SecretPassword123') is True
        assert user.check_password('WrongPassword') is False
        assert user.password_hash != 'SecretPassword123'

def test_duplicate_email_rejected(app):
    with app.app_context():
        AuthService.register_user('dup@example.com', 'Pass1234', 'User One')
        _, err = AuthService.register_user('dup@example.com', 'Pass1234', 'User Two')
        assert err is not None
        assert 'already exists' in err.lower()

def test_auth_service_login_validations(app):
    with app.app_context():
        AuthService.register_user('login_test@example.com', 'ValidPass123', 'User Test')
        
        # Valid login
        user, err = AuthService.authenticate('login_test@example.com', 'ValidPass123')
        assert err is None
        assert user.email == 'login_test@example.com'

        # Invalid password
        bad_user, bad_err = AuthService.authenticate('login_test@example.com', 'WrongPass')
        assert bad_user is None
        assert bad_err == 'Invalid email or password.'

def test_role_based_access_restrictions(client, test_data):
    # Unauthenticated accessing admin route -> 401 redirect to login
    res = client.get('/admin/', follow_redirects=False)
    assert res.status_code in (302, 401)

    # Customer trying to access Admin panel -> 403 Forbidden
    client.post('/auth/login', data={'email': 'customer_test@example.com', 'password': 'CustPass123!'})
    res_admin = client.get('/admin/')
    assert res_admin.status_code == 403

    # Customer trying to access Pharmacy dashboard -> 403 Forbidden
    res_pharm = client.get('/pharmacy/dashboard')
    assert res_pharm.status_code == 403

    # Pharmacy owner accessing pharmacy dashboard -> 200 OK
    client.get('/auth/logout')
    client.post('/auth/login', data={'email': 'pharmacy_test@example.com', 'password': 'PharmPass123!'})
    res_pharm_ok = client.get('/pharmacy/dashboard')
    assert res_pharm_ok.status_code == 200

    # Pharmacy owner trying to access admin -> 403 Forbidden
    res_admin_forbidden = client.get('/admin/')
    assert res_admin_forbidden.status_code == 403

    # Admin accessing admin -> 200 OK
    client.get('/auth/logout')
    client.post('/auth/login', data={'email': 'admin_test@example.com', 'password': 'AdminPass123!'})
    res_admin_ok = client.get('/admin/')
    assert res_admin_ok.status_code == 200

def test_register_choice_page(client):
    res = client.get('/auth/register')
    assert res.status_code == 200
    assert b'How do you want to use MediFind?' in res.data
    assert b'Customer' in res.data
    assert b'Pharmacy' in res.data
    # Ensure Admin registration is NEVER displayed publicly
    assert b'Register as Admin' not in res.data

def test_customer_registration_flow(client):
    res = client.get('/auth/register/customer')
    assert res.status_code == 200
    assert b'Create Customer Account' in res.data

    res_post = client.post('/auth/register/customer', data={
        'full_name': 'New Public Customer',
        'email': 'public_customer@example.com',
        'password': 'SecurePassword123!',
        'confirm_password': 'SecurePassword123!',
        'phone': '1234567890'
    }, follow_redirects=True)
    assert res_post.status_code == 200
    assert b'Registration successful' in res_post.data

def test_pharmacy_registration_flow(client):
    res = client.get('/auth/register/pharmacy')
    assert res.status_code == 200
    assert b'Register Your Pharmacy' in res.data

