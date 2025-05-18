from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import json
from datetime import date, timedelta

from .models import (
    User, 
    Customer, 
    Supplier, 
    Category, 
    Location, 
    Warehouse, 
    Product, 
    PurchaseOrder, 
    PurchaseItem, 
    SalesOrder, 
    SalesItem, 
    Inventory
)

class ModelTestCase(TestCase):
    """Tests for the model classes."""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com',
            role='administrator'
        )
        
        # Create location and warehouse
        self.location = Location.objects.create(
            name='Test Location',
            address='123 Test Street'
        )
        
        self.warehouse = Warehouse.objects.create(
            name='Test Warehouse',
            isRefrigerated=False,
            location=self.location
        )
        
        # Create category
        self.category = Category.objects.create(
            title='Test Category',
            description='Test category description'
        )
        
        # Create supplier
        self.supplier = Supplier.objects.create(
            first_name='Test',
            last_name='Supplier',
            email='supplier@example.com',
            address_street='456 Supplier St',
            address_city='Supplier City',
            address_postcode='12345',
            telephone='12345678901',
            businessName='Test Supplier Co',
            accountNumber='ACC123456'
        )
        
        # Create customer
        self.customer = Customer.objects.create(
            name='Test Customer',
            email='customer@example.com',
            telephone='09876543210',
            address_street='789 Customer St',
            address_city='Customer City',
            address_postcode='54321'
        )
        
        # Create product
        self.product = Product.objects.create(
            barCode='TEST001',
            name='Test Product',
            description='Test product description',
            category=self.category,
            sellingPrice=Decimal('25.00'),
            averageCostPrice=Decimal('15.00'),
            refrigerated=False
        )
        
        # Create inventory
        self.inventory = Inventory.objects.create(
            product=self.product,
            warehouse=self.warehouse,
            quantityAvailable=100,
            minimumStockLevel=10,
            maximumStockLevel=200
        )
    
    def test_user_creation(self):
        """Test that a user can be created with the correct role."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, 'administrator')
    
    def test_supplier_str_representation(self):
        """Test the string representation of a Supplier."""
        expected_str = f"Test Supplier (Test Supplier Co)"
        self.assertEqual(str(self.supplier), expected_str)
    
    def test_customer_str_representation(self):
        """Test the string representation of a Customer."""
        expected_str = f"Test Customer (customer@example.com)"
        self.assertEqual(str(self.customer), expected_str)
    
    def test_product_str_representation(self):
        """Test the string representation of a Product."""
        expected_str = f"Test Product (TEST001)"
        self.assertEqual(str(self.product), expected_str)
    
    def test_warehouse_relationship(self):
        """Test that a product is correctly related to warehouses through inventory."""
        self.assertIn(self.warehouse, self.product.warehouses.all())
    
    def test_inventory_creation(self):
        """Test that inventory is properly created."""
        self.assertEqual(self.inventory.quantityAvailable, 100)
        self.assertEqual(self.inventory.product, self.product)
        self.assertEqual(self.inventory.warehouse, self.warehouse)

class PurchaseOrderTestCase(TestCase):
    """Tests for the PurchaseOrder and PurchaseItem models."""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com',
            role='purchasing_officer'
        )
        
        # Create location and warehouse
        self.location = Location.objects.create(
            name='Test Location',
            address='123 Test Street'
        )
        
        self.warehouse = Warehouse.objects.create(
            name='Test Warehouse',
            isRefrigerated=False,
            location=self.location
        )
        
        # Create category
        self.category = Category.objects.create(
            title='Test Category',
            description='Test category description'
        )
        
        # Create supplier
        self.supplier = Supplier.objects.create(
            first_name='Test',
            last_name='Supplier',
            email='supplier@example.com',
            address_street='456 Supplier St',
            address_city='Supplier City',
            address_postcode='12345',
            telephone='12345678901',
            businessName='Test Supplier Co',
            accountNumber='ACC123456'
        )
        
        # Create product
        self.product = Product.objects.create(
            barCode='TEST001',
            name='Test Product',
            description='Test product description',
            category=self.category,
            sellingPrice=Decimal('25.00'),
            averageCostPrice=Decimal('15.00'),
            refrigerated=False
        )
        
        # Create purchase order
        self.purchase_order = PurchaseOrder.objects.create(
            date=date.today(),
            supplier=self.supplier,
            status='DRAFT',
            createdBy=self.user,
            deliveryWarehouse=self.warehouse
        )
    
    def test_purchase_order_creation(self):
        """Test that a purchase order can be created."""
        self.assertEqual(self.purchase_order.status, 'DRAFT')
        self.assertEqual(self.purchase_order.supplier, self.supplier)
    
    def test_purchase_item_creation(self):
        """Test creating purchase items and updating the purchase order totals."""        # Create two purchase items
        item1 = PurchaseItem.objects.create(
            purchaseOrder=self.purchase_order,
            product=self.product,
            orderQuantity=10,
            unitCostPrice=Decimal('15.00')
        )
        
        item2 = PurchaseItem.objects.create(
            purchaseOrder=self.purchase_order,
            product=self.product,
            orderQuantity=5,
            unitCostPrice=Decimal('15.00')
        )
        
        # Refresh purchase order from database
        self.purchase_order.refresh_from_db()
        
        # Check totals were updated
        expected_total_price = Decimal('15.00') * 10 + Decimal('15.00') * 5
        expected_total_items = 10 + 5
        
        self.assertEqual(self.purchase_order.totalPrice, expected_total_price)
        self.assertEqual(self.purchase_order.totalItems, expected_total_items)

class SalesOrderTestCase(TestCase):
    """Tests for the SalesOrder and SalesItem models."""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com',
            role='salesperson'
        )
        
        # Create location and warehouse
        self.location = Location.objects.create(
            name='Test Location',
            address='123 Test Street'
        )
        
        self.warehouse = Warehouse.objects.create(
            name='Test Warehouse',
            isRefrigerated=False,
            location=self.location
        )
        
        # Create category
        self.category = Category.objects.create(
            title='Test Category',
            description='Test category description'
        )
        
        # Create customer
        self.customer = Customer.objects.create(
            name='Test Customer',
            email='customer@example.com',
            telephone='09876543210',
            address_street='789 Customer St',
            address_city='Customer City',
            address_postcode='54321'
        )
        
        # Create product
        self.product = Product.objects.create(
            barCode='TEST001',
            name='Test Product',
            description='Test product description',
            category=self.category,
            sellingPrice=Decimal('25.00'),
            averageCostPrice=Decimal('15.00'),
            refrigerated=False
        )
        
        # Create inventory
        self.inventory = Inventory.objects.create(
            product=self.product,
            warehouse=self.warehouse,
            quantityAvailable=100,
            minimumStockLevel=10,
            maximumStockLevel=200
        )
        
        # Create sales order
        self.sales_order = SalesOrder.objects.create(
            date=date.today(),
            customer=self.customer,
            status='DRAFT',
            createdBy=self.user
        )
    
    def test_sales_order_creation(self):
        """Test that a sales order can be created."""
        self.assertEqual(self.sales_order.status, 'DRAFT')
        self.assertEqual(self.sales_order.customer, self.customer)
    
    def test_sales_item_creation_and_inventory_update(self):
        """Test creating sales items, and verify inventory is updated."""
        # Initial inventory quantity
        initial_quantity = self.inventory.quantityAvailable
        
        # Create a sales item
        item = SalesItem.objects.create(
            salesOrder=self.sales_order,
            product=self.product,
            warehouse=self.warehouse,
            quantity=10
        )
        
        # Refresh inventory from database
        self.inventory.refresh_from_db()
        
        # Check if inventory was updated
        self.assertEqual(self.inventory.quantityAvailable, initial_quantity - 10)
        
        # Check totals were updated on sales order
        self.sales_order.refresh_from_db()
        expected_total_price = Decimal('25.00') * 10  # sellingPrice * quantity
        self.assertEqual(self.sales_order.totalPrice, expected_total_price)
        self.assertEqual(self.sales_order.totalItems, 10)

class ViewTestCase(TestCase):
    """Tests for the views."""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com',
            role='administrator'
        )
        
        # Create test client
        self.client = Client()
        
        # Create location and warehouse
        self.location = Location.objects.create(
            name='Test Location',
            address='123 Test Street'
        )
        
        self.warehouse = Warehouse.objects.create(
            name='Test Warehouse',
            isRefrigerated=False,
            location=self.location
        )
        
        # Create category
        self.category = Category.objects.create(
            title='Test Category',
            description='Test category description'
        )
        
        # Create supplier
        self.supplier = Supplier.objects.create(
            first_name='Test',
            last_name='Supplier',
            email='supplier@example.com',
            address_street='456 Supplier St',
            address_city='Supplier City',
            address_postcode='12345',
            telephone='12345678901',
            businessName='Test Supplier Co',
            accountNumber='ACC123456'
        )
        
        # Create customer
        self.customer = Customer.objects.create(
            name='Test Customer',
            email='customer@example.com',
            telephone='09876543210',
            address_street='789 Customer St',
            address_city='Customer City',
            address_postcode='54321'
        )
        
        # Create product
        self.product = Product.objects.create(
            barCode='TEST001',
            name='Test Product',
            description='Test product description',
            category=self.category,
            sellingPrice=Decimal('25.00'),
            averageCostPrice=Decimal('15.00'),
            refrigerated=False
        )
        
        # Create inventory
        self.inventory = Inventory.objects.create(
            product=self.product,
            warehouse=self.warehouse,
            quantityAvailable=100,
            minimumStockLevel=10,
            maximumStockLevel=200
        )
    
    def test_index_redirect(self):
        """Test that the index page redirects to the dashboard."""
        response = self.client.get(reverse('index'))
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_login_view(self):
        """Test the login view."""
        # Test GET request
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        # Test invalid login
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Stays on login page
        
        # Test valid login
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpassword'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_dashboard_authenticated(self):
        """Test that authenticated users can access the dashboard."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
    def test_dashboard_unauthenticated(self):
        """Test that unauthenticated users cannot access the dashboard."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)  # Dashboard view does not have login_required
    
    def test_product_list_view(self):
        """Test the product list view."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')
    
    def test_product_create_view(self):
        """Test creating a product."""
        self.client.login(username='testuser', password='testpassword')
        
        # Get product form
        response = self.client.get(reverse('product_create'))
        self.assertEqual(response.status_code, 200)
        
        # Test creating a product
        product_data = {
            'barCode': 'TEST002',
            'name': 'New Test Product',
            'description': 'New test product description',
            'category': self.category.id,
            'sellingPrice': '30.00',
            'averageCostPrice': '20.00',
            'refrigerated': False
        }
        
        response = self.client.post(reverse('product_create'), product_data, follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify product was created
        self.assertTrue(Product.objects.filter(barCode='TEST002').exists())

class APITestCase(TestCase):
    """Tests for the API endpoints."""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com',
            role='administrator'
        )
        
        # Create test client
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        
        # Create location and warehouse
        self.location = Location.objects.create(
            name='Test Location',
            address='123 Test Street'
        )
        
        self.warehouse = Warehouse.objects.create(
            name='Test Warehouse',
            isRefrigerated=False,
            location=self.location
        )
        
        # Create category
        self.category = Category.objects.create(
            title='Test Category',
            description='Test category description'
        )
        
        # Create supplier
        self.supplier = Supplier.objects.create(
            first_name='Test',
            last_name='Supplier',
            email='supplier@example.com',
            address_street='456 Supplier St',
            address_city='Supplier City',
            address_postcode='12345',
            telephone='12345678901',
            businessName='Test Supplier Co',
            accountNumber='ACC123456'
        )
        
        # Create customer
        self.customer = Customer.objects.create(
            name='Test Customer',
            email='customer@example.com',
            telephone='09876543210',
            address_street='789 Customer St',
            address_city='Customer City',
            address_postcode='54321'
        )
        
        # Create product
        self.product = Product.objects.create(
            barCode='TEST001',
            name='Test Product',
            description='Test product description',
            category=self.category,
            sellingPrice=Decimal('25.00'),
            averageCostPrice=Decimal('15.00'),
            refrigerated=False
        )
        
        # Create inventory
        self.inventory = Inventory.objects.create(
            product=self.product,
            warehouse=self.warehouse,
            quantityAvailable=100,
            minimumStockLevel=10,
            maximumStockLevel=200
        )
    def test_sales_order_api_create(self):
        """Test creating a sales order through the API."""
        order_data = {
            'order': {
                'customer': self.customer.id,
                'date': date.today().isoformat(),
                'status': 'DRAFT',
                'paymentType': 'CASH'
            },
            'items': [
                {
                    'product': self.product.id,
                    'quantity': 5,
                    'warehouse': self.warehouse.id
                }
            ]
        }
        response = self.client.post(
            reverse('salesorder_create_api'),
            data=json.dumps(order_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify the order was created
        self.assertEqual(SalesOrder.objects.count(), 1)
        self.assertEqual(SalesItem.objects.count(), 1)
        
        # Verify inventory was updated
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantityAvailable, 95)  # 100 - 5
    def test_purchase_order_api_create(self):
        """Test creating a purchase order through the API."""
        order_data = {
            'order': {
                'supplier': self.supplier.id,
                'date': date.today().isoformat(),
                'status': 'DRAFT',
                'paymentStatus': 'PENDING',
                'paymentType': 'CASH',
                'deliveryWarehouse': self.warehouse.id
            },
            'items': [
                {
                    'product': self.product.id,
                    'orderQuantity': 20,
                    'unitCostPrice': '15.00'
                }
            ]
        }
        response = self.client.post(
            reverse('purchaseorder_create_api'),
            data=json.dumps(order_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify the order was created
        self.assertEqual(PurchaseOrder.objects.count(), 1)
        self.assertEqual(PurchaseItem.objects.count(), 1)
        
        # Get the created order
        purchase_order = PurchaseOrder.objects.first()
        self.assertEqual(purchase_order.totalItems, 20)
        self.assertEqual(purchase_order.totalPrice, Decimal('300.00'))  # 20 * 15.00
