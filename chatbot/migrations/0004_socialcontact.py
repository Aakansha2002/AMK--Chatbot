from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("chatbot", "0003_social_channels")]
    operations = [
        migrations.CreateModel(name="SocialContact", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("platform", models.CharField(max_length=20)),
            ("external_user_id", models.CharField(max_length=120)),
            ("session_id", models.CharField(max_length=80, unique=True)),
            ("updated_at", models.DateTimeField(auto_now=True)),
        ], options={"constraints": [models.UniqueConstraint(fields=("platform", "external_user_id"), name="uniq_social_platform_contact")]}),
    ]
