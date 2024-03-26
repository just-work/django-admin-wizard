from typing import List, Union, Callable, cast

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import path

from admin_wizard.admin import UpdateAction, UpdateDialog
from testproject.testapp import models, forms

Action = Callable[[admin.ModelAdmin, HttpRequest, QuerySet], None]


@admin.register(models.MyModel)
class MyModelAdmin(admin.ModelAdmin):
    actions = [cast(Action, UpdateAction(form_class=forms.RenameForm))]

    def get_urls(self):
        urls = [
            path('<int:pk>/rename/',
                 UpdateDialog.as_view(model_admin=self,
                                      model=models.MyModel,
                                      form_class=forms.RenameForm),
                 name='rename')
        ]
        return urls + super().get_urls()
