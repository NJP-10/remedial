from django.contrib import admin
from django.utils.html import format_html
from .models import Ride, RideEvent

class RideEventInline(admin.TabularInline):
    model = RideEvent
    extra = 0
    readonly_fields = ('created_at',)
    can_delete = False  # Prevent deletion of events
    ordering = ['-created_at']

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_customer', 'get_rider', 'get_locations', 'get_price', 'get_status_badge', 'created_at')
    list_filter = ('status', 'pickup', 'destination', 'created_at', 'rider__user_role', 'customer__user_role')
    search_fields = ('rider__username', 'rider__first_name', 'rider__last_name',
                    'customer__username', 'customer__first_name', 'customer__last_name',
                    'pickup', 'destination')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [RideEventInline]

    fieldsets = (
        ('Ride Details', {
            'fields': (('pickup', 'destination'), ('total_distance', 'price'))
        }),
        ('Users', {
            'fields': (('rider', 'customer'),)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_customer(self, obj):
        return f"{obj.customer.get_full_name()} ({obj.customer.username})"
    get_customer.short_description = 'Customer'

    def get_rider(self, obj):
        return f"{obj.rider.get_full_name()} ({obj.rider.username})"
    get_rider.short_description = 'Rider'

    def get_locations(self, obj):
        return format_html(f"From: <b>{obj.get_pickup_display()}</b><br>To: <b>{obj.get_destination_display()}</b>")
    get_locations.short_description = 'Route'

    def get_price(self, obj):
        return format_html('₱{:.2f}', obj.price)
    get_price.short_description = 'Price'

    def get_status_badge(self, obj):
        colors = {
            'PENDING': 'warning',
            'ACCEPTED': 'info',
            'ONGOING': 'primary',
            'COMPLETED': 'success',
            'CANCELLED': 'danger',
        }
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'

@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    list_display = ('ride', 'step', 'get_step_badge', 'description', 'created_at')
    list_filter = ('step', 'created_at', 'ride__status')
    search_fields = ('ride__id', 'description', 'ride__customer__username', 'ride__rider__username')
    readonly_fields = ('created_at',)

    def get_step_badge(self, obj):
        colors = {
            1: 'info',
            2: 'primary',
            3: 'warning',
            4: 'primary',
            5: 'success',
            6: 'danger',
        }
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            colors.get(obj.step, 'secondary'),
            obj.get_step_display()
        )
    get_step_badge.short_description = 'Event Type'
