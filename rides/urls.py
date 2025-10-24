from django.urls import path
from . import views

urlpatterns = [
    # Existing URL patterns...
    path('book/', views.CustomerBookRideView.as_view(), name='create-ride'),
    path('rides/active/', views.RideListView.as_view(), name='customer-active-rides'),
    path('rides/history/', views.RideListView.as_view(), name='customer-history'),
    path('rides/<int:pk>/', views.RideDetailView.as_view(), name='ride-detail'),
    path('rides/<int:pk>/edit/', views.EditPendingRideView.as_view(), name='ride-edit'),
    path('rides/<int:pk>/delete/', views.DeleteRideView.as_view(), name='ride-delete'),
    path('rides/<int:pk>/update-status/', views.update_ride_status, name='update-ride-status'),
    path('history/', views.CustomerRideHistoryView.as_view(), name='customer-history'),
    path('rider/dashboard/', views.RiderDashboardView.as_view(), name='rider-dashboard'),
    path('rider/history/', views.RiderRideHistoryView.as_view(), name='rider-history'),
    path('rides/<int:pk>/accept/', views.accept_ride, name='accept-ride'),
    path('rides/<int:pk>/drop/', views.drop_ride, name='drop-ride'),
]
