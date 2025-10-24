from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Ride, RideEvent
from .forms import RideForm, RideEventForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class CreateRideView(LoginRequiredMixin, CreateView):
    model = Ride
    form_class = RideForm
    template_name = 'rides/ride_form.html'
    success_url = reverse_lazy('ride-list')

    def form_valid(self, form):
        form.instance.customer = self.request.user
        response = super().form_valid(form)
        # Create initial ride event
        RideEvent.objects.create(
            ride=self.object,
            step=1,  # Ride Requested
            description=f"Ride requested by {self.request.user.get_full_name()}"
        )
        messages.success(self.request, 'Ride request created successfully!')
        return response

class RideListView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = 'rides/ride_list.html'
    context_object_name = 'rides'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Filter based on user role
        if user.user_role == 'RIDER':
            return queryset.filter(rider=user)
        elif user.user_role == 'CUSTOMER':
            return queryset.filter(customer=user)
        elif user.is_staff:
            return queryset
        return Ride.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = self.request.user.user_role
        return context

class RideDetailView(LoginRequiredMixin, DetailView):
    model = Ride
    template_name = 'rides/ride_detail.html'
    context_object_name = 'ride'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Allow access if user is the rider, customer, or staff
        if user.is_staff:
            return queryset
        return queryset.filter(Q(rider=user) | Q(customer=user))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = self.object.events.all().order_by('created_at')
        return context

class UpdateRideView(LoginRequiredMixin, UpdateView):
    model = Ride
    form_class = RideForm
    template_name = 'rides/ride_form.html'
    success_url = reverse_lazy('ride-list')

    def get_queryset(self):
        # Only allow updating pending rides
        return Ride.objects.filter(status='PENDING')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Only allow customer who created the ride or staff to update
        if not (self.request.user == obj.customer or self.request.user.is_staff):
            raise PermissionError("You don't have permission to edit this ride.")
        return obj

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ride updated successfully!')
        return response

class DeleteRideView(LoginRequiredMixin, DeleteView):
    model = Ride
    template_name = 'rides/ride_confirm_delete.html'
    success_url = reverse_lazy('ride-list')

    def get_queryset(self):
        # Only allow deleting pending rides
        return Ride.objects.filter(status='PENDING')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Only allow customer who created the ride or staff to delete
        if not (self.request.user == obj.customer or self.request.user.is_staff):
            raise PermissionError("You don't have permission to delete this ride.")
        return obj

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Ride deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Additional utility views for ride status updates
@login_required
def accept_ride(request, pk):
    ride = get_object_or_404(Ride, pk=pk)
    if request.user.user_role != 'RIDER':
        messages.error(request, "Only riders can accept rides.")
        return redirect('ride-detail', pk=pk)

    if ride.status != 'PENDING':
        messages.error(request, "This ride cannot be accepted.")
        return redirect('ride-detail', pk=pk)

    ride.rider = request.user
    ride.status = 'ACCEPTED'
    ride.save()

    # Create ride accepted event
    RideEvent.objects.create(
        ride=ride,
        step=2,  # Rider Accepted
        description=f"Ride accepted by {request.user.get_full_name()}"
    )

    messages.success(request, 'Ride accepted successfully!')
    return redirect('ride-detail', pk=pk)

class RideEventDetailView(LoginRequiredMixin, DetailView):
    model = RideEvent
    template_name = 'rides/ride_event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Allow access if user is part of the ride or staff
        if user.is_staff:
            return queryset
        return queryset.filter(Q(ride__rider=user) | Q(ride__customer=user))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ride'] = self.object.ride
        return context

class UpdateRideEventView(LoginRequiredMixin, UpdateView):
    model = RideEvent
    form_class = RideEventForm
    template_name = 'rides/ride_event_form.html'

    def get_success_url(self):
        return reverse_lazy('ride-detail', kwargs={'pk': self.object.ride.pk})

    def get_queryset(self):
        # Only staff can update events
        if not self.request.user.is_staff:
            return RideEvent.objects.none()
        return RideEvent.objects.all()

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ride event updated successfully!')
        return response

