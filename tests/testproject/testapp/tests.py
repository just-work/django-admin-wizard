from typing import cast

from admin_smoke.tests import AdminTests
from django.template.response import TemplateResponse

from admin_wizard.tests import AdminWizardBaseTestCase
from testproject.testapp import models, admin, forms


class MyModelAdminTestCase(AdminTests, AdminWizardBaseTestCase):
    model = models.MyModel
    model_admin = admin.MyModelAdmin
    object_name = 'obj'

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.obj = models.MyModel.objects.create(name='name')
        cls.another = models.MyModel.objects.create(name='not_changed')

    def transform_to_new(self, data: dict) -> dict:
        return data

    def test_rename_action(self):
        """ Checks action wizard form_valid handling."""
        name = admin.UpdateAction.__name__

        r = cast(TemplateResponse, self.post_admin_action(
            name, self.obj, submit=False))

        self.assertEqual(r.status_code, 200)
        form = r.context_data['form']
        self.assertIsInstance(form, forms.RenameForm)

        r = self.post_admin_action(name, self.obj, name='new_name')

        self.assertRedirects(r, self.changelist_url)

        self.assert_object_fields(
            self.obj, name='new_name')
        self.assert_object_fields(
            self.another, name='not_changed')

    def test_non_field_errors_in_action(self):
        """ Check non field errors rendering. """
        name = admin.UpdateAction.__name__

        r = self.post_admin_action(name, self.obj, name='xxx')

        self.assertIn("xxx is forbidden", r.content.decode('utf-8'))

    def test_rename_dialog(self):
        """ Checks action dialog form_valid handling."""
        r = cast(TemplateResponse, self.post_admin_url(
            'rename', self.obj, submit=False))

        self.assertEqual(r.status_code, 200)
        form = r.context_data['form']
        self.assertIsInstance(form, forms.RenameForm)

        r = self.post_admin_url('rename', self.obj, name='new_name')

        self.assertRedirects(r, self.change_url)
        self.assert_object_fields(
            self.obj, name='new_name')
        self.assert_object_fields(
            self.another, name='not_changed')

    def test_non_field_errors_in_dialog(self):
        """ Check non field errors rendering. """
        r = self.post_admin_url('rename', self.obj, name='xxx')

        self.assertIn("xxx is forbidden", r.content.decode('utf-8'))
