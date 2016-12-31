from base import BaseTestCase

from django.core.urlresolvers import reverse

from ..apps.devices.models import Device
from ..apps.people.models import Person


class PeopleTestCase(BaseTestCase):
    """
    List, create, edit, delete
    """

    def testPeople(self):
        self.client.login(**self.admin_cred)

        self.assertEqual(Person.objects.count(), 2)

        # Base list
        url = reverse('dashboard:person_list', kwargs=self.org_url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 2)

        # Add
        url = reverse('dashboard:person_add', kwargs=self.org_url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        post_dict = {
            'name': "person 3",
            'position': 'test dummy',
            'email': 'person@example.com',
            'is_active': 'yes'
        }
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Person.objects.count(), 3)

        # detail
        person = Person.objects.get(name="person 3")
        person_url_kwargs = {'pk': person.id}
        person_url_kwargs.update(self.org_url_kwargs)

        url = reverse('dashboard:person_detail', kwargs=person_url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # edit
        url = reverse('dashboard:person_update', kwargs=person_url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        post_dict['position'] = 'airbag'
        response = self.client.post(url, post_dict)
        self.assertEqual(response.status_code, 302)
        person.refresh_from_db()
        self.assertEqual(person.position, 'airbag')

        # delete
        # url = reverse('dashboard:person_delete', kwargs=person_url_kwargs)
        # response = self.client.get(url)
        # self.assertEqual(response.status_code, 200)
        # response = self.client.post(url, {'confirm': 'yes'})
        # self.assertEqual(Person.objects.count(), 2)
