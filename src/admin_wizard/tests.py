from typing import Any, Dict

from admin_smoke.tests import AdminBaseTestCase
from django.db import models
from django.http import HttpResponse
from django.urls import reverse


class AdminWizardBaseTestCase(AdminBaseTestCase):

    def transform_to_new(self, data: dict) -> dict:
        raise NotImplementedError()

    def post_admin_action(self, action_name: str, *objects: models.Model,
                          submit_field: str = 'apply', submit: bool = True,
                          **form_data: Any) -> HttpResponse:
        """
        Performs requests on django admin action.
        * if submit is True, performs final request from intermediate page;
        * else performs initial request from changelist.
        :param submit: final/initial request flag
        :param submit_field: name of submit input field in intermediate form
        :param action_name: action name as set in ModelAdmin.actions
        :param objects: selected objects list
        :param form_data: form data passed from intermediate page
        :returns: response with results of processing form data
        """
        data: Dict[str, Any] = {
            '_selected_action': [obj.pk for obj in objects],
            'action': action_name,
            **form_data
        }
        if submit:
            data[submit_field] = submit
        return self.client.post(self.changelist_url, data=data)

    def post_admin_url(self, url_name: str, obj: models.Model,
                       submit: bool = True, **form_data: Any) -> HttpResponse:
        """ Performs requests on django admin custom view.

        * if submit, performs post request with form data;
        * else performs get request with referer set to change_url

        :param url_name: url name as defined in ModelAdmin.get_urls()
        :param obj: object for change_view url
        :param submit: final/initial request flag
        :param form_data: form data passed from intermediate page
        :returns: response with results of processing form data
        """
        if not url_name.startswith('admin:'):
            url_name = f'admin:{url_name}'
        url = reverse(url_name, kwargs=dict(pk=obj.pk))
        if submit:
            # redirect is saved in intermediate page as a hidden input for
            # RedirectForm
            form_data.update(_redirect=self.change_url)
            return self.client.post(url, HTTP_REFERER=url, data=form_data)
        else:
            return self.client.get(url, HTTP_REFERER=self.change_url)
