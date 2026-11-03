from django.db import models
from django.utils import timezone

class Lead(models.Model):
    DEPARTMENTS = [("events", "Weddings & Events"), ("travel", "AMK Travels"), ("other", "Other Services")]
    STATUSES = [("new", "New"), ("contacted", "Contacted"), ("converted", "Converted"), ("closed", "Closed")]
    session_id = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    department = models.CharField(max_length=16, choices=DEPARTMENTS)
    channel = models.CharField(max_length=20, default="website")
    requirement = models.TextField()
    location = models.CharField(max_length=160, blank=True)
    date = models.CharField(max_length=100, blank=True)
    budget = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=16, choices=STATUSES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def as_dict(self):
        return {"id": self.pk, "name": self.name, "email": self.email, "phone": self.phone,
                "department": self.get_department_display(), "department_key": self.department,
                "channel": self.channel,
                "requirement": self.requirement, "location": self.location, "date": self.date,
                "budget": self.budget, "status": self.get_status_display(),
                "created_at": self.created_at.isoformat()}

class Conversation(models.Model):
    session_id = models.CharField(max_length=80, unique=True)
    channel = models.CharField(max_length=20, default="website")
    external_user_id = models.CharField(max_length=120, blank=True)
    context = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(default=timezone.now)

class ChatMessage(models.Model):
    ROLES = [("user", "Guest"), ("assistant", "Assistant")]
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=12, choices=ROLES)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

class SocialContact(models.Model):
    platform = models.CharField(max_length=20)
    external_user_id = models.CharField(max_length=120)
    session_id = models.CharField(max_length=80, unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["platform", "external_user_id"], name="uniq_social_platform_contact")]
