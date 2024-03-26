from django import forms
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from testproject.testapp import models


class RenameForm(forms.ModelForm):
    class Meta:
        model = models.MyModel
        fields = ('name',)

    def clean(self):
        cd = self.cleaned_data
        if 'xxx' in cd['name']:
            raise ValidationError({NON_FIELD_ERRORS: ["xxx is forbidden"]})
        return cd