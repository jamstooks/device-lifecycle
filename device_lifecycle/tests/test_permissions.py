from base import BaseTestCase

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class PermissionTestCase(BaseTestCase):

    def setUp(self):
        super(PermissionTestCase, self).setUp()
        self.bugus_user_cred = {'username': 'bogus', 'password': 'password'}
        self.bogus_user = User.objects.create_user(
            first_name='bogus',
            last_name='bogus',
            email='bogus@example.com',
            **self.bugus_user_cred
        )

    def testPermissions(self):

        url = reverse('dashboard:device_list', kwargs=self.org_url_kwargs)

        # not authenticated gets redirected
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # authenticated but not authorized gets permission denied
        self.client.login(**self.bugus_user_cred)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # admin gets in
        self.client.login(**self.admin_cred)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
