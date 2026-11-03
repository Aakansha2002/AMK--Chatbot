from django.utils import timezone
from .engine import respond
from .models import ChatMessage, Conversation, Lead

def process_message(session_id, text, channel="website", external_user_id=""):
    conversation, _ = Conversation.objects.get_or_create(
        session_id=session_id,
        defaults={"channel": channel, "external_user_id": external_user_id},
    )
    conversation.channel = channel
    if external_user_id:
        conversation.external_user_id = external_user_id
    context = conversation.context if isinstance(conversation.context, dict) else {}
    ChatMessage.objects.create(conversation=conversation, role="user", body=text)
    result = respond(text, context)
    # A finished social conversation keeps its transcript but starts the next turn clean.
    conversation.context = {} if result.get("reset_conversation") else result.get("context", context)
    conversation.updated_at = timezone.now()
    conversation.save(update_fields=["channel", "external_user_id", "context", "updated_at"])
    ChatMessage.objects.create(conversation=conversation, role="assistant", body=result["reply"])
    if result.get("qualified") or result.get("handoff_request"):
        ctx = result["context"]
        lead, _ = Lead.objects.update_or_create(session_id=session_id, defaults={
            "name": ctx.get("name", "Guest"), "email": ctx.get("email", "guest@example.com"),
            "phone": ctx.get("phone", ""), "department": ctx.get("department", "other"),
            "channel": channel, "requirement": ctx.get("requirement", ""),
            "location": ctx.get("location", ""), "date": ctx.get("date", ""),
            "budget": ctx.get("budget", "")})
        result["lead_id"] = lead.pk
    return result
