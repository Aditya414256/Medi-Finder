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

