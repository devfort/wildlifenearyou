from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import simplejson
from models import ChangeAttributeRequest, ContentType, CreateObjectRequest, \
    DeleteObjectRequest, ChangeRequest

class TestChangeRequests(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(username='test-user-1')

    def tearDown(self):
        self.user1.delete()

    def testChangeAttributeRequestString(self):
        cr = ChangeAttributeRequest.objects.create(
            content_type = ContentType.objects.get_for_model(User),
            object_id = self.user1.id,
            attribute = 'first_name',
            value = 'Oooh'
        )
        self.assertEqual(cr.content_object, self.user1)
        self.assert_(not self.user1.first_name)
        self.assert_(not cr.applied_at)
        self.assert_(not cr.applied_by)

        cr.apply()

        self.user1 = User.objects.get(pk = self.user1.pk)
        self.assertEqual(self.user1.first_name, 'Oooh')
        self.assert_(cr.applied_at)
        self.assert_(not cr.applied_by) # Because no specified user

    def testCreateObjectRequest(self):
        cr = CreateObjectRequest.objects.create(
            content_type = ContentType.objects.get_for_model(User),
            attributes = simplejson.dumps({
                'username': 'test-user-2',
                'email': 'testuser2@example.com',
            })
        )
        self.assertEqual(
            User.objects.filter(username = 'test-user-2').count(), 0
        )

        cr.apply()

        self.assertEqual(
            User.objects.filter(username = 'test-user-2').count(), 1
        )
        u = User.objects.get(username = 'test-user-2')
        self.assertEqual(u.email, 'testuser2@example.com')

    def testDeleteObjectRequest(self):
        user3 = User.objects.create(username='test-user-3')
        cr = DeleteObjectRequest.objects.create(
            content_type = ContentType.objects.get_for_model(User),
            object_id = user3.pk
        )
        self.assertEqual(
            User.objects.filter(username = 'test-user-3').count(), 1
        )

        cr.apply()

        self.assertEqual(
            User.objects.filter(username = 'test-user-3').count(), 0
        )

    def testTrackSubclassCorrectly(self):
        cr = DeleteObjectRequest.objects.create(
            content_type = ContentType.objects.get_for_model(User),
            object_id = self.user1.pk
        )
        # Reload it as a ChangeRequest
        cr2 = ChangeRequest.objects.get(pk = cr.pk)
        real = cr2.get_real()
        self.assertEqual(type(cr), type(real))
