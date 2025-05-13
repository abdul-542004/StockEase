from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum, F
from django.core.validators import MinValueValidator


class User(AbstractUser):
    """
    Custom user model that extends the default Django user model.
    Fields:
    - username: Unique identifier for the user.
    - password: Password for the user.
    - email: Email address of the user.
    - first_name: First name of the user.
    - last_name: Last name of the user.
    - date_joined: Date when the user joined.
    - role: Role of the user in the system.
    """
    role = models.CharField(max_length=50, choices=[
        ('administrator', 'Administrator'),
        ('inventory_manager', 'Inventory Manager'),
        ('salesperson', 'Salesperson'),
        ('purchasing_officer', 'Purchasing Officer'),
    ], default='administrator')

    def __str__(self): 
        return self.username

    


# -----------------------------------------------------------------------

class Supplier(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    address_street = models.CharField(max_length=255)
    address_city = models.CharField(max_length=255)
    address_postcode = models.CharField(max_length=20)
    telephone = models.CharField(max_length=11)  
    businessName = models.CharField(max_length=255)
    accountNumber = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.businessName})"



# -----------------------------------------------------------------------

class Customer(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, default='Walk in customer')
    telephone = models.CharField(max_length=11)  
    address_street = models.CharField(max_length=255)
    address_city = models.CharField(max_length=255)
    address_postcode = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} ({self.email})"




# -----------------------------------------------------------------------
class Category(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name_plural = "Categories"



# -----------------------------------------------------------------------

class Location(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.address})"



# -----------------------------------------------------------------------

class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    isRefrigerated = models.BooleanField(default=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='warehouses')

    def __str__(self):
        return f"{self.name} ({self.location})"


# -----------------------------------------------------------------------

class Product(models.Model):
    barCode = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    expiryDate = models.DateField(null=True, blank=True)
    averageCostPrice = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        help_text="Average cost price of the product"
    )
    sellingPrice = models.DecimalField(max_digits=10, decimal_places=2)
    packedWeight = models.FloatField(blank=True, null=True)
    packedHeight = models.FloatField(blank=True, null=True)
    packedWidth = models.FloatField(blank=True, null=True)
    packedDepth = models.FloatField(blank=True, null=True)
    refrigerated = models.BooleanField(default=False)
    warehouses = models.ManyToManyField('Warehouse', through='Inventory')

    def __str__(self):
        return f"{self.name} ({self.barCode})"


# -----------------------------------------------------------------------

class PurchaseOrder(models.Model):
    date = models.DateField()
    deliveryDate = models.DateField(null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL,null=True, related_name='purchase_orders')
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('APPROVED', 'Approved'), # Approved, ready to send to supplier
        ('ORDERED', 'Ordered'), # Sent to supplier
        ('RECEIVED', 'Received'), # All items received
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('MOBILE_PAYMENT', 'Mobile Payment'),
        ('OTHER', 'Other'),

    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
    ]
    
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='DRAFT')
    totalPrice = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    totalItems = models.PositiveIntegerField(default=0, editable=False)
    createdBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    paymentStatus = models.CharField(max_length=100, default='Pending', choices=PAYMENT_STATUS_CHOICES)
    paymentType = models.CharField(max_length=100, default='Cash', choices=PAYMENT_CHOICES)
    deliveryWarehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        help_text="The warehouse where these items will be delivered"
    )

    
    def __str__(self):
        return f"Purchase Order {self.id} - {self.date}"
        
    def update_totals(self):
        """Update the order's total price and item count from its related purchase items."""
        items = self.purchaseitem_set.all()
        if items.exists():
            self.totalPrice = sum(item.totalAmount for item in items)
            self.totalItems = sum(item.orderQuantity for item in items)
            # Use update_fields to only update specific fields without triggering full save
            super().save(update_fields=["totalPrice", "totalItems"])
            
    def save(self, *args, **kwargs):
        # First save to ensure we have an ID
        is_new = self.pk is None
        old_instance = None
        
        # Get previous state if this is an existing object
        if not is_new and self.pk:
            try:
                old_instance = PurchaseOrder.objects.get(pk=self.pk)
            except PurchaseOrder.DoesNotExist:
                pass
                
        super().save(*args, **kwargs)
        
        # Skip recalculation on initial save as items won't exist yet
        if not is_new:
            # Calculate totalPrice and totalItems after items are added
            items = self.purchaseitem_set.all()
            if items.exists():
                total_price = sum(item.totalAmount for item in items)
                total_items = sum(item.orderQuantity for item in items)
                
                # Avoid infinite recursion by only updating if changed
                if self.totalPrice != total_price or self.totalItems != total_items:
                    self.totalPrice = total_price
                    self.totalItems = total_items
                    # Use update_fields to only update specific fields
                    super().save(update_fields=["totalPrice", "totalItems"])
        
        # Handle status change to RECEIVED - update inventory
        if old_instance and old_instance.status != 'RECEIVED' and self.status == 'RECEIVED':
            self.receive_items()

    def receive_items(self):
        """
        Process the receipt of items in a purchase order:
        1. Update inventory quantities
        2. Create inventory records if needed
        3. Update product average cost prices
        """
        if not self.deliveryWarehouse:
            raise ValueError("Cannot receive items without a specified delivery warehouse")
            
        purchase_items = self.purchaseitem_set.select_related('product').all()
        
        for item in purchase_items:
            product = item.product
            
            # Get or create inventory record
            inventory, created = Inventory.objects.get_or_create(
                product=product,
                warehouse=self.deliveryWarehouse,
                defaults={
                    'quantityAvailable': 0,
                    'minimumStockLevel': 5,  # Default values
                    'maximumStockLevel': 100  # Default values
                }
            )
            
            # Update inventory quantity
            old_quantity = inventory.quantityAvailable
            inventory.quantityAvailable += item.orderQuantity
            inventory.save()
            
            # Update product average cost price
            self._update_product_avg_cost(product, old_quantity, item.orderQuantity, item.unitCostPrice)
    
    def _update_product_avg_cost(self, product, old_quantity, new_quantity, new_cost):
        """
        Update the average cost price of a product using weighted average method
        Formula: ((old_qty * old_cost) + (new_qty * new_cost)) / (old_qty + new_qty)
        """
        if old_quantity == 0:
            # If this is the first purchase, just set the cost price directly
            product.averageCostPrice = new_cost
        else:
            # Calculate weighted average cost
            total_old_value = old_quantity * float(product.averageCostPrice)
            total_new_value = new_quantity * float(new_cost)
            total_quantity = old_quantity + new_quantity
            
            # Calculate new average cost price
            product.averageCostPrice = (total_old_value + total_new_value) / total_quantity
            
        product.save(update_fields=['averageCostPrice'])


