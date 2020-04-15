from django.contrib import admin
from django.urls import path

from admin_wizard.admin import UpdateAction, UpdateDialog
from testproject.testapp import models, forms


@admin.register(models.MyModel)
class MyModelAdmin(admin.ModelAdmin):
    actions = [UpdateAction(form_class=forms.RenameForm)]

    def get_urls(self):
        urls = [
            path('<int:pk>/rename/',
                 UpdateDialog.as_view(model_admin=self,
                                      model=models.MyModel,
                                      form_class=forms.RenameForm),
                 name='rename')
        ]
        return urls + super().get_urls()
