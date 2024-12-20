from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('search-medicines/', views.search_medicines, name='search_medicines'),
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='pharmacy_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('medicines/', views.medicines_list, name='medicines_list'),
    path('medicines/add/', views.add_medicine, name='add_medicine'),
    path('sales/record/', views.record_sale, name='record_sale'),
    path('sales/view/<int:sale_id>/', views.view_sale, name='view_sale'),
    path('sales/report/', views.sales_report, name='sales_report'),
    path('enter-sale/<int:medicine_id>/', views.enter_sale, name='enter_sale'),
]