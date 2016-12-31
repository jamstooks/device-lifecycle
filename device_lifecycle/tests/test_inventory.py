from base import BaseTestCase

from django.core.urlresolvers import reverse

from ..apps.devices.models import (
    Device, DecommissionEvent, NoteEvent, RepairEvent, PurchaseEvent,
    TransferEvent, Warranty)
from ..apps.people.models import Person

import datetime


class InventoryTestCase(BaseTestCase):
    """
    Inventory lists and filters
    """
    def setUp(self):
        super(InventoryTestCase, self).setUp()
        self.init_two_devices()

    def testInventory(self):
        self.client.login(**self.admin_cred)
        url = reverse('dashboard:device_list', kwargs=self.org_url_kwargs)

        # Base list (default is active-only)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['filter'].qs), 1)

        # test all open filters
        filter_dict = {
            'date_purchased': '',
            'device_type': '',
            'status': ''
        }
        response = self.client.get(url, filter_dict)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['filter'].qs), 2)

        # filter on status
        filter_dict = {'status': 'spare'}
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['filter'].qs), 1)

        # filter on type
        filter_dict = {'device_type': 'desktop'}
        response = self.client.get(url, filter_dict)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['filter'].qs), 1)

        # filter on year purchased
        filter_dict = {'date_purchased': str(self.purchase_event2.date.year)}
        response = self.client.get(url, filter_dict)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['filter'].qs), 1)


class DevicesTestCase(BaseTestCase):
    """
    Tests:
        devices: create, modify, delete
    """
    def testDevices(self):
        """
            create, edit, delete
        """
        self.client.login(**self.admin_cred)

        # Test creation
        url = reverse('dashboard:device_add', kwargs=self.org_url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        post_dict = {
            'status': 'active',
            'device_type': 'laptop',
            'manufacturer': 'Apple',
            'model': 'Macbook 11"',
            'serial': '2000',
            'current_owner': self.person1.id,
            'description': "blah" * 3
        }
        self.assertEqual(self.org.device_set.count(), 0)
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.org.device_set.count(), 1)

        # get new url kwargs
        device = Device.objects.get(serial='2000')
        device_kwargs = {'pk': device.pk}
        device_kwargs.update(self.org_url_kwargs)

        # test Detail view
        url = reverse('dashboard:device_detail', kwargs=device_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Test Editing
        url = reverse('dashboard:device_update', kwargs=device_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        post_dict['description'] = "blerg" * 2
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 302)
        device.refresh_from_db()
        self.assertEqual(device.description, "blerg" * 2)

        # Test deletion
        url = reverse('dashboard:device_delete', kwargs=device_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, {'confirm': 'yes'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.org.device_set.count(), 0)


class ChildTestBase(BaseTestCase):
    """
    Tests:
        events: create, modify, delete (+triggers)
    """
    def setUp(self):
        super(ChildTestBase, self).setUp()
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
        self.device_kwargs = {'pk': self.device1.pk}
        self.device_kwargs.update(self.org_url_kwargs)

    def get_create_post_dict(self):
        return NotImplemented

    def pre_create(self):
        pass

    def post_create(self, event):
        """
        Test actions that should be "triggered" after this type of event
        is saved
        """
        pass

    def create(self):
        # create event
        url = reverse(
            "dashboard:%s_add" % self.prefix, kwargs=self.device_kwargs)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        post_dict = self.get_create_post_dict()

        self.pre_create()

        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 302)
        self.device1.refresh_from_db()
        self.assertEqual(self.childClass.objects.count(), 1)

        self.post_create(self.childClass.objects.all()[0])

    def get_modify_post_dict(self):
        " simplest option is just to change the note "
        post_dict = self.get_create_post_dict()
        post_dict['notes'] = "blerg" * 2
        return post_dict

    def pre_modify(self):
        pass

    def post_modify(self, event):
        " confirm that the note changed "
        self.assertEqual(event.notes, "blerg" * 2)

    def modify(self):
        event = self.childClass.objects.all()[0]
        event_kwargs = {'child_pk': event.pk}
        event_kwargs.update(self.device_kwargs)
        url = reverse("dashboard:%s_edit" % self.prefix, kwargs=event_kwargs)

        self.pre_modify()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, self.get_modify_post_dict())
        self.assertEqual(response.status_code, 302)

        self.post_modify(self.childClass.objects.all()[0])

    def pre_delete(self):
        pass

    def post_delete(self):
        pass

    def delete(self):
        event = self.childClass.objects.all()[0]
        event_kwargs = {'child_pk': event.pk}
        event_kwargs.update(self.device_kwargs)
        url = reverse("dashboard:%s_delete" % self.prefix, kwargs=event_kwargs)

        self.pre_delete()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, {'confirm': 'yes'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.childClass.objects.count(), 0)

        self.post_delete()


