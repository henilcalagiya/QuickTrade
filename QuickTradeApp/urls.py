from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),  # Root URL points to login view
    path('zerodha/login/', views.zerodha_login, name='zerodha_login'),  # Zerodha login page
    path('zerodha/callback/', views.zerodha_callback, name='zerodha_callback'),
    path('fyers/login/', views.fyers_login, name='fyers_login'),  # Fyers login page
    path('fyers/auth/', views.fyers_auth_redirect, name='fyers_auth_redirect'),  # Fyers auth callback
    path('fyers/callback/', views.fyers_callback, name='fyers_callback'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout, name='logout'),
    path('place_order/', views.place_order, name='place_order'),  # Place order endpoint
    path('exit_all/', views.exit_all, name='exit_all'),  # Exit all positions endpoint
    path('get_index_price/', views.get_index_price, name='get_index_price'),  # Get index price endpoint
]
