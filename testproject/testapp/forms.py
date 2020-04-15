from django import forms

from testproject.testapp import models


class RenameForm(forms.ModelForm):
    class Meta:
        model = models.MyModel
        fields = ('name',)
