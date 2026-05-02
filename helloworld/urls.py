from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Books CRUD
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_create, name='book_create'),
    path('books/<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),

    # Members CRUD
    path('members/', views.member_list, name='member_list'),
    path('members/add/', views.member_create, name='member_create'),
    path('members/<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('members/<int:pk>/delete/', views.member_delete, name='member_delete'),

    # Loans
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/checkout/', views.loan_create, name='loan_create'),
    path('loans/<int:pk>/return/', views.loan_return, name='loan_return'),

    # Report
    path('report/', views.loan_report, name='loan_report'),
]
