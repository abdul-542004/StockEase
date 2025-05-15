from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.graphics.shapes import Drawing, Circle, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from django.db.models import Sum, F, Count, ExpressionWrapper, DecimalField, Q
from datetime import datetime, timedelta
from io import BytesIO
from django.http import HttpResponse
from .models import Product, PurchaseItem, SalesItem, SalesOrder, PurchaseOrder, Inventory

def get_product_profitability_data(start_date=None, end_date=None, category=None, limit=20):
    """
    Get product profitability data sorted by profit margin.
    
    Parameters:
        start_date (date): Filter data from this date
        end_date (date): Filter data to this date
        category (int): Category ID for filtering
        limit (int): Limit number of results
        
    Returns:
        List of dictionaries with product profitability data
    """
    # Filter sales based on date range
    sales_filter = {}
    purchase_filter = {}
    
    if start_date:
        sales_filter['salesOrder__date__gte'] = start_date
        purchase_filter['purchaseOrder__date__gte'] = start_date
    
    if end_date:
        sales_filter['salesOrder__date__lte'] = end_date
        purchase_filter['purchaseOrder__date__lte'] = end_date
    
    # Category filtering
    product_filter = {}
    if category:
        product_filter['category_id'] = category
    
    # Get total sales per product within the date range
    sales_data = SalesItem.objects.filter(
        **sales_filter, 
        salesOrder__status='DELIVERED'
    ).values(
        'product'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('totalAmount')
    )
    
    # Create a dictionary to easily look up sales data
    sales_dict = {item['product']: item for item in sales_data}
    
    # Get products with relevant data
    products = Product.objects.filter(**product_filter).select_related('category')
    
    result = []
    for product in products:
        # Get sales data
        sales_info = sales_dict.get(product.id, {
            'total_quantity': 0,
            'total_revenue': 0
        })
        
        quantity_sold = sales_info['total_quantity'] or 0
        revenue = sales_info['total_revenue'] or 0
        
        # Calculate costs and profit
        cost_price = float(product.averageCostPrice)
        selling_price = float(product.sellingPrice)
        total_cost = cost_price * quantity_sold
        
        # Calculate profit and margin
        profit = revenue - total_cost
        margin_percentage = (profit / revenue * 100) if revenue > 0 else 0
        
        # Add to results if product was sold
        if quantity_sold > 0:
            result.append({
                'product_id': product.id,
                'product_name': product.name,
                'category': product.category.title,
                'cost_price': cost_price,
                'selling_price': selling_price,
                'quantity_sold': quantity_sold,
                'revenue': revenue,
                'total_cost': total_cost,
                'profit': profit,
                'margin_percentage': margin_percentage
            })
    
    # Sort by profit margin (descending)
    result.sort(key=lambda x: x['profit'], reverse=True)
    
    # Limit results
    return result[:limit]

def get_top_products_data(start_date=None, end_date=None, category=None, metric='quantity', limit=10):
    """
    Get top products by quantity sold, revenue or profit.
    
    Parameters:
        start_date (date): Filter data from this date
        end_date (date): Filter data to this date
        category (int): Category ID for filtering
        metric (str): 'quantity', 'revenue', or 'profit'
        limit (int): Limit number of results
        
    Returns:
        List of dictionaries with top products data
    """
    # Filter sales based on date range
    sales_filter = {}
    
    if start_date:
        sales_filter['salesOrder__date__gte'] = start_date
    
    if end_date:
        sales_filter['salesOrder__date__lte'] = end_date
    
    # Filter by delivered status
    sales_filter['salesOrder__status'] = 'DELIVERED'
    
    # Get category filter
    products_filter = {}
    if category:
        products_filter['product__category_id'] = category
    
    # Combine filters
    combined_filters = {**sales_filter, **products_filter}
    
    # Get top products based on metric
    if metric == 'quantity':
        top_products = SalesItem.objects.filter(
            **combined_filters
        ).values(
            'product__id',
            'product__name',
            'product__category__title',
            'product__sellingPrice',
            'product__averageCostPrice'
        ).annotate(
            quantity=Sum('quantity'),
            revenue=Sum('totalAmount')
        ).order_by('-quantity')[:limit]
        
    elif metric == 'revenue':
        top_products = SalesItem.objects.filter(
            **combined_filters
        ).values(
            'product__id',
            'product__name',
            'product__category__title',
            'product__sellingPrice',
            'product__averageCostPrice'
        ).annotate(
            quantity=Sum('quantity'),
            revenue=Sum('totalAmount')
        ).order_by('-revenue')[:limit]
        
    # Process and format the data
    result = []
    for item in top_products:
        cost_price = float(item['product__averageCostPrice'])
        quantity = item['quantity']
        revenue = float(item['revenue'])
        total_cost = cost_price * quantity
        profit = revenue - total_cost
        
        result.append({
            'product_id': item['product__id'],
            'product_name': item['product__name'],
            'category': item['product__category__title'],
            'quantity': quantity,
            'revenue': revenue,
            'profit': profit
        })
    
    return result

