from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Vendor, PurchaseOrder,HistoricalPerformance
from django.utils import timezone
from django.contrib.auth.models import User

class VendorAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_create_vendor(self):
        response = self.client.post('/api/vendors/', {'name': 'Vendor 1', 'contact_details': '123-456-7890', 'address': '123 Main St', 'vendor_code': 'V1'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vendor.objects.count(), 1)

    def test_get_vendor_list(self):
        Vendor.objects.create(name='Vendor 1', contact_details='123-456-7890', address='123 Main St', vendor_code='V1')
        Vendor.objects.create(name='Vendor 2', contact_details='987-654-3210', address='456 Oak St', vendor_code='V2')

        response = self.client.get('/api/vendors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_update_vendor(self):
        vendor = Vendor.objects.create(name='VendorToUpdate', contact_details='111-222-3333', address='456 Pine St', vendor_code='VTU')
        response = self.client.put(f'/api/vendors/{vendor.id}/', {'name': 'UpdatedVendor', 'contact_details': '999-888-7777', 'address': '789 Oak St', 'vendor_code': 'UPV'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_vendor = Vendor.objects.get(id=vendor.id)
        self.assertEqual(updated_vendor.name, 'UpdatedVendor')

    def test_delete_vendor(self):
        vendor = Vendor.objects.create(name='VendorToDelete', contact_details='444-555-6666', address='789 Elm St', vendor_code='VTD')
        response = self.client.delete(f'/api/vendors/{vendor.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Vendor.objects.count(), 0)

class PurchaseOrderAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_create_purchase_order(self):
        vendor = Vendor.objects.create(name='Vendor 1', contact_details='123-456-7890', address='123 Main St', vendor_code='V1')
        response = self.client.post('/api/purchase_orders/', {
            'po_number': 'PO123',
            'vendor': vendor.id,
            'order_date': timezone.now().isoformat(),
            'delivery_date': (timezone.now() + timezone.timedelta(days=7)).isoformat(),
            'items': '[{"name": "Item 1", "quantity": 10}]',  # Ensure this is a valid JSON array
            'quantity': 10,
            'status': 'pending',
            'issue_date': timezone.now().isoformat(),  # Add issue_date to satisfy the validation
        })

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PurchaseOrder.objects.count(), 1)

    def test_get_purchase_order_list(self):
        vendor = Vendor.objects.create(name='Vendor 1', contact_details='123-456-7890', address='123 Main St', vendor_code='V1')
        PurchaseOrder.objects.create(po_number='PO123', vendor=vendor, order_date=timezone.now(), delivery_date=timezone.now(), items='[{"name": "Item 1", "quantity": 5}]', quantity=5, status='pending', issue_date=timezone.now())
        PurchaseOrder.objects.create(po_number='PO456', vendor=vendor, order_date=timezone.now(), delivery_date=timezone.now(), items='[{"name": "Item 2", "quantity": 8}]', quantity=8, status='completed', issue_date=timezone.now())

        response = self.client.get('/api/purchase_orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_update_purchase_order(self):
        vendor = Vendor.objects.create(name='Vendor 1', contact_details='123-456-7890', address='123 Main St', vendor_code='V1')
        purchase_order = PurchaseOrder.objects.create(
        po_number='PO123',
        vendor=vendor,
        order_date=timezone.now(),
        delivery_date=timezone.now(),
        items='[{"name": "Item 1", "quantity": 5}]',
        quantity=5,
        status='pending',
        issue_date=timezone.now()
    )

        response = self.client.put(
            f'/api/purchase_orders/{purchase_order.id}/',
            {
                'po_number': 'PO123',
                'order_date': purchase_order.order_date.isoformat(),
                'delivery_date': purchase_order.delivery_date.isoformat(),
                'items': purchase_order.items,
                'quantity': 10,
                'status': 'pending',
                'issue_date': purchase_order.issue_date.isoformat(),
                'vendor': vendor.id,
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_purchase_order = PurchaseOrder.objects.get(id=purchase_order.id)
        self.assertEqual(updated_purchase_order.quantity, 10)


    def test_delete_purchase_order(self):
        vendor = Vendor.objects.create(name='Vendor 1', contact_details='123-456-7890', address='123 Main St', vendor_code='V1')
        purchase_order = PurchaseOrder.objects.create(po_number='PO123', vendor=vendor, order_date=timezone.now(), delivery_date=timezone.now(), items='[{"name": "Item 1", "quantity": 5}]', quantity=5, status='pending', issue_date=timezone.now())

        response = self.client.delete(f'/api/purchase_orders/{purchase_order.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PurchaseOrder.objects.count(), 0)

