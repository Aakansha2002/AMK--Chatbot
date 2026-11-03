from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [migrations.CreateModel(name="Lead", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("session_id", models.CharField(max_length=80, unique=True)),
        ("name", models.CharField(max_length=120)),
        ("email", models.EmailField(max_length=254)),
        ("phone", models.CharField(blank=True, max_length=40)),
        ("department", models.CharField(choices=[("events", "Weddings & Events"), ("travel", "AMK Travels"), ("other", "Other Services")], max_length=16)),
        ("requirement", models.TextField()),
        ("location", models.CharField(blank=True, max_length=160)),
        ("date", models.CharField(blank=True, max_length=100)),
        ("budget", models.CharField(blank=True, max_length=100)),
        ("status", models.CharField(choices=[("new", "New"), ("contacted", "Contacted"), ("converted", "Converted"), ("closed", "Closed")], default="new", max_length=16)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
    ], options={"ordering": ["-created_at"]})]