def get_sales_purchase_dashboard_data(period='monthly', months=12):
    """
    Get sales vs purchase data for dashboard.
    
    Parameters:
        period (str): 'daily', 'weekly', or 'monthly'
        months (int): Number of months to include
        
    Returns:
        Dictionary with sales and purchase data for the dashboard
    """
    today = datetime.now().date()
    start_date = today - timedelta(days=30 * months)
    
    # Define date trunc function based on period
    if period == 'daily':
        date_trunc = 'date'
        format_string = '%Y-%m-%d'
    elif period == 'weekly':
        date_trunc = 'week'  # This will need custom handling
        format_string = 'Week %W, %Y'
    else:  # monthly
        date_trunc = 'month'
        format_string = '%b %Y'
    
    # Get sales data
    if period == 'weekly':
        # For weekly data, we need a more custom approach
        sales_data = SalesOrder.objects.filter(
            date__gte=start_date,
            status='DELIVERED'
        ).values(
            'date'
        ).annotate(
            total_amount=Sum('totalPrice')
        ).order_by('date')
        
        purchase_data = PurchaseOrder.objects.filter(
            date__gte=start_date,
            status='RECEIVED'
        ).values(
            'date'
        ).annotate(
            total_amount=Sum('totalPrice')
        ).order_by('date')
        
        # Group by week
        sales_by_week = {}
        for item in sales_data:
            date = item['date']
            year, week, _ = date.isocalendar()
            week_key = f"{year}-W{week:02d}"
            display_date = f"Week {week}, {year}"
            
            if week_key not in sales_by_week:
                sales_by_week[week_key] = {
                    'date': display_date,
                    'total': 0
                }
            sales_by_week[week_key]['total'] += float(item['total_amount'])
        
        purchases_by_week = {}
        for item in purchase_data:
            date = item['date']
            year, week, _ = date.isocalendar()
            week_key = f"{year}-W{week:02d}"
            display_date = f"Week {week}, {year}"
            
            if week_key not in purchases_by_week:
                purchases_by_week[week_key] = {
                    'date': display_date,
                    'total': 0
                }
            purchases_by_week[week_key]['total'] += float(item['total_amount'])
        
        # Convert to sorted list
        sales_result = [{'date': data['date'], 'amount': data['total']} 
                      for _, data in sorted(sales_by_week.items())]
        
        purchases_result = [{'date': data['date'], 'amount': data['total']} 
                          for _, data in sorted(purchases_by_week.items())]
    else:
        # For daily or monthly data
        sales_data = SalesOrder.objects.filter(
            date__gte=start_date,
            status='DELIVERED'
        ).extra(
            select={'trunc_date': f"date_trunc('{date_trunc}', date)"}
        ).values(
            'trunc_date'
        ).annotate(
            total_amount=Sum('totalPrice')
        ).order_by('trunc_date')
        
        purchase_data = PurchaseOrder.objects.filter(
            date__gte=start_date,
            status='RECEIVED'
        ).extra(
            select={'trunc_date': f"date_trunc('{date_trunc}', date)"}
        ).values(
            'trunc_date'
        ).annotate(
            total_amount=Sum('totalPrice')
        ).order_by('trunc_date')
        
        # Format the results
        sales_result = [
            {
                'date': item['trunc_date'].strftime(format_string),
                'amount': float(item['total_amount'])
            }
            for item in sales_data
        ]
        
        purchases_result = [
            {
                'date': item['trunc_date'].strftime(format_string),
                'amount': float(item['total_amount'])
            }
            for item in purchase_data
        ]
    
    # Calculate overview metrics
    total_sales = sum(item['amount'] for item in sales_result)
    total_purchases = sum(item['amount'] for item in purchases_result)
    profit = total_sales - total_purchases
    profit_margin = (profit / total_sales * 100) if total_sales > 0 else 0
    
    return {
        'sales_data': sales_result,
        'purchase_data': purchases_result,
        'overview': {
            'total_sales': total_sales,
            'total_purchases': total_purchases,
            'profit': profit,
            'profit_margin': profit_margin
        }
    }

