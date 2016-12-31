from base import BaseTestCase

from django.core.urlresolvers import reverse

from ..apps.devices.models import Device
from ..apps.people.models import Person


class ReportTestCase(BaseTestCase):
    """
    Just a simple status check on all the report views
    """
    def setUp(self):
        super(ReportTestCase, self).setUp()
        self.init_two_devices()

    def testReports(self):
        self.client.login(**self.admin_cred)

        names = ['reports_summary', 'reports_age', 'replacement_timeline']

        for name in names:
            url = reverse('dashboard:%s' % name, kwargs=self.org_url_kwargs)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
