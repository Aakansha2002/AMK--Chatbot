import hashlib
import hmac
import json
import logging
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import SocialContact
from .services import process_message

logger = logging.getLogger(__name__)

def _send_instagram_reply(recipient_id, text):
    token = settings.META_INSTAGRAM_ACCESS_TOKEN
    version = settings.META_GRAPH_VERSION
    url = f"https://graph.instagram.com/{version}/{settings.META_INSTAGRAM_ACCOUNT_ID}/messages"
    body = json.dumps({"recipient": {"id": recipient_id}, "message": {"text": text}}).encode()
    request = Request(url, data=body, headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}, method="POST")
    with urlopen(request, timeout=8) as response:
        response.read()

@csrf_exempt
@require_http_methods(["GET", "POST"])
def meta_webhook(request):
    if request.method == "GET":
        if not settings.META_VERIFY_TOKEN:
            return HttpResponse("Meta webhook is not configured", status=503)
        if request.GET.get("hub.mode") == "subscribe" and hmac.compare_digest(
            request.GET.get("hub.verify_token", ""), settings.META_VERIFY_TOKEN
        ):
            return HttpResponse(request.GET.get("hub.challenge", ""), content_type="text/plain")
        return HttpResponse("Webhook verification failed", status=403)

    if not settings.META_APP_SECRET or not settings.META_INSTAGRAM_ACCESS_TOKEN or not settings.META_INSTAGRAM_ACCOUNT_ID:
        return JsonResponse({"error": "Meta webhook is not configured"}, status=503)
    raw = request.body
    supplied = request.headers.get("X-Hub-Signature-256", "")
    expected = "sha256=" + hmac.new(settings.META_APP_SECRET.encode(), raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(supplied, expected):
        return JsonResponse({"error": "Invalid webhook signature"}, status=403)
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid webhook JSON"}, status=400)

    if payload.get("object") != "instagram":
        return JsonResponse({"error": "Only Instagram messaging webhooks are enabled"}, status=400)
    platform = "instagram"
    processed = 0
    for entry in payload.get("entry", []):
        for event in entry.get("messaging", []):
            message = event.get("message", {})
            sender_id = (event.get("sender") or {}).get("id")
            text = message.get("text")
            if not sender_id or not text or message.get("is_echo"):
                continue
            contact, _ = SocialContact.objects.get_or_create(
                platform=platform,
                external_user_id=str(sender_id),
                defaults={"session_id": f"{platform}:{sender_id}"[:80]},
            )
            result = process_message(contact.session_id, str(text)[:1000], platform, str(sender_id))
            if result.get("reset_conversation"):
                contact.session_id = f"{platform}:{sender_id}:{uuid.uuid4().hex[:10]}"[:80]
                contact.save(update_fields=["session_id", "updated_at"])
            try:
                _send_instagram_reply(str(sender_id), result["reply"])
            except (HTTPError, URLError, TimeoutError, OSError):
                # Acknowledge the webhook to avoid duplicate replies on Meta retries.
                logger.exception("Could not send Instagram reply")
            processed += 1
    return JsonResponse({"status": "ok", "processed": processed})
