from django import forms


class RedirectForm(forms.Form):
    _redirect = forms.CharField(widget=forms.HiddenInput, required=False)
