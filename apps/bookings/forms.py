from django import forms
from django.core.exceptions import ValidationError
from datetime import date

class HotelBookingForm(forms.Form):
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-3 border rounded-xl focus:ring-2 focus:ring-red-400 bg-white shadow-sm'})
    )
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-3 border rounded-xl focus:ring-2 focus:ring-red-400 bg-white shadow-sm'})
    )
    guests = forms.IntegerField(
        min_value=1, initial=1,
        widget=forms.NumberInput(attrs={'class': 'w-full p-3 border rounded-xl focus:ring-2 focus:ring-red-400 bg-white shadow-sm'})
    )

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        # Basic Date Validations
        if check_in and check_in < date.today():
            raise ValidationError("Check-in date palaiya date-ah irukka koodathu!")
        
        if check_in and check_out and check_out <= check_in:
            raise ValidationError("Check-out date kandippa Check-in date-ku appuram thaan irukkanum!")
        
        return cleaned_data