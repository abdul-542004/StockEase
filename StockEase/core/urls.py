from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False), name='index'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # User Management URLs
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_update, name='user_update'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),

    # Customer Management URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),

    # Supplier Management URLs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_update, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),

    # Category Management URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Warehouse Management URLs
    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouses/add/', views.warehouse_create, name='warehouse_create'),
    path('warehouses/<int:pk>/edit/', views.warehouse_update, name='warehouse_update'),
    path('warehouses/<int:pk>/delete/', views.warehouse_delete, name='warehouse_delete'),

    # Product Management URLs
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),

    # Location Management URLs
    path('locations/', views.location_list, name='location_list'),
    path('locations/add/', views.location_create, name='location_create'),
    path('locations/<int:pk>/edit/', views.location_update, name='location_update'),
    path('locations/<int:pk>/delete/', views.location_delete, name='location_delete'),

    # Inventory URLs
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/<int:pk>/edit/', views.inventory_edit, name='inventory_edit'),

    # Sales Order URLs
    path('salesorders/', views.salesorder_list, name='salesorder_list'),
    path('salesorders/<int:pk>/', views.salesorder_detail, name='salesorder_detail'),
    # Sales Order AJAX/API and Form URLs
    path('salesorders/add/', views.salesorder_form, name='salesorder_add'),
    path('salesorders/<int:pk>/edit/', views.salesorder_form, name='salesorder_edit'),
    path('salesorders/api/create/', views.salesorder_create_api, name='salesorder_create_api'),
    path('salesorders/api/<int:pk>/update/', views.salesorder_update_api, name='salesorder_update_api'),

    # Purchase Order URLs
    path('purchaseorders/', views.purchaseorder_list, name='purchaseorder_list'),
    path('purchaseorders/<int:pk>/', views.purchaseorder_detail, name='purchaseorder_detail'),
    path('purchaseorders/add/', views.purchaseorder_form, name='purchaseorder_add'),
    path('purchaseorders/<int:pk>/edit/', views.purchaseorder_form, name='purchaseorder_edit'),
    # AJAX API endpoints
    path('purchaseorders/api/create/', views.purchaseorder_create_api, name='purchaseorder_create_api'),
    path('purchaseorders/api/<int:pk>/update/', views.purchaseorder_update_api, name='purchaseorder_update_api'),

    # Report URLs
    path('reports/', views.reports_index, name='reports_index'),
    path('reports/product-profitability/', views.product_profitability_report, name='product_profitability_report'),
    path('reports/top-products/', views.top_products_report, name='top_products_report'),
    path('reports/sales-purchase-dashboard/', views.sales_purchase_dashboard, name='sales_purchase_dashboard'),
]