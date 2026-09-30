"""
Accounts models: UserProfile and UserActivityLog.
"""
from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Extended profile information for each registered user."""
    GENDER_CHOICES = (("M", "Male"), ("F", "Female"), ("O", "Other / Prefer not to say"))

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    full_name = models.CharField(max_length=200, blank=True, help_text="Full legal name")
    phone = models.CharField(max_length=25, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    organization = models.CharField(max_length=200, blank=True, help_text="Hospital / Clinic / Institution")
    bio = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return "{}'s profile".format(self.user.username)

    def get_display_name(self):
        """Return the best available display name."""
        return self.full_name or self.user.get_full_name() or self.user.username

    def get_initials(self):
        name = self.get_display_name()
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return name[:2].upper()


class UserActivityLog(models.Model):
    """Tracks user actions for audit trail."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity_logs"
    )
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-timestamp",)
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"

    def __str__(self):
        return "{} – {} at {}".format(
            self.user.username, self.action, self.timestamp.strftime("%Y-%m-%d %H:%M")
        )