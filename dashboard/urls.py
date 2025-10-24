from django.urls import path
from . import views

urlpatterns = [
    path('', views.StaffDashboardView.as_view(), name='staff-dashboard'),
    path('rides/', views.StaffRideListView.as_view(), name='staff-rides'),
    path('users/', views.StaffUserListView.as_view(), name='staff-users'),
    path('users/<int:pk>/', views.StaffRideDetailView.as_view(), name='staff-user-detail'),
    path('users/<int:user_id>/add-balance/', views.add_balance, name='staff-add-balance'),
    path('users/create/', views.StaffCreateUserView.as_view(), name='staff-create-user'),
]
