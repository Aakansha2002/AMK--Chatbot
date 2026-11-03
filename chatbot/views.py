import json
import uuid
from datetime import timedelta
from urllib.parse import quote
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .models import ChatMessage, Conversation, Lead
from .services import process_message

def dashboard(request):
    recent = [l.as_dict() for l in Lead.objects.all()[:8]]
    totals = {"all": Lead.objects.count(), "new": Lead.objects.filter(status="new").count(),
              "events": Lead.objects.filter(department="events").count(), "travel": Lead.objects.filter(department="travel").count()}
    today = timezone.localdate()
    days = [today - timedelta(days=n) for n in range(6, -1, -1)]
    counts = {"all": [0] * 7, "new": [0] * 7, "events": [0] * 7, "travel": [0] * 7}
    for lead in Lead.objects.filter(created_at__date__gte=days[0]).only("created_at", "department", "status"):
        day = timezone.localtime(lead.created_at).date()
        index = (day - days[0]).days
        if 0 <= index < 7:
            counts["all"][index] += 1
            if lead.status == "new": counts["new"][index] += 1
            if lead.department in ("events", "travel"): counts[lead.department][index] += 1
    trends = {}
    for key, series in counts.items():
        max_value = max(series, default=0) or 1
        trends[key] = [{"height": max(9, round((value / max_value) * 100)), "value": value} for value in series]
    latest_reply = ChatMessage.objects.filter(role="assistant").order_by("-created_at").first()
    reply_preview = latest_reply.body if latest_reply else "No guest conversations yet. Preview the assistant to try a conversation."
    return render(request, "chatbot/dashboard.html", {"leads": recent, "totals": totals, "trends": trends,
        "today": today, "today_label": today.strftime("%A, %B %-d"), "reply_preview": reply_preview,
        "instagram_username": settings.INSTAGRAM_USERNAME,
        "instagram_dm_url": f"https://ig.me/m/{settings.INSTAGRAM_USERNAME}",
        "whatsapp_dm_url": f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={quote('Hi AMK Hospitality, I would like help with an enquiry.')}"})

@csrf_exempt
@require_POST
def chat(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    text = str(payload.get("message", ""))[:1000]
    if not text.strip(): return JsonResponse({"error": "Message is required"}, status=400)
    session_id = str(payload.get("session_id") or uuid.uuid4())[:80]
    result = process_message(session_id, text, channel="website")
    result["session_id"] = session_id
    return JsonResponse(result)

@require_GET
def chat_history(request, session_id):
    conversation = Conversation.objects.filter(session_id=session_id[:80]).first()
    if not conversation:
        return JsonResponse({"context": {}, "messages": []})
    return JsonResponse({"context": conversation.context, "messages": [
        {"role": m.role, "body": m.body, "created_at": m.created_at.isoformat()}
        for m in conversation.messages.all()[:100]
    ]})

@require_GET
def leads(request):
    qs = Lead.objects.all()
    department = request.GET.get("department")
    status = request.GET.get("status")
    if department in {"events", "travel", "other"}: qs = qs.filter(department=department)
    if status in {"new", "contacted", "converted", "closed"}: qs = qs.filter(status=status)
    return JsonResponse({"leads": [l.as_dict() for l in qs[:100]]})

@csrf_exempt
@require_http_methods(["GET", "PATCH"])
def lead_detail(request, lead_id):
    try:
        lead = Lead.objects.get(pk=lead_id)
    except Lead.DoesNotExist:
        return JsonResponse({"error": "Lead not found"}, status=404)
    if request.method == "PATCH":
        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        status = data.get("status")
        if status not in {"new", "contacted", "converted", "closed"}:
            return JsonResponse({"error": "Choose a valid lead status"}, status=400)
        lead.status = status
        lead.save(update_fields=["status"])
    return JsonResponse({"lead": lead.as_dict()})

@require_GET
def health(request):
    return JsonResponse({"status": "ok", "service": "AMK Hospitality assistant"})

@require_GET
def channels(request):
    from .models import Conversation
    instagram_ready = all([settings.META_VERIFY_TOKEN, settings.META_APP_SECRET, settings.META_INSTAGRAM_ACCESS_TOKEN, settings.META_INSTAGRAM_ACCOUNT_ID])
    instagram_seen = Conversation.objects.filter(channel="instagram").exists()
    instagram_state = "connected" if instagram_ready and instagram_seen else "active"
    return JsonResponse({"channels": [
        {"id": "website", "label": "Website chat", "state": "active", "detail": "Running on this site"},
        {"id": "instagram", "label": f"@{settings.INSTAGRAM_USERNAME}", "state": instagram_state, "detail": "DM link ready · chatbot is receiving DMs" if instagram_seen and instagram_ready else "Tap to open Instagram DM · automated replies need account setup"},
        {"id": "whatsapp", "label": "WhatsApp chat", "state": "active", "detail": "Tap to open WhatsApp chat"},
    ]})
