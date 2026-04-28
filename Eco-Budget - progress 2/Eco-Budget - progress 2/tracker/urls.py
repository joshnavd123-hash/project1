from django.urls import path
from . import views

urlpatterns = [
    path('add-expense/', views.add_expense, name='add_expense'),
    path('add-income/', views.add_income, name='add_income'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('get-expenses/', views.get_expenses, name='get_expenses'),
    path('get-income/', views.get_income, name='get_income'),
    path('get-summary/', views.get_summary, name='get_summary'),
]
