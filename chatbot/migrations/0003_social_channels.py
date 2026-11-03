from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("chatbot", "0002_conversation_chatmessage")]
    operations = [
        migrations.AddField(model_name="conversation", name="channel", field=models.CharField(default="website", max_length=20)),
        migrations.AddField(model_name="conversation", name="external_user_id", field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name="lead", name="channel", field=models.CharField(default="website", max_length=20)),
    ]
