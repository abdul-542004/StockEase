from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum, F
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Category, Product, Inventory, SalesOrder, PurchaseOrder, PurchaseItem, User, Customer, Supplier, Warehouse, Location
from .forms import *
from django import forms
from datetime import date
import calendar
import json
from django.contrib.auth import logout, login, authenticate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods

import decimal

# Helper functions to check user roles

def is_admin(user):
    return user.is_authenticated and user.role == 'administrator'

def is_inventory_manager(user):
    return user.is_authenticated and user.role == 'inventory_manager'

def is_salesperson(user):
    return user.is_authenticated and user.role == 'salesperson'

def is_purchasing_manager(user):
    return user.is_authenticated and user.role == 'purchasing_manager'


# --- Authentication Views ---
def login_view(request):
    """Login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have been logged in successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html')

def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# --- User CRUD Views ---
@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all()
    return render(request, 'core/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully!')
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'core/user_form.html', {'form': form, 'title': 'Add User'})

@login_required
@user_passes_test(is_admin)
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('user_list')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'core/user_form.html', {'form': form, 'title': 'Edit User'})

@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('user_list')
    return render(request, 'core/user_confirm_delete.html', {'user': user})


# --- Category CRUD Views ---
@login_required
@user_passes_test(is_admin)
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'core/category_list.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'core/category_form.html', {'form': form, 'title': 'Add Category'})

@login_required
@user_passes_test(is_admin)
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'core/category_form.html', {'form': form, 'title': 'Edit Category'})

@login_required
@user_passes_test(is_admin)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('category_list')
    return render(request, 'core/category_confirm_delete.html', {'category': category})

# --- Warehouse CRUD Views ---
@login_required
@user_passes_test(is_admin)
def warehouse_list(request):
    warehouses = Warehouse.objects.select_related('location').all()
    return render(request, 'core/warehouse_list.html', {'warehouses': warehouses})

@login_required
@user_passes_test(is_admin)
def warehouse_create(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Warehouse created successfully!')
            return redirect('warehouse_list')
    else:
        form = WarehouseForm()
    return render(request, 'core/warehouse_form.html', {'form': form, 'title': 'Add Warehouse'})

@login_required
@user_passes_test(is_admin)
def warehouse_update(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            messages.success(request, 'Warehouse updated successfully!')
            return redirect('warehouse_list')
    else:
        form = WarehouseForm(instance=warehouse)
    return render(request, 'core/warehouse_form.html', {'form': form, 'title': 'Edit Warehouse'})

@login_required
@user_passes_test(is_admin)
def warehouse_delete(request, pk):
    warehouse = get_object_or_404(Warehouse, pk=pk)
    if request.method == 'POST':
        warehouse.delete()
        messages.success(request, 'Warehouse deleted successfully!')
        return redirect('warehouse_list')
    return render(request, 'core/warehouse_confirm_delete.html', {'warehouse': warehouse})

# --- Product CRUD Views ---
@login_required
@user_passes_test(is_admin)
def product_list(request):
    products = Product.objects.select_related('category').all()
    return render(request, 'core/product_list.html', {'products': products})

@login_required
@user_passes_test(is_admin)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
@user_passes_test(is_admin)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Edit Product'})

@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('product_list')
    return render(request, 'core/entity_confirm_delete.html', {'product': product})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    inventories = product.inventory_set.select_related('warehouse').all()
    return render(request, 'core/product_detail.html', {
        'product': product,
        'inventories': inventories,
    })

# --- Customer CRUD Views ---
@login_required
@user_passes_test(is_admin)
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'core/customer_list.html', {'customers': customers})

@login_required
@user_passes_test(is_admin)
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully!')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'core/customer_form.html', {'form': form, 'title': 'Add Customer'})

@login_required
@user_passes_test(is_admin)
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'core/customer_form.html', {'form': form, 'title': 'Edit Customer'})

@login_required
@user_passes_test(is_admin)
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('customer_list')
    return render(request, 'core/customer_confirm_delete.html', {'customer': customer})

# --- Supplier CRUD Views ---
@login_required
@user_passes_test(is_admin)
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'core/supplier_list.html', {'suppliers': suppliers})

@login_required
@user_passes_test(is_admin)
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier created successfully!')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'core/supplier_form.html', {'form': form, 'title': 'Add Supplier'})

@login_required
@user_passes_test(is_admin)
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully!')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'core/supplier_form.html', {'form': form, 'title': 'Edit Supplier'})

@login_required
@user_passes_test(is_admin)
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully!')
        return redirect('supplier_list')
    return render(request, 'core/supplier_confirm_delete.html', {'supplier': supplier})



# --- Location CRUD Views ---
@login_required
@user_passes_test(is_admin)
def location_list(request):
    locations = Location.objects.all()
    return render(request, 'core/location_list.html', {'locations': locations})

@login_required
@user_passes_test(is_admin)
def location_create(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Location created successfully!')
            return redirect('location_list')
    else:
        form = LocationForm()
    return render(request, 'core/location_form.html', {'form': form, 'title': 'Add Location'})

@login_required
@user_passes_test(is_admin)
def location_update(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, 'Location updated successfully!')
            return redirect('location_list')
    else:
        form = LocationForm(instance=location)
    return render(request, 'core/location_form.html', {'form': form, 'title': 'Edit Location'})

@login_required
@user_passes_test(is_admin)
def location_delete(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        location.delete()
        messages.success(request, 'Location deleted successfully!')
        return redirect('location_list')
    return render(request, 'core/location_confirm_delete.html', {'location': location})

# --- Inventory CRUD Views ---
@login_required
@user_passes_test(is_admin)
def inventory_list(request):
    warehouses = Warehouse.objects.all()
    selected_warehouse = None
    query = request.GET.get('q', '').strip()
    warehouse_id = request.GET.get('warehouse', '')

    inventory_qs = Inventory.objects.select_related('product', 'warehouse')
    if warehouse_id:
        try:
            selected_warehouse = Warehouse.objects.get(id=warehouse_id)
            inventory_qs = inventory_qs.filter(warehouse=selected_warehouse)
        except Warehouse.DoesNotExist:
            selected_warehouse = None
    if query:
        inventory_qs = inventory_qs.filter(product__name__icontains=query)
    inventory_qs = inventory_qs.order_by('warehouse__name', 'product__name')

    context = {
        'warehouses': warehouses,
        'selected_warehouse': selected_warehouse,
        'inventory_list': inventory_qs,
        'query': query,
    }
    return render(request, 'core/inventory_list.html', context)

# --- Sales Order CRUD Views ---
@login_required
@user_passes_test(is_admin)
def salesorder_list(request):
    query = request.GET.get('q', '').strip()
    sales_orders = SalesOrder.objects.select_related('customer').all()
    if query:
        sales_orders = sales_orders.filter(customer__name__icontains=query)
    sales_orders = sales_orders.order_by('-date', '-id')
    return render(request, 'core/salesorder_list.html', {
        'sales_orders': sales_orders,
        'query': query,
    })



@login_required
@user_passes_test(is_admin)
def salesorder_detail(request, pk):
    order = get_object_or_404(SalesOrder, pk=pk)
    return render(request, 'core/salesorder_detail.html', {
        'order': order,
        'created_by': order.createdBy,
    })


@login_required
@user_passes_test(is_admin)
def salesorder_form(request, pk=None):
    if not pk:
        order = None
        items = []
        created_by = request.user
    else:
        order = get_object_or_404(SalesOrder, pk=pk)
        items = list(order.salesitem_set.select_related('product', 'warehouse').all())
        created_by = order.createdBy
    customers = list(Customer.objects.values('id', 'name', 'email'))
    warehouses = list(Warehouse.objects.values('id', 'name'))
    products = list(Product.objects.values('id', 'name', 'sellingPrice'))
    # For warehouse filtering, provide inventory info per product
    inventory = list(Inventory.objects.values('product_id', 'warehouse_id', 'quantityAvailable'))
    context = {
        'order': order,
        'items': items,
        'customers': customers,
        'warehouses': warehouses,
        'products': products,
        'inventory': inventory,
        'status_choices': SalesOrder.DELIVERY_STATUS_CHOICES,
        'payment_choices': SalesOrder.PAYMENT_CHOICES,
        'today': date.today().isoformat(),
        'created_by': created_by,
    }
    return render(request, 'core/salesorder_form.html', context)


# --- Sales Order AJAX API Endpoints ---
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def salesorder_create_api(request):
    """API endpoint to create a SalesOrder and its items via JSON."""
    try:
        data = json.loads(request.body)
        order_data = data.get('order', {})
        items_data = data.get('items', [])

        # Validate required fields
        required_fields = ['date', 'customer', 'status', 'paymentType']
        for field in required_fields:
            if not order_data.get(field):
                return JsonResponse({'success': False, 'error': f'Missing field: {field}'}, status=400)

        customer = Customer.objects.get(pk=order_data['customer'])
        so = SalesOrder.objects.create(
            date=order_data['date'],
            customer=customer,
            status=order_data['status'],
            paymentType=order_data['paymentType'],
            createdBy=request.user
        )

        # Create SalesItems
        for item in items_data:
            product = Product.objects.get(pk=item['product'])
            quantity = int(item['quantity'])
            warehouse_id = item.get('warehouse')
            if not warehouse_id:
                # Auto-assign warehouse if not provided (handled in model)
                SalesItem.objects.create(
                    salesOrder=so,
                    product=product,
                    quantity=quantity
                )
            else:
                warehouse = Warehouse.objects.get(pk=warehouse_id)
                SalesItem.objects.create(
                    salesOrder=so,
                    product=product,
                    quantity=quantity,
                    warehouse=warehouse
                )
        so.update_totals()
        return JsonResponse({'success': True, 'order_id': so.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@login_required
@require_http_methods(["PUT"])
def salesorder_update_api(request, pk):
    """API endpoint to update a SalesOrder and its items via JSON."""
    try:
        so = SalesOrder.objects.get(pk=pk)
        if so.status == 'DELIVERED':
            return JsonResponse({'success': False, 'error': 'Cannot update a delivered order.'}, status=400)
        data = json.loads(request.body)
        order_data = data.get('order', {})
        items_data = data.get('items', [])

        # Update SalesOrder fields
        for field in ['date', 'status', 'paymentType']:
            if field in order_data:
                setattr(so, field, order_data[field])
        if 'customer' in order_data:
            so.customer = Customer.objects.get(pk=order_data['customer'])
        # Do NOT update createdBy on edit
        so.save()

        # Remove all existing items and recreate
        so.salesitem_set.all().delete()
        for item in items_data:
            product = Product.objects.get(pk=item['product'])
            quantity = int(item['quantity'])
            warehouse_id = item.get('warehouse')
            if not warehouse_id:
                SalesItem.objects.create(
                    salesOrder=so,
                    product=product,
                    quantity=quantity
                )
            else:
                warehouse = Warehouse.objects.get(pk=warehouse_id)
                SalesItem.objects.create(
                    salesOrder=so,
                    product=product,
                    quantity=quantity,
                    warehouse=warehouse
                )
        so.update_totals()
        return JsonResponse({'success': True, 'order_id': so.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# --- Purchase Order CRUD Views ---


@login_required
def purchaseorder_list(request):
    """Display a list of purchase orders with filtering options."""
    queryset = PurchaseOrder.objects.all().order_by('-id')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)
        
    # Search by supplier name if provided
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(supplier__first_name__icontains=search)
    
    # Pagination
    paginator = Paginator(queryset, 10)  # Show 10 orders per page
    page = request.GET.get('page')
    
    try:
        purchase_orders = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        purchase_orders = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        purchase_orders = paginator.page(paginator.num_pages)
    
    context = {
        'purchase_orders': purchase_orders,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': purchase_orders,
        'model': PurchaseOrder,  # To access model choices in template
    }
    
    return render(request, 'core/purchaseorder_list.html', context)


@login_required
def purchaseorder_detail(request, pk):
    """Display detailed information about a specific purchase order."""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    
    # Process status change actions if submitted from the template
    if request.method == 'POST' and 'status' in request.POST:
        new_status = request.POST.get('status')
        # Validate the status transition 
        if new_status in dict(PurchaseOrder.STATUS_CHOICES):
            purchase_order.status = new_status
            purchase_order.save()
            messages.success(request, f"Purchase order status updated to {purchase_order.get_status_display()}")
            return redirect('core/purchaseorder_detail', pk=pk)
    
    context = {
        'purchase_order': purchase_order,
        'status_choices': PurchaseOrder.STATUS_CHOICES
    }
    
    return render(request, 'core/purchaseorder_detail.html', context)


@login_required
def purchaseorder_form(request, pk=None):
    """Render the PurchaseOrder create or update form (AJAX-powered)."""
    order = None
    items = []
    if pk:
        order = get_object_or_404(PurchaseOrder, pk=pk)
        items = list(order.purchaseitem_set.select_related('product').all())
    suppliers = Supplier.objects.all()
    warehouses = Warehouse.objects.all()
    # Convert products to a list of dicts for JSON serialization
    products = list(Product.objects.values('id', 'name'))
    context = {
        'order': order,
        'items': items,
        'suppliers': suppliers,
        'warehouses': warehouses,
        'products': products,
        'status_choices': PurchaseOrder.STATUS_CHOICES,
        'payment_choices': PurchaseOrder.PAYMENT_CHOICES,
        'payment_status_choices': PurchaseOrder.PAYMENT_STATUS_CHOICES,
        'today': date.today().isoformat(),
    }
    return render(request, 'core/purchaseorder_form.html', context)


def parse_decimal(val):
    try:
        return decimal.Decimal(val)
    except Exception:
        return decimal.Decimal(0)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def purchaseorder_create_api(request):
    """API endpoint to create a PurchaseOrder and its items via JSON."""
    try:
        data = json.loads(request.body)
        order_data = data.get('order', {})
        items_data = data.get('items', [])

        # Validate required fields
        required_fields = ['date', 'supplier', 'status', 'paymentStatus', 'paymentType', 'deliveryWarehouse']
        for field in required_fields:
            if not order_data.get(field):
                return JsonResponse({'success': False, 'error': f'Missing field: {field}'}, status=400)

        # Create PurchaseOrder
        supplier = Supplier.objects.get(pk=order_data['supplier'])
        warehouse = Warehouse.objects.get(pk=order_data['deliveryWarehouse'])
        po = PurchaseOrder.objects.create(
            date=order_data['date'],
            deliveryDate=order_data.get('deliveryDate'),
            supplier=supplier,
            status=order_data['status'],
            paymentStatus=order_data['paymentStatus'],
            paymentType=order_data['paymentType'],
            deliveryWarehouse=warehouse,
            createdBy=request.user
        )

        # Create PurchaseItems
        for item in items_data:
            product = Product.objects.get(pk=item['product'])
            PurchaseItem.objects.create(
                purchaseOrder=po,
                product=product,
                unitCostPrice=parse_decimal(item['unitCostPrice']),
                orderQuantity=int(item['orderQuantity'])
            )
        po.update_totals()
        return JsonResponse({'success': True, 'order_id': po.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@login_required
@require_http_methods(["PUT"])
def purchaseorder_update_api(request, pk):
    """API endpoint to update a PurchaseOrder and its items via JSON."""
    try:
        po = PurchaseOrder.objects.get(pk=pk)
        if po.status == 'RECEIVED':
            # Prevent updates to delivered orders
            return JsonResponse({'success': False, 'error': 'Cannot update a delivered order.'}, status=400)
        data = json.loads(request.body)
        order_data = data.get('order', {})
        items_data = data.get('items', [])

        # Update PurchaseOrder fields
        for field in ['date', 'deliveryDate', 'status', 'paymentStatus', 'paymentType']:
            if field in order_data:
                setattr(po, field, order_data[field])
        if 'supplier' in order_data:
            po.supplier = Supplier.objects.get(pk=order_data['supplier'])
        if 'deliveryWarehouse' in order_data:
            po.deliveryWarehouse = Warehouse.objects.get(pk=order_data['deliveryWarehouse'])
        po.save()

        # Update PurchaseItems: remove all and recreate (simple approach)
        po.purchaseitem_set.all().delete()
        for item in items_data:
            product = Product.objects.get(pk=item['product'])
            PurchaseItem.objects.create(
                purchaseOrder=po,
                product=product,
                unitCostPrice=parse_decimal(item['unitCostPrice']),
                orderQuantity=int(item['orderQuantity'])
            )
        po.update_totals()
        return JsonResponse({'success': True, 'order_id': po.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# --- Dashboard View ---

def dashboard(request):
    """Dashboard view showing key metrics and visualizations"""
    
    # Get current month and year, or from query parameters
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    # 1. Category Distribution Pie chart data
    category_distribution = list(
        Category.objects.annotate(
            product_count=Count('product')
        ).values('title', 'product_count').order_by('-product_count')
    )
    
    # Format data for chart.js
    categories = [item['title'] for item in category_distribution]
    category_counts = [item['product_count'] for item in category_distribution]
    
    # 2. Sales Activity - PENDING and DELIVERED counts
    sales_pending = SalesOrder.objects.filter(status='PENDING').count()
    sales_delivered = SalesOrder.objects.filter(status='DELIVERED').count()
    
    # 3. Inventory Summary
    # Total quantity available across all warehouses
    total_inventory = Inventory.objects.aggregate(
        total_qty=Sum('quantityAvailable')
    )['total_qty'] or 0
    
    # Items to be received (ordered but not yet received)
    to_be_received = PurchaseItem.objects.filter(
        purchaseOrder__status__in=['ORDERED', 'APPROVED']
    ).aggregate(
        total=Sum('orderQuantity')
    )['total'] or 0
    
    # Low stock items (where current quantity <= minimum stock level)
    low_stock_items = Inventory.objects.filter(
        quantityAvailable__lte=F('minimumStockLevel')
    ).select_related('product', 'warehouse')[:10]  # Limit to 10 items
    
    # 4. Purchase Order Summary for selected month
    month_name = calendar.month_name[month]
    purchase_orders_month = PurchaseOrder.objects.filter(
        date__year=year, 
        date__month=month
    )
    
    po_quantity = purchase_orders_month.aggregate(
        total_items=Sum('totalItems')
    )['total_items'] or 0
    
    po_cost = purchase_orders_month.filter(paymentStatus='PAID').aggregate(
        total_cost=Sum('totalPrice')
    )['total_cost'] or 0
    
    # 5. Sales Order Graph for selected month
    # Group by date and sum total price
    sales_by_date = SalesOrder.objects.filter(
        date__year=year, 
        date__month=month
    ).values('date').annotate(
        daily_total=Sum('totalPrice')
    ).order_by('date')
    
    # Format dates for chart.js
    sales_dates = [item['date'].strftime('%d %b') for item in sales_by_date]
    sales_amounts = [float(item['daily_total']) for item in sales_by_date]
    
    # Generate month dropdown for date filter
    months = [
        {"number": i, "name": calendar.month_name[i]} 
        for i in range(1, 13)
    ]
    
    years = list(range(today.year - 2, today.year + 1))
    
    context = {
        # Category data
        'categories_json': json.dumps(categories),
        'category_counts_json': json.dumps(category_counts),
        'category_distribution': category_distribution,
        
        # Sales activity
        'sales_pending': sales_pending,
        'sales_delivered': sales_delivered,
        
        # Inventory summary
        'total_inventory': total_inventory,
        'to_be_received': to_be_received,
        'low_stock_items': low_stock_items,
        
        # Purchase order summary
        'po_quantity': po_quantity,
        'po_cost': po_cost,
        'month_name': month_name,
        'year': year,
        
        # Sales graph data
        'sales_dates_json': json.dumps(sales_dates),
        'sales_amounts_json': json.dumps(sales_amounts),
        
        # Filter options
        'months': months,
        'years': years,
        'selected_month': month,
        'selected_year': year,
    }
    
    return render(request, 'core/dashboard.html', context)
