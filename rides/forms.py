from django import forms
from .models import Ride, RideEvent

class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['pickup', 'destination']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pickup'].widget.attrs.update({'class': 'form-control'})
        self.fields['destination'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        pickup = cleaned_data.get('pickup')
        destination = cleaned_data.get('destination')

        if pickup and destination and pickup == destination:
            raise forms.ValidationError("Pickup and destination cannot be the same location.")

class RideEventForm(forms.ModelForm):
    class Meta:
        model = RideEvent
        fields = ['step', 'description']
        widgets = {
            'step': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = True
