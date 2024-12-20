from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Shop, Medicine, Sale, ShopAttendant
from .forms import MedicineForm, SaleForm
from decimal import Decimal

class PharmacyAppTests(TestCase):
    def setUp(self):
        # Create test users
        self.admin_user = User.objects.create_superuser('admin', 'admin@test.com', 'adminpass')
        self.attendant_user = User.objects.create_user('attendant', 'attendant@test.com', 'attendantpass')
        
        # Create test shop
        self.shop = Shop.objects.create(
            name='Test Shop',
            address='Test Address',
            owner=self.admin_user
        )
        
        # Create shop attendant
        self.attendant = ShopAttendant.objects.create(
            user=self.attendant_user,
            shop=self.shop
        )
        
        # Create test medicine
        self.medicine = Medicine.objects.create(
            name='Test Medicine',
            description='Test Description',
            price=Decimal('10.00'),
            stock=100,
            shop=self.shop
        )
        
        self.client = Client()

    def test_medicine_form_admin(self):
        self.client.login(username='admin', password='adminpass')
        form_data = {
            'name': 'New Medicine',
            'description': 'New Description',
            'price': '15.00',
            'stock': 50,
            'shop': self.shop.id
        }
        form = MedicineForm(data=form_data, user=self.admin_user)
        self.assertTrue(form.is_valid())

    def test_medicine_form_attendant(self):
        self.client.login(username='attendant', password='attendantpass')
        form_data = {
            'name': 'New Medicine',
            'description': 'New Description',
            'price': '15.00',
            'stock': 50
        }
        form = MedicineForm(data=form_data, user=self.attendant_user)
        self.assertTrue(form.is_valid())

    def test_sale_form_validation(self):
        # Test valid form data
        form_data = {
            'medicine': self.medicine.id,
            'quantity': 2
        }
        form = SaleForm(data=form_data, shop=self.shop)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['total_amount'], Decimal('20.00'))
        
        # Test insufficient stock
        form_data = {
            'medicine': self.medicine.id,
            'quantity': 150  # More than available stock
        }
        form = SaleForm(data=form_data, shop=self.shop)
        self.assertFalse(form.is_valid())
        
        # Test missing quantity
        form_data = {
            'medicine': self.medicine.id
        }
        form = SaleForm(data=form_data, shop=self.shop)
        self.assertFalse(form.is_valid())
        self.assertIn('Insufficient stock available', str(form.errors))

    def test_sale_creation(self):
        self.client.login(username='attendant', password='attendantpass')
        form_data = {
            'medicine': self.medicine.id,
            'quantity': 5
        }
        response = self.client.post('/record-sale/', form_data)
        self.assertEqual(Sale.objects.count(), 1)
        sale = Sale.objects.first()
        self.assertEqual(sale.total_amount, Decimal('50.00'))
        self.assertEqual(Medicine.objects.get(id=self.medicine.id).stock, 95)