django-admin-wizard
===================


django-admin-wizard is a Django app providing helpers for django admin actions
with intermediate forms.

[![Build Status](https://github.com/just-work/django-admin-wizard/workflows/build/badge.svg?branch=master&event=push)](https://github.com/just-work/django-admin-wizard/actions?query=event%3Apush+branch%3Amaster+workflow%3Abuild)
[![codecov](https://codecov.io/gh/just-work/django-admin-wizard/branch/master/graph/badge.svg)](https://codecov.io/gh/just-work/django-admin-wizard)
[![PyPI version](https://badge.fury.io/py/django-admin-wizard.svg)](https://badge.fury.io/py/django-admin-wizard)

Description
-----------

Do you know "delete selected" action in Django-admin? This package provides 
helpers for creating such actions with intermediate forms in two lines of code.
Also, you may add a link from django admin change page to a custom form view to
perform some form-supplied action on single object.

Installation
------------

```shell script
pip install django-admin-wizard
```

Working example is in `testproject.testapp`.

1. Add application to installed apps in django settings:
    ```python
    INSTALLED_APPS.append('admin_wizard')
    ```
2. And an action to your admin:
    ```python
    from django.contrib import admin
    from admin_wizard.admin import UpdateAction
    
    from testproject.testapp import forms, models
   
   
    @admin.register(models.MyModel)
    class MyModelAdmin(admin.ModelAdmin):
        actions = [UpdateAction(form_class=forms.RenameForm)]
    ```
3. Add custom view to your admin:
    ```python
    from django.contrib import admin
    from django.urls import path
    from admin_wizard.admin import UpdateDialog
    
    from testproject.testapp import forms, models
   
   
    @admin.register(models.MyModel)
    class MyModelAdmin(admin.ModelAdmin):
   
        def get_urls(self):
            urls = [
                path('<int:pk>/rename/',
                     UpdateDialog.as_view(model_admin=self,
                                          model=models.MyModel,
                                          form_class=forms.RenameForm),
                     name='rename')
            ]
            return urls + super().get_urls()

    ```
4. Add a link to custom dialog in admin change page:
    ```python
    from django.contrib import admin
    from django.urls import reverse
    
    from testproject.testapp import models
   
  
    @admin.register(models.MyModel)
    class MyModelAdmin(admin.ModelAdmin):
       readonly_fields = ('update_obj_url',)
   
       def update_obj_url(self, obj):
           # FIXME: it's XSS, don't copy-paste
           url = reverse('admin:rename', kwargs=dict(pk=obj.pk))
           return f'<a href="{url}">Rename...</a>'
       update_obj_url.short_description = 'rename'
    ```

Now you have "rename" action in changelist and "rename" link in change view.
Enjoy :)
