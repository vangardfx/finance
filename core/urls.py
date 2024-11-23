from django.urls import path
from .views import (index, contact_view, dashboard_view, profile_settings_view, services,
                    profile_view, plan_detail_view, send_payment_review, 
                    plans_view,deposit_view,send_deposit_review,transaction_view,deposits_view,search_view,withdraw_view,withdrawal_view,pricing,about,referral_view, get_user_devices,
                    delete_device, transactions_api)

app_name = "core"

urlpatterns = [
    path('', index, name='index'),
    path('home/', index, name='index'),
    path('contact/', contact_view, name='contact'),
    path('plans/', pricing, name='pricing'),
    path('about/', about, name='about'),
    path('services/', services, name='services'),
    path('app/dashboard',dashboard_view, name='dashboard'),
    path('app/dashboard/',dashboard_view, name='dashboard'),
    path('app/deposit',deposit_view, name='deposit'),
    path('app/deposit/payment/',send_deposit_review, name='payment'),
    path('app/deposit/payment',send_deposit_review, name='payment'),
    path('app/profile-settings', profile_settings_view, name='profile-settings'),
    path('app/profile', profile_view, name='profile'),
    path('app/plan/<pid>/', plan_detail_view, name='plan-detail'),
    path('app/plans', plans_view, name='plans'),
    path('app/transactions', transaction_view, name='transactions'),
    path('app/deposits', deposits_view, name='deposits'),
    path('app/referrals', referral_view, name='referrals'),
    path('app/withdraw', withdraw_view, name="withdraw"),
    path('app/withdrawals', withdrawal_view, name="withdrawals"),
    path("send-payment-review/<pid>/", send_payment_review, name="send-payment-review"),
    path('search/', search_view, name='search'),
    path('api/devices/', get_user_devices, name='get_user_devices'),
    path('api/devices/delete/<int:device_id>/', delete_device, name='delete_device'),
    path('api/transactions', transactions_api, name="transaction_api"),

]