class DeleteRideEventView(LoginRequiredMixin, DeleteView):
    model = RideEvent
    template_name = 'rides/ride_event_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('ride-detail', kwargs={'pk': self.object.ride.pk})

    def get_queryset(self):
        # Only staff can delete events
        if not self.request.user.is_staff:
            return RideEvent.objects.none()
        return RideEvent.objects.all()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Ride event deleted successfully!')
        return super().delete(request, *args, **kwargs)

class CustomerBookRideView(LoginRequiredMixin, CreateView):
    model = Ride
    template_name = 'rides/book_ride.html'
    fields = ['pickup', 'destination', 'price']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = Ride.LOCATION_CHOICES
        return context

    def form_valid(self, form):
        if form.cleaned_data['pickup'] == form.cleaned_data['destination']:
            messages.error(self.request, 'Pickup and destination cannot be the same location.')
            return self.form_invalid(form)

        if form.cleaned_data['price'] < 50:
            messages.error(self.request, 'Minimum price is ₱50.')
            return self.form_invalid(form)

        # Set the customer to current user
        form.instance.customer = self.request.user
        form.instance.status = 'PENDING'

        response = super().form_valid(form)

        # Create initial ride event
        RideEvent.objects.create(
            ride=self.object,
            step=1,  # Ride Requested
            description=f"Ride requested by {self.request.user.get_full_name()}"
        )

        messages.success(self.request, 'Ride request created successfully!')
        return response

    def get_success_url(self):
        return reverse_lazy('customer-active-rides')

class EditPendingRideView(LoginRequiredMixin, UpdateView):
    model = Ride
    template_name = 'rides/edit_ride.html'
    fields = ['pickup', 'destination', 'price']

    def get_queryset(self):
        # Only allow editing pending rides
        return Ride.objects.filter(
            status='PENDING',
            customer=self.request.user
        )

    def form_valid(self, form):
        if form.cleaned_data['pickup'] == form.cleaned_data['destination']:
            messages.error(self.request, 'Pickup and destination cannot be the same location.')
            return self.form_invalid(form)

        if form.cleaned_data['price'] < 50:
            messages.error(self.request, 'Minimum price is ₱50.')
            return self.form_invalid(form)

        response = super().form_valid(form)

        # Create edit event
        RideEvent.objects.create(
            ride=self.object,
            step=1,
            description=f"Ride details updated by {self.request.user.get_full_name()}"
        )

        messages.success(self.request, 'Ride details updated successfully!')
        return response

    def get_success_url(self):
        return reverse_lazy('ride-detail', kwargs={'pk': self.object.pk})

