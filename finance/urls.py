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
    path('delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
]