# -----------------------------------------------------------------------

class PurchaseItem(models.Model):
    purchaseOrder = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    unitCostPrice = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    orderQuantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(1)])
    totalAmount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def __str__(self):
        return f"Purchase Item {self.id} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Calculate totalAmount based on unit price and quantity
        self.totalAmount = self.unitCostPrice * self.orderQuantity
        
        super().save(*args, **kwargs)
        
        # Update parent order totals
        if self.purchaseOrder:
            self.purchaseOrder.update_totals()


# -----------------------------------------------------------------------

class SalesOrder(models.Model):
    date = models.DateField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    DELIVERY_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('MOBILE_PAYMENT', 'Mobile Payment'),
        ('OTHER', 'Other'),
    ]

    status = models.CharField(max_length=100, choices=DELIVERY_STATUS_CHOICES, default='PENDING')
    totalPrice = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    createdBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    totalItems = models.PositiveIntegerField(default=0, editable=False)
    paymentType = models.CharField(max_length=100, choices=PAYMENT_CHOICES, default='CASH')

    def __str__(self):
        return f"Sales Order {self.id} - {self.date}"

    def update_totals(self):
        """Update the order's total price and item count from its related sales items."""
        items = self.salesitem_set.all()
        if items.exists():
            self.totalPrice = sum(item.totalAmount for item in items)
            self.totalItems = sum(item.quantity for item in items)
            # Use update_fields to only update specific fields without triggering full save
            super().save(update_fields=["totalPrice", "totalItems"])
            
    def save(self, *args, **kwargs):
        # First save to ensure we have an ID
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Skip recalculation on initial save as items won't exist yet
        if not is_new:
            # Calculate totalPrice and totalItems after items are added
            items = self.salesitem_set.all()
            if items.exists():
                total_price = sum(item.totalAmount for item in items)
                total_items = sum(item.quantity for item in items)
                
                # Avoid infinite recursion by only updating if changed
                if self.totalPrice != total_price or self.totalItems != total_items:
                    self.totalPrice = total_price
                    self.totalItems = total_items
                    # Use update_fields to only update specific fields
                    super().save(update_fields=["totalPrice", "totalItems"])


# -----------------------------------------------------------------------

class SalesItem(models.Model):
    salesOrder = models.ForeignKey(SalesOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE,
        null=True,  # Must remain nullable for pre-save assignment
        help_text="The warehouse from which this product will be shipped"
    )
    quantity = models.PositiveIntegerField()
    totalAmount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def __str__(self):
        return f"Sales Item {self.id} - {self.product.name}"

    def save(self, *args, **kwargs):
        # Auto-assign warehouse if not already set
        if not self.warehouse:
            # Try to find a warehouse where the product exists in inventory
            inventory = Inventory.objects.filter(product=self.product, quantityAvailable__gte=self.quantity).first()
            if not inventory:
                raise ValueError(f"No warehouse with sufficient inventory for {self.product.name}")
            self.warehouse = inventory.warehouse

        # Calculate totalAmount
        self.totalAmount = self.product.sellingPrice * self.quantity

        # Inventory check
        inventory = Inventory.objects.filter(
            product=self.product,
            warehouse=self.warehouse
        ).first()

        if inventory is None or inventory.quantityAvailable < self.quantity:
            raise ValueError(f"Insufficient inventory for {self.product.name} in {self.warehouse.name}")

        super().save(*args, **kwargs)

        # Update inventory
        inventory.quantityAvailable -= self.quantity
        inventory.save()
        
        # Update parent order totals
        if self.salesOrder:
            self.salesOrder.update_totals()


# -----------------------------------------------------------------------

class Inventory(models.Model):
    inventoryID = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantityAvailable = models.PositiveIntegerField(editable=False, default=0)
    minimumStockLevel = models.PositiveIntegerField() # Reorder level
    maximumStockLevel = models.PositiveIntegerField()

    def __str__(self):
        return f"Inventory {self.inventoryID} - {self.product.name} in {self.warehouse.name}"
    
    class Meta:
        unique_together = ('product', 'warehouse')
        verbose_name_plural = "Inventories"

