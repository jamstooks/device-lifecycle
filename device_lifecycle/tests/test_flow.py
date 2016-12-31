from base import BaseTestCase

from django.core.urlresolvers import reverse

from organizations.models import Organization, OrganizationUser


class FlowTestCase(BaseTestCase):
    """
    Right now just tests the dashboard redirect view, but will eventually
    test registration as well.
    """

    def testFlow(self):
        self.client.login(**self.admin_cred)

        # a user with one org
        url = reverse('dashboard_redirect')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # a user with two orgs
        org2 = Organization.objects.create(
            name='testorg2',
            slug='testorg2'
        )
        org_user = OrganizationUser.objects.create(
            organization=org2,
            user=self.admin_user,
            is_admin=True
        )

        # a user with one org
        url = reverse('dashboard_redirect')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['organization_list']), 2)