@login_required
def update_ride_status(request, pk):
    ride = get_object_or_404(Ride, pk=pk)

    # Verify permissions
    if not (request.user.is_staff or request.user == ride.rider):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    new_status = request.POST.get('status')
    if new_status not in dict(Ride.STATUS_CHOICES):
        return JsonResponse({'error': 'Invalid status'}, status=400)

    # Handle balance transfer for completed rides
    if new_status == 'COMPLETED':
        customer = ride.customer
        rider = ride.rider
        price = ride.price

        # Check if customer has sufficient balance
        if customer.balance < price:
            return JsonResponse({
                'error': 'Customer has insufficient balance for this ride.'
            }, status=400)

        # Transfer balance from customer to rider
        customer.balance -= price
        rider.balance += price

        # Save both users
        customer.save()
        rider.save()

        # Add transfer event
        RideEvent.objects.create(
            ride=ride,
            step=5,
            description=f"Payment of ₱{price} transferred from {customer.get_full_name()} to {rider.get_full_name()}"
        )

    # Map status to step number
    status_to_step = {
        'ACCEPTED': 2,
        'ONGOING': 3,
        'COMPLETED': 5,
        'CANCELLED': 6
    }

    step = status_to_step.get(new_status, 1)

    # Update ride status
    ride.status = new_status
    ride.save()

    # Create event for status change
    event = RideEvent.objects.create(
        ride=ride,
        step=step,
        description=f"Ride status updated to {ride.get_status_display()} by {request.user.get_full_name()}"
    )

    return JsonResponse({
        'status': 'success',
        'new_status': ride.get_status_display(),
        'customer_balance': customer.balance if new_status == 'COMPLETED' else None,
        'rider_balance': rider.balance if new_status == 'COMPLETED' else None,
        'event': {
            'step': event.get_step_display(),
            'description': event.description,
            'created_at': event.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    })

class CustomerRideHistoryView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = 'rides/customer_ride_history.html'
    context_object_name = 'rides'
    paginate_by = 10

    def get_queryset(self):
        return Ride.objects.filter(
            customer=self.request.user
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed_rides'] = self.get_queryset().filter(status='COMPLETED').count()
        context['cancelled_rides'] = self.get_queryset().filter(status='CANCELLED').count()
        context['total_spent'] = self.get_queryset().filter(status='COMPLETED').aggregate(
            total=models.Sum('price')
        )['total'] or 0
        return context

class RiderRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_role == 'RIDER'

class RiderDashboardView(LoginRequiredMixin, RiderRequiredMixin, ListView):
    model = Ride
    template_name = 'rides/rider_dashboard.html'
    context_object_name = 'available_rides'
    paginate_by = 10

    def get_queryset(self):
        # Get all pending rides that don't have a rider assigned
        return Ride.objects.filter(
            status='PENDING',
            rider__isnull=True
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add active rides (accepted or ongoing)
        context['active_rides'] = Ride.objects.filter(
            rider=self.request.user,
            status__in=['ACCEPTED', 'ONGOING']
        ).order_by('-created_at')

        # Add statistics
        context['total_completed'] = Ride.objects.filter(
            rider=self.request.user,
            status='COMPLETED'
        ).count()
        context['total_earnings'] = Ride.objects.filter(
            rider=self.request.user,
            status='COMPLETED'
        ).aggregate(total=models.Sum('price'))['total'] or 0

        return context

class RiderRideHistoryView(LoginRequiredMixin, RiderRequiredMixin, ListView):
    model = Ride
    template_name = 'rides/rider_history.html'
    context_object_name = 'rides'
    paginate_by = 10

    def get_queryset(self):
        return Ride.objects.filter(
            rider=self.request.user
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate statistics
        context['completed_rides'] = self.get_queryset().filter(status='COMPLETED').count()
        context['cancelled_rides'] = self.get_queryset().filter(status='CANCELLED').count()
        context['total_earnings'] = self.get_queryset().filter(
            status='COMPLETED'
        ).aggregate(total=models.Sum('price'))['total'] or 0
        context['total_distance'] = self.get_queryset().filter(
            status='COMPLETED'
        ).aggregate(total=models.Sum('total_distance'))['total'] or 0
        return context

@login_required
def drop_ride(request, pk):
    ride = get_object_or_404(Ride, pk=pk)

    # Only allow rider or customer to drop the ride
    if not (request.user == ride.rider or request.user == ride.customer):
        messages.error(request, "You don't have permission to drop this ride.")
        return redirect('ride-detail', pk=pk)

    # Only allow dropping accepted or ongoing rides
    if ride.status not in ['ACCEPTED', 'ONGOING']:
        messages.error(request, "This ride cannot be dropped at this stage.")
        return redirect('ride-detail', pk=pk)

    # Update ride status and create event
    ride.status = 'CANCELLED'
    ride.save()

    # Create event with appropriate message
    dropper_type = 'rider' if request.user == ride.rider else 'customer'
    RideEvent.objects.create(
        ride=ride,
        step=6,  # Cancelled
        description=f"Ride dropped by {dropper_type} {request.user.get_full_name()}"
    )

    messages.warning(request, 'Ride has been dropped.')

    # Redirect riders to dashboard, customers to their active rides
    if request.user == ride.rider:
        return redirect('rider-dashboard')
    return redirect('customer-active-rides')
