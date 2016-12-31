from django.test import TestCase
from django.contrib.auth import get_user_model

from organizations.models import Organization, OrganizationUser
from ..apps.people.models import Person, Settings
from ..apps.devices.models import Device, PurchaseEvent

import datetime

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
        org_settings = Settings.objects.create(organization=self.org)
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

    def init_two_devices(self):
        self.device1 = Device.objects.create(
            organization=self.org,
            status='active',
            device_type='laptop',
            manufacturer='Apple',
            model='Macbook 1',
            serial='1000',
            current_owner=self.person1,
            description="blah" * 3
        )
        self.purchase_event1 = PurchaseEvent.objects.create(
            device=self.device1,
            purchased_device=self.device1,
            date=datetime.date(year=2017, month=1, day=1)
        )
        self.device2 = Device.objects.create(
            organization=self.org,
            status='spare',
            device_type='desktop',
            manufacturer='Apple',
            model='Macbook 2',
            serial='1000',
            current_owner=self.person1,
            description="blah" * 3
        )
        self.purchase_event2 = PurchaseEvent.objects.create(
            device=self.device2,
            purchased_device=self.device2,
            date=datetime.date(year=2016, month=1, day=1)
        )
