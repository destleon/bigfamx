from django.conf import settings
from django.core.mail import send_mail
from .models import Medicine, Shop

def check_low_inventory(shop):
    """Check for low inventory items in a shop and send alerts."""
    low_stock_threshold = getattr(settings, 'LOW_STOCK_THRESHOLD', 10)
    low_stock_items = Medicine.objects.filter(
        shop=shop,
        stock__lte=low_stock_threshold
    )
    
    if low_stock_items.exists():
        # Prepare alert message
        message = "Low stock alert for the following items:\n\n"
        for item in low_stock_items:
            message += f"- {item.name}: {item.stock} units remaining\n"
        
        # Send email alert to shop owner
        send_mail(
            subject=f"Low Stock Alert - {shop.name}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[shop.owner.email],
            fail_silently=False,
        )
        
        return True
    return False

def generate_sales_report(shop, start_date, end_date):
    """Generate a sales report for a specific date range."""
    from django.db.models import Sum, Count
    from .models import Sale
    
    sales_data = Sale.objects.filter(
        shop=shop,
        sale_date__gte=start_date,
        sale_date__lte=end_date
    ).aggregate(
        total_sales=Sum('total_amount'),
        total_items_sold=Sum('quantity'),
        number_of_transactions=Count('id')
    )
    
    # Get top selling medicines
    top_medicines = Sale.objects.filter(
        shop=shop,
        sale_date__gte=start_date,
        sale_date__lte=end_date
    ).values('medicine__name').annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_amount')
    ).order_by('-total_quantity')[:5]
    
    return {
        'summary': sales_data,
        'top_medicines': top_medicines,
        'period': {
            'start': start_date,
            'end': end_date
        }
    }