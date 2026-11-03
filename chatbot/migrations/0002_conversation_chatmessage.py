import django.utils.timezone
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [("chatbot", "0001_initial")]
    operations = [
        migrations.CreateModel(name="Conversation", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("session_id", models.CharField(max_length=80, unique=True)),
            ("context", models.JSONField(blank=True, default=dict)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("updated_at", models.DateTimeField(default=django.utils.timezone.now)),
        ]),
        migrations.CreateModel(name="ChatMessage", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("role", models.CharField(choices=[("user", "Guest"), ("assistant", "Assistant")], max_length=12)),
            ("body", models.TextField()),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("conversation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="chatbot.conversation")),
        ], options={"ordering": ["created_at", "id"]}),
    ]
