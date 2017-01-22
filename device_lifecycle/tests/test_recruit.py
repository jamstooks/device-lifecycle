from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

from htmlvalidator.client import ValidatingClient

User = get_user_model()


class RecruitTestCase(TestCase):
    """
    Test recruitment
    """
    def setUp(self):
        super(RecruitTestCase, self).setUp()
        self.client = ValidatingClient()

    def testPromos(self):
        url = reverse('recruit_home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def testSubscriptions(self):
        url = reverse('join:subscribe')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 4242 * 4
