from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Sale, Medicine
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import Shop, Medicine, Sale, ShopAttendant
from .forms import MedicineForm, SaleForm
from .utils import check_low_inventory
from django.db.models import Sum
from datetime import datetime, timedelta

@login_required
def dashboard(request):
    if request.user.is_superuser:
        # Admin dashboard
        shops = Shop.objects.all()
        total_sales = Sale.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_medicines = Medicine.objects.count()
        recent_sales = Sale.objects.order_by('-sale_date')[:5]
        
        context = {
            'shops': shops,
            'total_sales': total_sales,
            'total_medicines': total_medicines,
            'recent_sales': recent_sales,
            'is_admin': True
        }
    else:
        # Attendant dashboard
        try:
            attendant = ShopAttendant.objects.get(user=request.user)
            shop = attendant.shop
            
            today = datetime.now()
            # Check for low inventory items
            check_low_inventory(shop)
            
            # Get recent sales for this attendant's shop
            recent_sales = Sale.objects.filter(
                shop=shop
            ).order_by('-sale_date')[:5]

            context = {
                'attendant': attendant,
                'is_admin': False,
                'recent_sales': recent_sales,
                'total_medicines': Medicine.objects.filter(shop=shop).count(),
                'total_sales': Sale.objects.filter(shop=shop).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            }
            
            # Get today's sales
            today_sales = Sale.objects.filter(
                shop=shop,
                sale_date__date=today.date()
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            
            low_stock = Medicine.objects.filter(shop=shop, stock__lt=10)
            recent_sales = Sale.objects.filter(shop=shop).order_by('-sale_date')[:5]
            
            context = {
                'shop': shop,
                'today_sales': today_sales,
                'low_stock': low_stock,
                'recent_sales': recent_sales,
                'is_admin': False
            }
        except ShopAttendant.DoesNotExist:
            return redirect('login')
    
    return render(request, 'pharmacy_app/dashboard.html', context)

@login_required
@login_required
def add_medicine(request):
    # Check if user is a shop owner
    if not request.user.is_superuser and not Shop.objects.filter(owner=request.user).exists():
        messages.error(request, 'Only shop owners can add medicines')
        return redirect('dashboard')
    try:
        if request.method == 'POST':
            form = MedicineForm(request.POST, request.FILES, user=request.user)
            if form.is_valid():
                medicine = form.save(commit=False)
                if request.user.is_superuser:
                    if 'shop' not in form.cleaned_data:
                        messages.error(request, 'Shop is required for admin users')
                        return render(request, 'pharmacy_app/add_medicine.html', {'form': form})
                    medicine.shop = form.cleaned_data['shop']
                else:
                    attendant = ShopAttendant.objects.get(user=request.user)
                    medicine.shop = attendant.shop
                medicine.save()
                messages.success(request, 'Medicine added successfully!')
                return redirect('medicines_list')
        else:
            form = MedicineForm(user=request.user)
    except ShopAttendant.DoesNotExist:
        messages.error(request, 'Shop attendant profile not found')
        return redirect('dashboard')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('dashboard')
    
    return render(request, 'pharmacy_app/add_medicine.html', {'form': form})

@login_required
def enter_sale(request, medicine_id):
    try:
        if request.method == 'POST':
            if request.user.is_superuser:
                # For superuser, we allow selection from all medicines
                form = SaleForm(request.POST, shop=None)
            else:
                attendant = ShopAttendant.objects.get(user=request.user)
                form = SaleForm(request.POST, shop=attendant.shop)
            if form.is_valid():
                # First, check if we have sufficient stock
                medicine = form.cleaned_data['medicine']
                quantity = form.cleaned_data['quantity']
                if medicine.stock < quantity:
                    messages.error(request, 'Insufficient stock!')
                    return render(request, 'pharmacy_app/enter_sale.html', {'form': form})

                sale = form.save(commit=False)
                # Set total_amount from form's cleaned data
                sale.total_amount = form.cleaned_data['total_amount']
                
                # Set shop based on user type
                if request.user.is_superuser:
                    if 'shop' not in form.cleaned_data:
                        messages.error(request, 'Shop is required for admin users')
                        return render(request, 'pharmacy_app/enter_sale.html', {'form': form})
                    sale.shop = form.cleaned_data['shop']
                else:
                    attendant = ShopAttendant.objects.get(user=request.user)
                    sale.shop = attendant.shop
                
                # Set attendant and save
                sale.attendant = request.user
                
                # Update medicine stock and save both records
                medicine.stock -= quantity
                medicine.save()
                sale.save()
                messages.success(request, 'Sale entered successfully!')
                return redirect('dashboard')
        else:
            medicine = get_object_or_404(Medicine, id=medicine_id)
            if request.user.is_superuser:
                form = SaleForm(initial={'medicine': medicine})
            else:
                attendant = ShopAttendant.objects.get(user=request.user)
                form = SaleForm(shop=attendant.shop, initial={'medicine': medicine})
        return render(request, 'pharmacy_app/enter_sale.html', {'form': form})
    except Exception as e:
        messages.error(request, str(e))
        return redirect('dashboard')

def record_sale(request):
    try:
        if request.method == 'POST':
            if request.user.is_superuser:
                # For superuser, we allow selection from all medicines
                form = SaleForm(request.POST, shop=None)
            else:
                attendant = ShopAttendant.objects.get(user=request.user)
                form = SaleForm(request.POST, shop=attendant.shop)
            if form.is_valid():
                # First, check if we have sufficient stock
                medicine = form.cleaned_data['medicine']
                quantity = form.cleaned_data['quantity']
                if medicine.stock < quantity:
                    messages.error(request, 'Insufficient stock!')
                    return render(request, 'pharmacy_app/record_sale.html', {'form': form})

                sale = form.save(commit=False)
                # Set total_amount from form's cleaned data
                sale.total_amount = form.cleaned_data['total_amount']
                
                # Set shop based on user type
                if request.user.is_superuser:
                    if 'shop' not in form.cleaned_data:
                        messages.error(request, 'Shop is required for admin users')
                        return render(request, 'pharmacy_app/record_sale.html', {'form': form})
                    sale.shop = form.cleaned_data['shop']
                else:
                    attendant = ShopAttendant.objects.get(user=request.user)
                    sale.shop = attendant.shop
                
                # Set attendant and save
                sale.attendant = request.user
                
                # Update medicine stock and save both records
                medicine.stock -= quantity
                medicine.save()
                sale.save()
                messages.success(request, 'Sale recorded successfully!')
                return redirect('dashboard')
        else:
            if request.user.is_superuser:
                form = SaleForm()
            else:
                attendant = ShopAttendant.objects.get(user=request.user)
                form = SaleForm(shop=attendant.shop)
    except ShopAttendant.DoesNotExist:
        messages.error(request, 'Shop attendant profile not found')
        return redirect('dashboard')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('dashboard')

    return render(request, 'pharmacy_app/record_sale.html', {'form': form})

@login_required
def medicines_list(request):
    if request.user.is_superuser:
        medicines = Medicine.objects.all()
    else:
        attendant = ShopAttendant.objects.get(user=request.user)
        medicines = Medicine.objects.filter(shop=attendant.shop)
    
    return render(request, 'pharmacy_app/medicines_list.html', {'medicines': medicines})

@login_required
def search_medicines(request):
    query = request.GET.get('query', '')
    try:
        if request.user.is_superuser:
            medicines = Medicine.objects.filter(name__icontains=query)
        else:
            attendant = ShopAttendant.objects.get(user=request.user)
            medicines = Medicine.objects.filter(shop=attendant.shop, name__icontains=query)
        
        medicines_data = [{'id': m.id, 'name': m.name, 'price': str(m.price)} for m in medicines[:10]]
        return JsonResponse({'medicines': medicines_data})
    except ShopAttendant.DoesNotExist:
        return JsonResponse({'error': 'Shop attendant not found'}, status=403)

@login_required
def view_sale(request, sale_id):
    # First check if the sale exists at all
    try:
        sale = Sale.objects.get(id=sale_id)
    except Sale.DoesNotExist:
        messages.error(request, f'Sale record with ID {sale_id} does not exist.')
        return redirect('dashboard')

    if request.user.is_superuser:
        # Superusers can view any sale
        pass
    else:
        # Regular users can only view sales from their shop
        try:
            shop_attendant = ShopAttendant.objects.get(user=request.user)
            if sale.shop != shop_attendant.shop:
                messages.error(request, 'You do not have permission to view sales from other shops.')
                return redirect('dashboard')
        except ShopAttendant.DoesNotExist:
            messages.error(request, 'Shop attendant profile not found.')
            return redirect('dashboard')
    
    return render(request, 'pharmacy_app/view_sale.html', {'sale': sale})

def sales_report(request):
    try:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        attendant_id = request.GET.get('attendant_id')
        
        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            # Default to last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        
        if request.user.is_superuser:
            if shop_id := request.GET.get('shop_id'):
                shop = Shop.objects.get(id=shop_id)
                sales_query = Sale.objects.filter(shop=shop, sale_date__range=(start_date, end_date))
                if attendant_id:
                    sales_query = sales_query.filter(attendant_id=attendant_id)
                sales = sales_query.select_related('medicine', 'shop', 'attendant')
                total_amount = sales_query.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
                shops = Shop.objects.all()
                context = {
                    'sales': sales,
                    'total_amount': total_amount,
                    'shops': shops,
                    'attendants': User.objects.filter(sale__isnull=False).distinct(),
                    'selected_shop': shop,
                    'selected_attendant': User.objects.get(id=attendant_id) if attendant_id else None,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d')
                }
            else:
                shops = Shop.objects.all()
                context = {
                    'shops': shops,
                    'attendants': User.objects.filter(sale__isnull=False).distinct(),
                    'selected_attendant': User.objects.get(id=attendant_id) if attendant_id else None,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d')
                }
        else:
            shop_attendant = ShopAttendant.objects.get(user=request.user)
            sales_query = Sale.objects.filter(
                shop=shop_attendant.shop,
                sale_date__range=(start_date, end_date)
            )
            if attendant_id:
                sales_query = sales_query.filter(attendant_id=attendant_id)
            sales = sales_query.select_related('medicine', 'shop', 'attendant')
            total_amount = sales_query.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            context = {
                'sales': sales,
                'total_amount': total_amount,
                'attendants': User.objects.filter(sale__shop=shop_attendant.shop).distinct(),
                'selected_attendant': User.objects.get(id=attendant_id) if attendant_id else None,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
        
        return render(request, 'pharmacy_app/sales_report.html', context)
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('dashboard')
    
    total_amount = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    return render(request, 'pharmacy_app/sales_report.html', {
        'sales': sales,
        'total_amount': total_amount
    })