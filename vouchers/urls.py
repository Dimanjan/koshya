from django.urls import path
from . import views

urlpatterns = [
    # Frontend views
    path('', views.index_view, name='index'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('payment/', views.payment_view, name='payment'),
    
        # Authentication
        path('register/', views.register_user, name='register'),
        path('get-token/', views.get_token, name='get-token'),

    # Statistics
    path('statistics/', views.get_statistics, name='statistics'),

    # Voucher management
    path('vouchers/', views.VoucherListCreateView.as_view(), name='voucher-list-create'),
    path('vouchers/disabled/', views.get_disabled_vouchers, name='disabled-vouchers'),
    path('vouchers/sold/', views.get_sold_vouchers, name='sold-vouchers'),
    path('vouchers/<int:pk>/', views.VoucherDetailView.as_view(), name='voucher-detail'),
    path('vouchers/<int:pk>/enable/', views.enable_voucher, name='enable-voucher'),
    path('vouchers/<int:pk>/mark-sold/', views.mark_voucher_sold, name='mark-voucher-sold'),
    path('vouchers/<str:code>/recharge/', views.recharge_voucher, name='voucher-recharge'),

    # Public payment endpoint
    path('pay/', views.make_payment, name='make-payment'),
    
    # Public balance check endpoint
    path('vouchers/<str:code>/balance/', views.check_voucher_balance, name='check-balance'),
]
