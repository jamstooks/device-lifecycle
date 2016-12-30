from django.test import TestCase
from django.contrib.auth import get_user_model

from organizations.models import Organization, OrganizationUser
from ..apps.people.models import Person

User = get_user_model()


class BaseTestCase(TestCase):
    """
    Base fixtures:
        - Organization
            - admin user
    """
    def setUp(self):
        self.admin_cred = {'username': 'test', 'password': 'password'}
        self.admin_user = User.objects.create_user(
            first_name='test',
            last_name='test',
            email='test@example.com',
            **self.admin_cred
        )
        self.org = Organization.objects.create(
            name='testorg',
            slug='testorg'
        )
        org_user = OrganizationUser.objects.create(
            organization=self.org,
            user=self.admin_user,
            is_admin=True
        )
        self.org_url_kwargs = {'org_slug': self.org.slug}

        self.person1 = Person.objects.create(
            organization=self.org,
            name="first user",
            position="staff"
        )
        self.person2 = Person.objects.create(
            organization=self.org,
            name="second user",
            position="staff"
        )

        return super(BaseTestCase, self).setUp()
