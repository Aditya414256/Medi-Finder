import pytest
from app.services.medicine_service import MedicineService

def test_search_by_medicine_name(app, test_data):
    with app.app_context():
        results = MedicineService.search_medicines('Paracetamol')
        assert len(results) >= 1
        assert any('Paracetamol' in m.name for m in results)

def test_search_by_generic_name(app, test_data):
    with app.app_context():
        results = MedicineService.search_medicines('Acetaminophen')
        assert len(results) >= 1
        assert any(m.generic_name == 'Acetaminophen' for m in results)

def test_search_by_brand_name(app, test_data):
    with app.app_context():
        results = MedicineService.search_medicines('Novamox')
        assert len(results) >= 1
        assert any(m.name == 'Amoxicillin 500mg Test' for m in results)

def test_search_prescription_filter(app, test_data):
    with app.app_context():
        rx_results = MedicineService.search_medicines('', prescription_only=True)
        assert all(m.requires_prescription for m in rx_results)

        otc_results = MedicineService.search_medicines('', prescription_only=False)
        assert all(not m.requires_prescription for m in otc_results)

def test_api_medicine_search_endpoint(client, test_data):
    res = client.get('/api/medicines/search?q=Paracetamol')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert data['count'] >= 1
    assert data['results'][0]['name'] == 'Paracetamol 500mg Test'

def test_api_medicine_suggestions_endpoint(client, test_data):
    # Test partial prefix match (autocomplete "para")
    res = client.get('/api/medicines/suggestions?q=para')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert data['count'] >= 1
    sugg = data['suggestions'][0]
    assert 'Paracetamol' in sugg['name']
    assert 'url' in sugg
    assert sugg['url'].startswith('/medicine/')

def test_api_medicine_suggestions_empty(client, test_data):
    res = client.get('/api/medicines/suggestions?q=')
    assert res.status_code == 200
    data = res.get_json()
    assert data['suggestions'] == []


def test_unified_home_page_loads(client, test_data):
    """Verify / loads the unified discovery page with reference design elements."""
    res = client.get('/')
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert 'Find your medicine' in html
    assert 'verified pharmacy' in html
    assert 'Search for medicines' in html
    # Check unified navigation
    assert 'Find Medicine' in html
    assert 'Pharmacies' in html
    # Check logo icon from frontend reference
    assert 'logo-icon' in html
    assert '+' in html
    # Check feature highlights (no-query state)
    assert 'Verified Pharmacies' in html
    assert 'Real-Time Stock' in html


def test_unified_home_search_valid_query(client, test_data):
    """Verify search submission on / displays matching database records and detail links."""
    res = client.get('/?q=Paracetamol')
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert 'Paracetamol 500mg Test' in html
    assert 'Acetaminophen' in html
    assert 'OTC' in html
    assert 'View Stores' in html
    assert f"/medicine/{test_data['med_otc_id']}" in html
    assert 'Found' in html
    assert 'matching medicine' in html


def test_unified_home_search_prescription_badge(client, test_data):
    """Verify prescription-required medicine displays Rx badge."""
    res = client.get('/?q=Amoxicillin')
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert 'Amoxicillin 500mg Test' in html
    assert 'Rx Required' in html
    assert 'View Stores' in html
    assert f"/medicine/{test_data['med_rx_id']}" in html


def test_unified_home_search_unknown_query(client, test_data):
    """Verify unknown query displays an informative empty state."""
    res = client.get('/?q=NonExistentMedicineXYZ')
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert 'No medicines found' in html
    assert 'Clear Search' in html


def test_unified_home_search_blank_query(client, test_data):
    """Verify blank search query is handled gracefully and shows discovery hero."""
    res = client.get('/?q=')
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert 'Find your medicine' in html


def test_search_endpoint_backward_compatibility(client, test_data):
    """Verify /search remains backward-compatible and preserves query."""
    res = client.get('/search?q=Paracetamol')
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert 'Paracetamol 500mg Test' in html
    assert 'View Stores' in html
    assert f"/medicine/{test_data['med_otc_id']}" in html


def test_medicine_detail_route_accessible(client, test_data):
    """Verify medicine detail route continues to function for discovered items."""
    res = client.get(f"/medicine/{test_data['med_otc_id']}")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert 'Paracetamol 500mg Test' in html


