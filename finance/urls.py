from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('add-transaction/', views.add_transaction, name='add_transaction'),
    path('add-category/', views.add_category, name='add_category'),
    path('transactions/', views.all_transactions, name='all_transactions'),
    path('statistics/', views.statistics, name='statistics'),
    path('savings-calculator/', views.savings_calculator, name='savings_calculator'),
    path('adjust-balance/', views.adjust_balance, name='adjust_balance'),
    path('delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
]
