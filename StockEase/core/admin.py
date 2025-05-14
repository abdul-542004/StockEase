from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Supplier, Customer, Category, Location, 
    Warehouse, Product, PurchaseOrder, PurchaseItem, 
    SalesOrder, SalesItem, Inventory
)

# Custom User Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')

# Supplier Admin
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('businessName', 'first_name', 'last_name', 'email', 'telephone')
    search_fields = ('businessName', 'first_name', 'last_name', 'email')
    list_filter = ('address_city',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'email', 'telephone')
        }),
        ('Business Details', {
            'fields': ('businessName', 'accountNumber')
        }),
        ('Address', {
            'fields': ('address_street', 'address_city', 'address_postcode')
        }),
    )

# Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'telephone', 'address_city')
    search_fields = ('name', 'email', 'telephone')
    list_filter = ('address_city',)
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'telephone')
        }),
        ('Address', {
            'fields': ('address_street', 'address_city', 'address_postcode')
        }),
    )

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)

# Location Admin
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name', 'address')

# Warehouse Admin with Location filter
@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'isRefrigerated')
    list_filter = ('isRefrigerated', 'location')
    search_fields = ('name',)

# Inventory Inline for Product
class InventoryInline(admin.TabularInline):
    model = Inventory
    extra = 1
    fields = ('warehouse',  'minimumStockLevel', 'maximumStockLevel')

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'barCode', 'category', 'sellingPrice', 'averageCostPrice', 'expiryDate', 'refrigerated')
    list_filter = ('category', 'refrigerated', 'expiryDate')
    search_fields = ('name', 'barCode', 'description')
    inlines = [InventoryInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'barCode', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('averageCostPrice', 'sellingPrice')
        }),
        ('Product Details', {
            'fields': ('expiryDate', 'refrigerated')
        }),
        ('Dimensions', {
            'fields': ('packedWeight', 'packedHeight', 'packedWidth', 'packedDepth'),
            'classes': ('collapse',)
        }),
    )

# Purchase Item Inline for Purchase Order
class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    fields = ('product', 'unitCostPrice', 'orderQuantity', 'totalAmount')
    readonly_fields = ('totalAmount',)

# Purchase Order Admin
@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'supplier', 'status', 'totalPrice', 'totalItems', 'paymentStatus')
    list_filter = ('status', 'paymentStatus', 'paymentType', 'date')
    search_fields = ('supplier__businessName', 'supplier__email')
    inlines = [PurchaseItemInline]
    readonly_fields = ('totalPrice', 'totalItems')
    fieldsets = (
        ('Order Information', {
            'fields': ('supplier', 'date', 'deliveryDate', 'status')
        }),
        ('Delivery Information', {
            'fields': ('deliveryWarehouse',)
        }),
        ('Payment Details', {
            'fields': ('paymentStatus', 'paymentType')
        }),
        ('Order Summary', {
            'fields': ('totalPrice', 'totalItems', 'createdBy')
        }),
    )

# Sales Item Inline for Sales Order
class SalesItemInline(admin.TabularInline):
    model = SalesItem
    extra = 1
    fields = ('product', 'quantity', 'totalAmount','warehouse')
    readonly_fields = ('totalAmount',)

# Sales Order Admin
@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'customer', 'status', 'totalPrice', 'totalItems', 'paymentType')
    list_filter = ('status', 'date', 'paymentType')
    search_fields = ('customer__name', 'customer__email')
    inlines = [SalesItemInline]
    readonly_fields = ('totalPrice', 'totalItems')
    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'date', 'status')
        }),
        ('Payment Information', {
            'fields': ('paymentType',)
        }),
        ('Order Summary', {
            'fields': ('totalPrice', 'totalItems', 'createdBy')
        }),
    )

# Inventory Admin
@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('inventoryID', 'product_name', 'warehouse_name',  
                   'minimumStockLevel', 'maximumStockLevel', 'stock_status')
    list_filter = ('warehouse', 'product__category')
    search_fields = ('product__name', 'warehouse__name')
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Product'
    
    def warehouse_name(self, obj):
        return obj.warehouse.name
    warehouse_name.short_description = 'Warehouse'
    
    def stock_status(self, obj):
        if obj.quantityAvailable <= obj.minimumStockLevel:
            return 'Low Stock'
        elif obj.quantityAvailable >= obj.maximumStockLevel:
            return 'Overstocked'
        else:
            return 'Normal'
    stock_status.short_description = 'Stock Status'