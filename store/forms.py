from django import forms
from .models import *

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']
        
class VariationAdminForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set default choices if adding a new variation
        if self.initial.get('variation_category') == 'size':
            self.fields['variation_value'].widget = forms.Select(choices=SIZE_CHOICES)
        elif self.initial.get('variation_category') == 'color':
            self.fields['variation_value'].widget = forms.Select(choices=COLOR_CHOICES)
