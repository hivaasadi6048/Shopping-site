from django import forms

class AddToCartProductForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=30, initial=1, widget=forms.NumberInput(attrs={'style':'width:60px'}))
    inplace = forms.BooleanField(required=False, initial=True, widget=forms.HiddenInput)