def generate_product_profitability_report(start_date=None, end_date=None, category=None):
    """
    Generate a PDF report for product profitability
    """
    # Get data for the report
    profitability_data = get_product_profitability_data(start_date, end_date, category)
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="Product Profitability Report")
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Add custom styles
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.white,
        alignment=TA_CENTER
    )
    
    # Add the report title
    title = Paragraph("Product Profitability Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Add date range
    date_range = ""
    if start_date and end_date:
        date_range = f"Period: {start_date} to {end_date}"
    elif start_date:
        date_range = f"Period: From {start_date}"
    elif end_date:
        date_range = f"Period: Until {end_date}"
    else:
        date_range = "Period: All time"
        
    date_paragraph = Paragraph(date_range, styles['Normal'])
    elements.append(date_paragraph)
    elements.append(Spacer(1, 12))
    
    # Add table headers
    headers = [
        "Product", 
        "Category", 
        "Cost Price", 
        "Selling Price", 
        "Quantity Sold", 
        "Revenue", 
        "Total Cost", 
        "Profit", 
        "Margin %"
    ]
    
    # Format headers as paragraphs with the table header style
    header_paragraphs = [Paragraph(header, table_header_style) for header in headers]
    
    # Add data rows
    data = [header_paragraphs]
    
    for item in profitability_data:
        row = [
            Paragraph(item['product_name'], normal_style),
            Paragraph(item['category'], normal_style),
            f"${item['cost_price']:.2f}",
            f"${item['selling_price']:.2f}",
            f"{item['quantity_sold']}",
            f"${item['revenue']:.2f}",
            f"${item['total_cost']:.2f}",
            f"${item['profit']:.2f}",
            f"{item['margin_percentage']:.1f}%"
        ]
        data.append(row)
    
    # Create the table
    col_widths = [100, 80, 55, 55, 55, 55, 55, 55, 55]  # Adjust column widths as needed
    table = Table(data, colWidths=col_widths)
    
    # Define table style
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Right align numeric columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    # Add alternating row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
    
    # Apply the style to the table
    table.setStyle(style)
    
    # Add the table to the elements
    elements.append(table)
    elements.append(Spacer(1, 24))
    
    # Add a simple bar chart showing top 5 products by profit
    top5_by_profit = sorted(profitability_data, key=lambda x: x['profit'], reverse=True)[:5]
    
    if top5_by_profit:
        elements.append(Paragraph("Top 5 Products by Profit", heading_style))
        elements.append(Spacer(1, 12))
        
        # Create drawing for the chart
        drawing = Drawing(500, 200)
        
        # Create the chart
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 125
        bc.width = 400
        bc.data = [[item['profit'] for item in top5_by_profit]]
        bc.strokeColor = colors.black
        
        # Y-axis
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max([item['profit'] for item in top5_by_profit]) * 1.1
        bc.valueAxis.valueStep = bc.valueAxis.valueMax / 5
        bc.valueAxis.labelTextFormat = '${:.0f}'
        
        # X-axis
        bc.categoryAxis.categoryNames = [item['product_name'] for item in top5_by_profit]
        bc.categoryAxis.labels.boxAnchor = 'ne'
        bc.categoryAxis.labels.dx = 8
        bc.categoryAxis.labels.dy = -2
        bc.categoryAxis.labels.angle = 30
        
        # Add and customize the bars
        bc.bars[0].fillColor = colors.steelblue
        
        drawing.add(bc)
        elements.append(drawing)
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HTTP response with PDF content
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"product_profitability_report_{datetime.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

def generate_top_products_report(start_date=None, end_date=None, category=None, metric='quantity'):
    """
    Generate a PDF report for top products by specified metric
    """
    # Get data for the report
    top_products_data = get_top_products_data(start_date, end_date, category, metric)
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="Top Products Report")
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Add custom styles
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.white,
        alignment=TA_CENTER
    )
    
    # Determine report title based on metric
    metric_title_map = {
        'quantity': 'Top Products by Quantity Sold',
        'revenue': 'Top Products by Revenue',
        'profit': 'Top Products by Profit'
    }
    
    report_title = metric_title_map.get(metric, 'Top Products Report')
    
    # Add the report title
    title = Paragraph(report_title, title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Add date range
    date_range = ""
    if start_date and end_date:
        date_range = f"Period: {start_date} to {end_date}"
    elif start_date:
        date_range = f"Period: From {start_date}"
    elif end_date:
        date_range = f"Period: Until {end_date}"
    else:
        date_range = "Period: All time"
        
    date_paragraph = Paragraph(date_range, styles['Normal'])
    elements.append(date_paragraph)
    elements.append(Spacer(1, 12))
    
    # Add table headers based on metric
    headers = ["Product", "Category"]
    
    if metric == 'quantity':
        headers.extend(["Quantity Sold", "Revenue", "Profit"])
    elif metric == 'revenue':
        headers.extend(["Revenue", "Quantity Sold", "Profit"])
    else:  # profit
        headers.extend(["Profit", "Revenue", "Quantity Sold"])
    
    # Format headers as paragraphs with the table header style
    header_paragraphs = [Paragraph(header, table_header_style) for header in headers]
    
    # Add data rows
    data = [header_paragraphs]
    
    for item in top_products_data:
        if metric == 'quantity':
            row = [
                Paragraph(item['product_name'], normal_style),
                Paragraph(item['category'], normal_style),
                f"{item['quantity']}",
                f"${item['revenue']:.2f}",
                f"${item['profit']:.2f}"
            ]
        elif metric == 'revenue':
            row = [
                Paragraph(item['product_name'], normal_style),
                Paragraph(item['category'], normal_style),
                f"${item['revenue']:.2f}",
                f"{item['quantity']}",
                f"${item['profit']:.2f}"
            ]
        else:  # profit
            row = [
                Paragraph(item['product_name'], normal_style),
                Paragraph(item['category'], normal_style),
                f"${item['profit']:.2f}",
                f"${item['revenue']:.2f}",
                f"{item['quantity']}"
            ]
        data.append(row)
    
    # Create the table
    col_widths = [150, 100, 80, 80, 80]  # Adjust column widths as needed
    table = Table(data, colWidths=col_widths)
    
    # Define table style
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Right align numeric columns
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    # Add alternating row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
    
    # Apply the style to the table
    table.setStyle(style)
    
    # Add the table to the elements
    elements.append(table)
    elements.append(Spacer(1, 24))
    
    # Add a pie chart for visualizing the distribution
    if top_products_data:
        elements.append(Paragraph(f"Distribution of Top Products by {metric.capitalize()}", heading_style))
        elements.append(Spacer(1, 12))
        
        # Create drawing for the chart
        drawing = Drawing(500, 250)
        
        # Create the pie chart
        pie = Pie()
        pie.x = 150
        pie.y = 50
        pie.width = 200
        pie.height = 200
        
        if metric == 'quantity':
            data_values = [item['quantity'] for item in top_products_data]
        elif metric == 'revenue':
            data_values = [item['revenue'] for item in top_products_data]
        else:  # profit
            data_values = [item['profit'] for item in top_products_data]
        
        pie.data = data_values
        pie.labels = [item['product_name'][:15] + '...' if len(item['product_name']) > 15 else item['product_name'] 
                     for item in top_products_data]
        
        # Set slice colors
        pie.slices.strokeWidth = 0.5
        pie.slices[0].fillColor = colors.steelblue
        pie.slices[1].fillColor = colors.lightsteelblue
        pie.slices[2].fillColor = colors.darkblue
        pie.slices[3].fillColor = colors.blue
        pie.slices[4].fillColor = colors.lightblue
        
        drawing.add(pie)
        elements.append(drawing)
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HTTP response with PDF content
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"top_products_by_{metric}_report_{datetime.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

def generate_sales_purchase_dashboard(period='monthly', months=12):
    """
    Generate a PDF dashboard for sales vs purchases
    """
    # Get data for the dashboard
    dashboard_data = get_sales_purchase_dashboard_data(period, months)
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="Sales vs Purchases Dashboard")
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Add the report title
    title = Paragraph("Sales vs Purchases Dashboard", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Add period information
    period_text = f"Period: Last {months} months ({datetime.now().date() - timedelta(days=30 * months)} to {datetime.now().date()})"
    period_paragraph = Paragraph(period_text, normal_style)
    elements.append(period_paragraph)
    elements.append(Spacer(1, 12))
    
    # Add overview section
    elements.append(Paragraph("Financial Overview", heading_style))
    elements.append(Spacer(1, 12))
    
    # Create overview table
    overview_data = [
        ["Total Sales", f"${dashboard_data['overview']['total_sales']:.2f}"],
        ["Total Purchases", f"${dashboard_data['overview']['total_purchases']:.2f}"],
        ["Profit", f"${dashboard_data['overview']['profit']:.2f}"],
        ["Profit Margin", f"{dashboard_data['overview']['profit_margin']:.1f}%"]
    ]
    
    overview_table = Table(overview_data, colWidths=[200, 100])
    
    # Style the overview table
    overview_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),  # Right align values
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Bold headers
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # Bold total row
    ])
    
    # Apply alternating colors
    for i in range(len(overview_data)):
        if i % 2 == 0:
            overview_style.add('BACKGROUND', (0, i), (-1, i), colors.whitesmoke)
    
    overview_table.setStyle(overview_style)
    elements.append(overview_table)
    elements.append(Spacer(1, 24))
    
    # Add line chart for sales vs purchases
    elements.append(Paragraph("Sales vs Purchases Over Time", heading_style))
    elements.append(Spacer(1, 12))
    
    # Extract data for the line chart
    if dashboard_data['sales_data'] and dashboard_data['purchase_data']:
        # Collect all unique dates from both sales and purchases
        all_dates = set()
        sales_by_date = {}
        purchases_by_date = {}
        
        for item in dashboard_data['sales_data']:
            date = item['date']
            all_dates.add(date)
            sales_by_date[date] = item['amount']
        
        for item in dashboard_data['purchase_data']:
            date = item['date']
            all_dates.add(date)
            purchases_by_date[date] = item['amount']
        
        # Sort dates
        sorted_dates = sorted(all_dates)
        
        # Get values for each series, using 0 for missing dates
        sales_values = [sales_by_date.get(date, 0) for date in sorted_dates]
        purchase_values = [purchases_by_date.get(date, 0) for date in sorted_dates]
        
        # Create drawing for the chart
        drawing = Drawing(500, 250)
        
        # Create the line chart
        lc = HorizontalLineChart()
        lc.x = 50
        lc.y = 50
        lc.height = 150
        lc.width = 400
        
        # Add data to the chart
        lc.data = [sales_values, purchase_values]
        
        # Set axis properties
        lc.categoryAxis.categoryNames = sorted_dates
        lc.categoryAxis.labels.boxAnchor = 'ne'
        lc.categoryAxis.labels.dx = 8
        lc.categoryAxis.labels.dy = -2
        lc.categoryAxis.labels.angle = 30
        
        # Set value axis properties
        max_value = max(max(sales_values or [0]), max(purchase_values or [0]))
        lc.valueAxis.valueMin = 0
        lc.valueAxis.valueMax = max_value * 1.1
        lc.valueAxis.valueStep = max_value / 5
        lc.valueAxis.labelTextFormat = '${:,.0f}'
        
        # Set line colors and styles
        lc.lines[0].strokeColor = colors.blue
        lc.lines[0].strokeWidth = 3
        lc.lines[0].symbol = makeMarker('FilledCircle')
        lc.lines[0].name = 'Sales'
        
        lc.lines[1].strokeColor = colors.red
        lc.lines[1].strokeWidth = 3
        lc.lines[1].symbol = makeMarker('FilledDiamond')
        lc.lines[1].name = 'Purchases'
        
        # Add legend
        lc.lineLabelFormat = '${:,.0f}'
        lc.strokeColor = colors.black
        
        drawing.add(lc)
        elements.append(drawing)
        
        # Add a legend
        legend_table = Table([
            [Paragraph('<font color="blue">■</font>', normal_style), "Sales"],
            [Paragraph('<font color="red">■</font>', normal_style), "Purchases"],
        ], colWidths=[20, 80])
        
        legend_style = TableStyle([
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ])
        legend_table.setStyle(legend_style)
        elements.append(legend_table)
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HTTP response with PDF content
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"sales_purchases_dashboard_{datetime.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

# Helper function for the line chart markers
def makeMarker(name):
    if name == 'FilledCircle':
        return Circle(0, 0, 5, fillColor=colors.blue)
    elif name == 'FilledDiamond':
        return Rect(0, 0, 5, 5, fillColor=colors.red)
    else:
        return None