class ChildTestMixin():

    def testChild(self):
        """
            create, edit, delete
        """
        self.client.login(**self.admin_cred)
        self.create()
        self.modify()
        self.delete()


class TransferEventTestCase(ChildTestBase, ChildTestMixin):
    prefix = "transfer"
    childClass = TransferEvent

    def get_create_post_dict(self):
        return {
            'date': "2017-1-1",
            'transferred_to': self.person2.pk,
            'notes': "blah" * 3
        }

    def pre_create(self):
        self.assertEqual(self.device1.current_owner, self.person1)

    def post_create(self, event):
        """
        Test actions that should be "triggered" after this type of event
        is saved
        """
        self.assertEqual(event.device.current_owner, self.person2)
        self.assertEqual(event.transferred_to, self.person2)
        self.assertEqual(event.transferred_from, self.person1)

    def get_modify_post_dict(self):
        post_dict = self.get_create_post_dict()
        post_dict['transferred_to'] = ''
        return post_dict

    def post_modify(self, event):
        self.assertEqual(event.device.current_owner, None)
        self.assertEqual(event.device.status, 'spare')
        self.assertEqual(event.transferred_to, None)
        self.assertEqual(event.transferred_from, self.person1)


class NoteEventTestCase(ChildTestBase, ChildTestMixin):
    prefix = "note"
    childClass = NoteEvent

    def get_create_post_dict(self):
        return {
            'date': "2017-1-1",
            'notes': "blah" * 3
        }


class RepairEventTestCase(ChildTestBase, ChildTestMixin):
    prefix = "repair"
    childClass = RepairEvent

    def get_create_post_dict(self):
        return {
            'date': "2017-1-1",
            'cost': '200',
            'vendor_name': "Vendor Name",
            'vendor_address': "addy",
            'notes': "blah" * 3
        }


class PurchaseEventTestCase(ChildTestBase, ChildTestMixin):
    prefix = "purchase"
    childClass = PurchaseEvent

    def get_create_post_dict(self):
        return {
            'date': "2017-1-1",
            'vendor_name': "Vendor Name",
            'vendor_address': "addy",
            'purchase_price': '200',
            'notes': "blah" * 3
        }


class DecommissionEventTestCase(ChildTestBase, ChildTestMixin):
    prefix = "decommission"
    childClass = DecommissionEvent

    def get_create_post_dict(self):
        return {
            'date': "2017-1-1",
            'method': "recycled",
            'cost': '200',
            'notes': "blah" * 3
        }

    def post_create(self, event):
        self.assertEqual(event.device.status, 'retired')
        self.assertEqual(event.device.current_owner, None)


class WarrantyTestCase(ChildTestBase, ChildTestMixin):
    prefix = "warranty"
    childClass = Warranty

    def get_create_post_dict(self):
        return {
            'start_date': "2017-1-1",
            'end_date': "2018-1-1",
            'description': "blah" * 3
        }

    def get_modify_post_dict(self):
        " simplest option is just to change the note "
        post_dict = self.get_create_post_dict()
        post_dict['description'] = "blerg" * 2
        return post_dict

    def post_modify(self, warranty):
        " confirm that the description changed "
        self.assertEqual(warranty.description, "blerg" * 2)
