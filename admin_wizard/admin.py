from typing import Type, Any, Dict, cast, Optional

from django import forms
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.db import models
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, UpdateView

from admin_wizard.forms import RedirectForm


def admin_url(obj: models.Model) -> str:
    # noinspection PyProtectedMember
    url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
                  kwargs={'object_id': obj.pk})
    return url


class WizardBase:
    model_admin: admin.ModelAdmin

    def get_admin_form(self, form: forms.BaseForm) -> helpers.AdminForm:
        fieldsets = [(None, {'fields': list(form.fields)})]
        admin_form = helpers.AdminForm(
            # FIXME: django-stubs bug #358
            cast(AdminPasswordChangeForm, form),
            fieldsets,
            prepopulated_fields={},
            model_admin=self.model_admin)
        return admin_form


class UpdateAction(WizardBase, FormView):
    template_name = "admin/admin_action_wizard.html"
    submit = "apply"
    summary = _("Summary")

    queryset: models.QuerySet

    def __init__(self, form_class: Type[forms.BaseForm],
                 title: str = None, short_description: str = None):
        super().__init__()
        # used as action slug in ModelAdmin.actions
        self.__name__: str = self.__class__.__name__
        self.form_class = form_class
        self.title = title or self.__name__
        self.short_description = short_description or self.title

    def __call__(self, model_admin: admin.ModelAdmin, request: HttpRequest,
                 queryset: QuerySet) -> HttpResponse:
        self.request = request
        self.queryset = queryset
        self.model_admin = model_admin
        if self.submit not in request.POST:
            # Came here from admin changelist
            return self.get(request)
        return self.post(request)

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Return the keyword arguments for instantiating the form."""
        kwargs: Dict[str, Any] = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.submit in self.request.POST:
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        cd = super().get_context_data(**kwargs)
        has_view_permission = self.model_admin.has_view_permission(self.request)
        cd.update({
            'has_view_permission': has_view_permission,
            'opts': self.model_admin.opts,
            'object_list': self.queryset,
            'title': self.title,
            'button': self.short_description,
            'summary': self.summary,
            'action': self.request.POST['action'],
            'adminform': self.get_admin_form(cd['form']),
            'media': self.model_admin.media + cd['form'].media
        })
        return cd

    def form_valid(self, form: forms.BaseForm  # type: ignore
                   ) -> Optional[HttpResponse]:
        self.queryset.update(**form.cleaned_data)
        return None


class UpdateDialog(WizardBase, UpdateView):
    template_name = "admin/admin_update_wizard.html"

    # needed for as_view() call
    model_admin: admin.ModelAdmin = None  # type: ignore

    def __init__(self, *, model_admin: admin.ModelAdmin, title: str = None,
                 short_description: str = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.model_admin = model_admin
        self.title = title or self.__class__.__name__
        self.short_description = short_description or self.title

    def get_redirect_form(self) -> RedirectForm:
        return RedirectForm(
            initial={'_redirect': self.request.META.get('HTTP_REFERER')},
            data=self.request.POST or None)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        cd = super().get_context_data(**kwargs)
        has_view_permission = self.model_admin.has_view_permission(self.request)
        cd.update({
            'has_view_permission': has_view_permission,
            'opts': self.model_admin.opts,
            'original': self.get_object(self.get_queryset()),
            'title': self.title,
            'button': self.short_description,
            'redirect_form': self.get_redirect_form(),
            'adminform': self.get_admin_form(cd['form']),
            'media': self.model_admin.media + cd['form'].media
        })
        return cd

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any
             ) -> HttpResponse:
        response = super().post(request, *args, **kwargs)
        if response is not None:
            return response
        form = self.get_redirect_form()
        if form.is_valid():
            url = form.cleaned_data['_redirect']
        else:
            url = None
        return redirect(url or admin_url(self.get_object(self.get_queryset())))

    def form_valid(self, form: forms.BaseForm) -> None:  # type: ignore

        form = cast(forms.ModelForm, form)
        form.save()
