from django.db import models
from django.conf import settings

# Create your models here.

class Ride(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    LOCATION_CHOICES = [
        ('CLARK_MAIN', 'Clark Main Gate'),
        ('SM_CLARK', 'SM City Clark'),
        ('CLARK_PARADE', 'Clark Parade Grounds'),
        ('WIDUS_HOTEL', 'Widus Hotel & Casino'),
        ('MARQUEE_MALL', 'Marquee Mall'),
        ('CLARK_MUSEUM', 'Clark Museum'),
        ('AQUA_PLANET', 'Aqua Planet'),
        ('CLARK_AIRPORT', 'Clark International Airport'),
        ('CDC', 'Clark Development Corporation'),
        ('FONTANA', 'Fontana Leisure Park'),
        ('CLARK_SUN', 'Clark Sun Valley'),
        ('MIDORI_HOTEL', 'Midori Clark Hotel'),
        ('ROYCE_HOTEL', 'Royce Hotel & Casino'),
    ]

    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rides_as_rider',
        limit_choices_to={'user_role': 'RIDER'}
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rides_as_customer',
        limit_choices_to={'user_role': 'CUSTOMER'}
    )
    pickup = models.CharField(
        max_length=255,
        choices=LOCATION_CHOICES,
        help_text="Select pickup location"
    )
    destination = models.CharField(
        max_length=255,
        choices=LOCATION_CHOICES,
        help_text="Select destination location"
    )
    total_distance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Distance in kilometers"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price in PHP"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ride {self.id} - {self.pickup} to {self.destination} ({self.status})"

    def get_status_display_class(self):
        """Returns Bootstrap class for status badge"""
        return {
            'PENDING': 'warning',
            'ACCEPTED': 'info',
            'ONGOING': 'primary',
            'COMPLETED': 'success',
            'CANCELLED': 'danger',
        }.get(self.status, 'secondary')

class RideEvent(models.Model):
    STEP_CHOICES = [
        (1, 'Ride Requested'),
        (2, 'Rider Accepted'),
        (3, 'Rider Arrived at Pickup'),
        (4, 'Journey Started'),
        (5, 'Journey Completed'),
        (6, 'Ride Cancelled'),
    ]

    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='events'
    )
    step = models.IntegerField(
        choices=STEP_CHOICES,
        help_text="Current step in the ride process"
    )
    description = models.TextField(
        help_text="Detailed description of the event"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        get_latest_by = 'created_at'

    def __str__(self):
        return f"{self.ride} - Step {self.step}: {self.get_step_display()}"

    def save(self, *args, **kwargs):
        # Update ride status based on step if no description is provided
        if not self.description:
            self.description = self.get_step_display()

        # Update the ride status based on the event step
        status_mapping = {
            1: 'PENDING',
            2: 'ACCEPTED',
            3: 'ACCEPTED',
            4: 'ONGOING',
            5: 'COMPLETED',
            6: 'CANCELLED',
        }
        if self.ride.status != status_mapping.get(self.step, self.ride.status):
            self.ride.status = status_mapping.get(self.step, self.ride.status)
            self.ride.save()

        super().save(*args, **kwargs)
