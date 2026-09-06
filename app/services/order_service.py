from typing import Optional, Tuple, List, Dict, Any
from app.extensions import db
from app.models.order import Order, OrderItem
from app.models.medicine import Medicine
from app.models.pharmacy import Pharmacy
from app.models.inventory import PharmacyInventory
from app.models.request import MedicineRequest
from app.models.prescription import Prescription
from app.models.notification import Notification
from app.models.audit import AuditLog

class OrderService:
    @staticmethod
    def create_order(
        customer_id: int,
        pharmacy_id: int,
        order_type: str,
        contact_phone: str,
        items_data: List[Dict[str, Any]], # [{'medicine_id': int, 'quantity': int}]
        delivery_address: str = None,
        prescription_id: Optional[int] = None,
        customer_notes: str = None
    ) -> Tuple[Optional[Order], Optional[str]]:
        """
        Creates an order with items, checking prescription requirements and inventory.
        """
        pharmacy = db.session.get(Pharmacy, pharmacy_id)
        if not pharmacy or not pharmacy.is_active:
            return None, "Selected pharmacy is not available."

        if not items_data:
            return None, "Order must contain at least one item."

        if order_type == 'DELIVERY' and not pharmacy.supports_delivery:
            return None, "This pharmacy does not support home delivery."

        if order_type == 'DELIVERY' and not delivery_address:
            return None, "Delivery address is required for home delivery."

        # Check if any medicine in items requires prescription
        total_amount = 0.0
        if order_type == 'DELIVERY':
            total_amount += pharmacy.delivery_fee

        order_items = []
        requires_rx = False

        for item_data in items_data:
            med_id = item_data.get('medicine_id')
            qty = int(item_data.get('quantity', 1))
            if qty <= 0:
                return None, "Item quantity must be greater than 0."

            medicine = db.session.get(Medicine, med_id)
            if not medicine:
                return None, f"Medicine #{med_id} not found."

            if medicine.requires_prescription:
                requires_rx = True

            # Get price from pharmacy inventory
            inventory_item = PharmacyInventory.query.filter_by(
                pharmacy_id=pharmacy_id,
                medicine_id=med_id
            ).first()

            unit_price = inventory_item.price if inventory_item else 0.0
            subtotal = unit_price * qty
            total_amount += subtotal

            order_items.append(
                OrderItem(
                    medicine_id=med_id,
                    quantity=qty,
                    unit_price=unit_price,
                    subtotal=subtotal
                )
            )

        if requires_rx:
            if not prescription_id:
                return None, "One or more medicines in your order require a valid prescription upload."
            prescription = db.session.get(Prescription, prescription_id)
            if not prescription or prescription.customer_id != customer_id:
                return None, "Invalid prescription selected."

        order = Order(
            order_number=Order.generate_order_number(),
            customer_id=customer_id,
            pharmacy_id=pharmacy_id,
            prescription_id=prescription_id,
            order_type=order_type,
            delivery_address=delivery_address if order_type == 'DELIVERY' else None,
            contact_phone=contact_phone,
            status=Order.STATUS_PENDING,
            total_amount=round(total_amount, 2),
            customer_notes=customer_notes
        )

        db.session.add(order)
        db.session.flush()

        for oi in order_items:
            oi.order_id = order.id
            db.session.add(oi)

        # Notify Pharmacy
        notif = Notification(
            user_id=pharmacy.owner_id,
            title="New Order Received",
            message=f"New order #{order.order_number} received for {len(order_items)} items.",
            type="ORDER",
            link_url=f"/pharmacy/orders/{order.id}"
        )
        db.session.add(notif)

        db.session.commit()
        return order, None

    @staticmethod
    def transition_order_status(
        order_id: int,
        new_status: str,
        actor_user_id: int,
        notes: str = None,
        reason: str = None,
        ip_address: str = None
    ) -> Tuple[bool, str]:
        """
        Transitions an order status according to strict state machine rules.
        """
        order = db.session.get(Order, order_id)
        if not order:
            return False, "Order not found."

        old_status = order.status
        if not order.can_transition_to(new_status):
            return False, f"Invalid status transition from {old_status} to {new_status}."

        success = order.transition_to(new_status, notes=notes, reason=reason)
        if not success:
            return False, "Failed to transition order status."

        # If completed, deduct stock
        if new_status == Order.STATUS_COMPLETED:
            for item in order.items:
                inv = PharmacyInventory.query.filter_by(
                    pharmacy_id=order.pharmacy_id,
                    medicine_id=item.medicine_id
                ).first()
                if inv:
                    new_qty = max(0, inv.quantity - item.quantity)
                    inv.update_stock(quantity=new_qty)

        # Notification message for customer
        readable_status = new_status.replace('_', ' ').title()
        customer_msg = f"Your order #{order.order_number} status has been updated to: {readable_status}."
        if reason:
            customer_msg += f" Reason: {reason}"
        if notes:
            customer_msg += f" Pharmacy note: {notes}"

        notif = Notification(
            user_id=order.customer_id,
            title=f"Order {readable_status}",
            message=customer_msg,
            type="ORDER",
            link_url=f"/orders/{order.id}"
        )
        db.session.add(notif)

        # Audit log
        audit = AuditLog(
            actor_user_id=actor_user_id,
            action=f"ORDER_STATUS_{new_status}",
            target_type="Order",
            target_id=order.id,
            details=f"Status changed from {old_status} to {new_status}. Notes: {notes or 'N/A'}. Reason: {reason or 'N/A'}",
            ip_address=ip_address
        )
        db.session.add(audit)

        db.session.commit()
        return True, f"Order status updated to {readable_status}."

    # Medicine Requests
    @staticmethod
    def create_medicine_request(
        customer_id: int,
        pharmacy_id: int,
        medicine_id: int,
        quantity: int = 1,
        prescription_id: Optional[int] = None,
        notes: str = None
    ) -> Tuple[Optional[MedicineRequest], Optional[str]]:
        pharmacy = db.session.get(Pharmacy, pharmacy_id)
        if not pharmacy or not pharmacy.is_active:
            return None, "Pharmacy not available."

        medicine = db.session.get(Medicine, medicine_id)
        if not medicine:
            return None, "Medicine not found."

        if medicine.requires_prescription and not prescription_id:
            return None, "A valid prescription is required for this medicine."

        req = MedicineRequest(
            customer_id=customer_id,
            pharmacy_id=pharmacy_id,
            medicine_id=medicine_id,
            prescription_id=prescription_id,
            quantity=max(1, quantity),
            status='PENDING',
            notes=notes
        )
        db.session.add(req)

        # Notify Pharmacy
        notif = Notification(
            user_id=pharmacy.owner_id,
            title="New Medicine Availability Request",
            message=f"A customer requested availability for {medicine.name} ({medicine.strength}).",
            type="REQUEST",
            link_url="/pharmacy/requests"
        )
        db.session.add(notif)

        db.session.commit()
        return req, None

    @staticmethod
    def respond_to_request(
        request_id: int,
        status: str, # 'ACCEPTED', 'REJECTED', 'FULFILLED'
        response_text: str = None
    ) -> Tuple[bool, str]:
        req = db.session.get(MedicineRequest, request_id)
        if not req:
            return False, "Request not found."

        if status not in ('ACCEPTED', 'REJECTED', 'FULFILLED'):
            return False, "Invalid status."

        req.status = status
        req.pharmacy_response = response_text

        # Notify customer
        notif = Notification(
            user_id=req.customer_id,
            title=f"Medicine Request {status.capitalize()}",
            message=f"Your request for {req.medicine.name} was {status.lower()} by {req.pharmacy.name}. Response: {response_text or 'No comments provided.'}",
            type="REQUEST",
            link_url="/requests"
        )
        db.session.add(notif)
        db.session.commit()
        return True, f"Request marked as {status.lower()}."
