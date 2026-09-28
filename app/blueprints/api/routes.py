import os
from flask import Blueprint, jsonify, request, send_file, current_app, abort
from flask_login import login_required, current_user
from app.models.medicine import Medicine
from app.models.pharmacy import Pharmacy, VerificationDocument
from app.models.inventory import PharmacyInventory
from app.models.prescription import Prescription
from app.models.order import Order
from app.services.medicine_service import MedicineService
from app.services.location_service import LocationService
from app.services.prescription_service import PrescriptionService
from app.services.notification_service import NotificationService
from app.utils.helpers import sanitize_search_query

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/medicines/search')
def search_medicines():
    query_str = sanitize_search_query(request.args.get('q', ''))
    category_id = request.args.get('category_id', type=int)
    medicines = MedicineService.search_medicines(query_str=query_str, category_id=category_id, limit=20)
    return jsonify({
        'status': 'success',
        'count': len(medicines),
        'results': [m.to_dict() for m in medicines]
    })


@api_bp.route('/medicines/suggestions')
def medicine_suggestions():
    """
    Lightweight autocomplete suggestions endpoint for fast frontend querying.
    Returns only essential display fields for live dropdown.
    """
    query_str = sanitize_search_query(request.args.get('q', ''))
    if not query_str or len(query_str) < 2:
        return jsonify({'status': 'success', 'count': 0, 'suggestions': []})

    medicines = MedicineService.search_medicines(query_str=query_str, limit=8)
    suggestions = []
    for m in medicines:
        suggestions.append({
            'id': m.id,
            'name': m.name,
            'generic_name': m.generic_name,
            'brand_name': m.brand_name,
            'strength': m.strength,
            'dosage_form': m.dosage_form,
            'requires_prescription': m.requires_prescription,
            'category_name': m.category.name if m.category else None,
            'url': f"/medicine/{m.id}"
        })

    return jsonify({
        'status': 'success',
        'count': len(suggestions),
        'suggestions': suggestions
    })


@api_bp.route('/medicines/<int:medicine_id>')
def get_medicine(medicine_id: int):
    medicine = MedicineService.get_medicine_by_id(medicine_id)
    if not medicine:
        return jsonify({'status': 'error', 'message': 'Medicine not found'}), 404
    return jsonify({'status': 'success', 'data': medicine.to_dict()})


@api_bp.route('/pharmacies/nearby')
def nearby_pharmacies():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    radius = request.args.get('radius', 50.0, type=float)
    only_verified = request.args.get('verified', '0') == '1'
    medicine_id = request.args.get('medicine_id', type=int)

    if medicine_id:
        results = LocationService.get_nearby_pharmacies_for_medicine(
            medicine_id=medicine_id,
            customer_lat=lat,
            customer_lon=lon,
            max_radius_km=radius,
            only_verified=only_verified
        )
    else:
        results = LocationService.get_all_nearby_pharmacies(
            customer_lat=lat,
            customer_lon=lon,
            max_radius_km=radius,
            only_verified=only_verified
        )

    return jsonify({
        'status': 'success',
        'count': len(results),
        'pharmacies': results
    })


@api_bp.route('/pharmacies/<int:pharmacy_id>/inventory')
def pharmacy_inventory(pharmacy_id: int):
    pharmacy = Pharmacy.query.get_or_404(pharmacy_id)
    items = PharmacyInventory.query.filter_by(pharmacy_id=pharmacy.id).all()
    return jsonify({
        'status': 'success',
        'pharmacy': pharmacy.to_dict(),
        'inventory': [i.to_dict() for i in items]
    })


@api_bp.route('/notifications/unread-count')
def unread_notifications():
    if not current_user.is_authenticated:
        return jsonify({'count': 0})
    count = NotificationService.get_unread_count(current_user.id)
    return jsonify({'count': count})


@api_bp.route('/prescriptions/<int:prescription_id>/file')
@login_required
def get_prescription_file(prescription_id: int):
    """
    Secure download/view endpoint for prescriptions.
    Never exposes direct static URLs.
    Validates access: Customer owner, Admin, or Pharmacy fulfilling order/request.
    """
    prescription = Prescription.query.get_or_404(prescription_id)
    if not PrescriptionService.can_access_prescription(prescription, current_user):
        abort(403)

    target_dir = current_app.config['PRESCRIPTIONS_DIR']
    full_path = os.path.join(target_dir, prescription.file_path)

    if not os.path.exists(full_path):
        abort(404)

    return send_file(
        full_path,
        mimetype=prescription.mime_type,
        as_attachment=False,
        download_name=prescription.original_filename
    )


@api_bp.route('/verification-docs/<int:doc_id>/file')
@login_required
def get_verification_document_file(doc_id: int):
    """
    Secure download/view endpoint for pharmacy verification documents.
    Only accessible by Admin or the Pharmacy Owner.
    """
    doc = VerificationDocument.query.get_or_404(doc_id)
    pharmacy = doc.pharmacy

    if not (current_user.is_admin or (current_user.is_pharmacy and pharmacy.owner_id == current_user.id)):
        abort(403)

    target_dir = current_app.config['VERIFICATION_DOCS_DIR']
    full_path = os.path.join(target_dir, doc.file_path)

    if not os.path.exists(full_path):
        abort(404)

    return send_file(
        full_path,
        mimetype=doc.mime_type,
        as_attachment=False,
        download_name=doc.original_filename
    )
