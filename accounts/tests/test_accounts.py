from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccountTests(TestCase):
    def test_registration_creates_profile_and_authenticates_user(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "patient-one", "email": "patient@example.com", "first_name": "Pat",
            "last_name": "One", "password1": "Valid-Safe-Pass-489!", "password2": "Valid-Safe-Pass-489!",
        })
        user = get_user_model().objects.get(username="patient-one")
        self.assertRedirects(response, reverse("dashboard:home"))
        self.assertTrue(user.check_password("Valid-Safe-Pass-489!"))
        self.assertTrue(user.is_authenticated)
        self.assertTrue(user.profile)

    def test_profile_updates_user_and_profile_fields(self):
        user = get_user_model().objects.create_user(username="profile-user", password="Safe-Password-2048!")
        self.client.force_login(user)
        response = self.client.post(reverse("accounts:profile"), {
            "first_name": "Avery", "last_name": "Lee", "email": "avery@example.com", "organization": "Clinic",
        })
        user.refresh_from_db()
        self.assertRedirects(response, reverse("accounts:profile"))
        self.assertEqual(user.first_name, "Avery")
        self.assertEqual(user.profile.organization, "Clinic")