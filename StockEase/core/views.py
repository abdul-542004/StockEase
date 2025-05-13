from django.shortcuts import render
from django.db.models import Count, Sum, F
from .models import Category, Product, Inventory, SalesOrder, PurchaseOrder, PurchaseItem
from datetime import date, datetime
import calendar
import json


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
    
    po_cost = purchase_orders_month.aggregate(
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
