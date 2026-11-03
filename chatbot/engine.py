import re
import os

DEPARTMENTS = {"events": "Weddings & Events", "travel": "AMK Travels", "other": "Other Services"}
QUESTIONS = {
    "events": ["What kind of celebration are you planning?", "Where will it take place?", "When is your event?", "Do you have a budget range in mind?", "What should we call you?", "What's the best email to reach you?", "And a phone number, if you'd like us to call?"] ,
    "travel": ["Where would you like to travel?", "Where will you be travelling from?", "When are you hoping to travel?", "What's your approximate budget per person?", "What should we call you?", "What's the best email to reach you?", "And a phone number, if you'd like us to call?"],
    "other": ["Could you tell me a little about the service you need?", "Which city or location is this for?", "When do you need the service?", "Do you have a budget range in mind?", "What should we call you?", "What's the best email to reach you?", "And a phone number, if you'd like us to call?"]
}
SLOT_KEYS = {"events": ["requirement", "location", "date", "budget", "name", "email", "phone"], "travel": ["requirement", "location", "date", "budget", "name", "email", "phone"], "other": ["requirement", "location", "date", "budget", "name", "email", "phone"]}
FAQ_MENU = ["About Us", "Existing Booking", "Payment & Invoice", "Booking Status", "Cancellation & Refunds", "Partnership & Collaboration", "Careers", "Feedback & Complaints", "Contact Our Team", "Something Else"]
FAQ_PROMPTS = [
    "Would you like to know more about our company?",
    "Do you need help with an existing booking or reservation?",
    "Do you have a question about payments, invoices or receipts?",
    "Would you like an update on your ongoing arrangements?",
    "Do you have a question about our cancellation or refund policies?",
    "Are you interested in working or partnering with us?",
    "Would you like to explore career opportunities with us?",
    "Would you like to share feedback or report an issue?",
    "Would you like to speak with one of our representatives?",
    "Is there anything else you'd like to ask?",
]
FAQ_ALIASES = {item.lower(): item.lower().replace(" & ", "_and_").replace(" ", "_") for item in FAQ_MENU}

def question_menu(context):
    context.pop("faq_topic", None)
    context.pop("faq_waiting", None)
    context.pop("faq_replies", None)
    context.pop("contact_followup", None)
    return {"reply": "Choose a topic:", "context": context, "quick_replies": FAQ_MENU}

def contact_number():
    digits = "".join(c for c in os.environ.get("WHATSAPP_NUMBER", "919251966666") if c.isdigit()) or "919251966666"
    if len(digits) == 12 and digits.startswith("91"):
        return f"+91 {digits[2:7]} {digits[7:]}"
    return f"+{digits}"

def contact_team(context):
    context.pop("faq_topic", None)
    context.pop("faq_waiting", None)
    context.pop("faq_replies", None)
    context["contact_followup"] = True
    return {"reply": f"You can contact AMK Hospitality on WhatsApp at {contact_number()}. Would you like to ask another question or end this conversation?", "context": context, "quick_replies": ["Ask another question", "End conversation", "Open WhatsApp chat"]}

def detect_department(text):
    t = text.lower()
    if any(w in t for w in ["wedding", "marriage", "reception", "venue", "event", "celebration", "birthday", "conference"]): return "events"
    if any(w in t for w in ["travel", "trip", "holiday", "package", "itinerary", "flight", "hotel", "tour", "honeymoon"]): return "travel"
    if any(w in t for w in ["service", "catering", "decoration", "decor", "photography", "ask", "help"]): return "other"
    return None

def respond(text, context):
    t = text.strip()
    lower = t.lower()
    normalized = re.sub(r"[^a-z0-9& ]", "", lower).strip()
    if context.get("contact_followup"):
        if normalized in {"end conversation", "end", "end chat", "finish", "close chat"}:
            return {"reply": "Thanks for contacting AMK Hospitality. This conversation is now closed. Goodbye!", "context": {}, "quick_replies": [], "end_conversation": True}
        if normalized in {"ask another question", "ask a question", "back to topics"}:
            return question_menu(context)
        return {"reply": f"You can contact AMK Hospitality on WhatsApp at {contact_number()}. Would you like to ask another question or end this conversation?", "context": context, "quick_replies": ["Ask another question", "End conversation", "Open WhatsApp chat"]}
    if normalized in {"ask a question", "ask another question", "back to topics"}:
        return question_menu(context)
    selected_topic = FAQ_ALIASES.get(normalized)
    if selected_topic:
        if selected_topic == "contact_our_team":
            return contact_team(context)
        context["faq_topic"] = selected_topic
        context["faq_waiting"] = True
        context["faq_replies"] = 0
        if selected_topic == "contact_our_team":
            prompt = "What would you like help with? Type your question and I'll help direct you to the right team."
        else:
            prompt = "Sure! Please type your question below, and I'll do my best to help you. 😊"
        return {"reply": prompt, "context": context, "quick_replies": ["Back to topics"]}
    pricing_words = any(w in lower for w in ["price", "cost", "how much", "quote"])
    dept_from_message = detect_department(t)
    service_choice = normalized in {"plan an event", "plan a trip", "weddings events", "weddings & events", "amk travels", "other services"}
    service_followup = context.get("faq_topic") == "pricing" and bool(dept_from_message)
    if service_choice or service_followup:
        context.pop("faq_topic", None)
        context.pop("faq_waiting", None)
        context.pop("faq_replies", None)
    elif context.get("faq_topic"):
        topic = context["faq_topic"]
        context["faq_waiting"] = False
        prior_replies = context.get("faq_replies", 0)
        context["faq_replies"] = prior_replies + 1
        if prior_replies and topic == "pricing":
            reply = "To guide you on pricing, I need to know which service you're considering."
            return {"reply": reply, "context": context, "quick_replies": ["Plan an event", "Plan a trip", "Other services"]}
        if prior_replies:
            reply = "I don't have more verified details for that topic loaded here, so I don't want to guess. Choose Contact Our Team or go back to the topics."
        elif topic == "about_us":
            reply = "AMK Hospitality helps with weddings and events, travel plans, and other hospitality services. What would you like to know about a specific service?"
        elif topic in {"existing_booking", "booking_status"}:
            reply = "I can't access live booking records in this chat, so I can't confirm a reservation or status. Please check your booking confirmation. If you need a person to review it, choose Contact Our Team."
        elif topic == "payment_and_invoice":
            reply = "I can't look up invoices or payment records here. Please check your booking email or invoice, and never send card numbers, passwords, PINs, or one-time codes in chat. Choose Contact Our Team if you need help."
        elif topic == "cancellation_and_refunds":
            reply = "Cancellation and refund terms depend on the specific booking. Please check the terms in your confirmation; I don't have AMK's approved policy details loaded here. Choose Contact Our Team for help with a specific booking."
        elif topic in {"partnership_and_collaboration", "careers"}:
            reply = "I don't have current partnership opportunities or job listings loaded here. Choose Contact Our Team and I can help direct your enquiry."
        elif topic == "feedback_and_complaints":
            reply = "I'm sorry something didn't go as expected. Please describe what happened and what outcome would help. This demo doesn't yet submit a support ticket, but you can choose Contact Our Team."
        elif topic == "contact_our_team":
            return contact_team(context)
        elif topic == "pricing" or any(w in lower for w in ["price", "cost", "how much", "quote"]):
            context["faq_topic"] = "pricing"
            context["faq_replies"] = 1
            reply = "Pricing depends on the service, location, and plans. Choose a service below and I'll ask a few details so the right team can guide you."
            return {"reply": reply, "context": context, "quick_replies": ["Plan an event", "Plan a trip", "Other services"]}
        else:
            reply = "Thanks for your question. I can answer basic questions about AMK's services, but I don't have a full company FAQ connected yet. Choose Contact Our Team if you need a person."
        return {"reply": reply, "context": context, "quick_replies": ["Ask another question", "Contact Our Team", "Back to topics"]}
    if context.get("handoff"):
        normalized = re.sub(r"[^a-z\s]", "", lower).strip()
        if normalized in {"thats all thanks", "that is all thanks", "thanks thats all", "thank you thats all", "thank you", "thanks"}:
            return {"reply": "You're very welcome. This conversation is complete, and I'm ready to help with a fresh enquiry.", "context": context, "quick_replies": [], "reset_conversation": True}
        return {"reply": "Your details are already with our team. Someone from the right department will be in touch shortly. Is there anything else I can help with?", "context": context, "quick_replies": ["Ask another question", "That's all, thanks"]}
    if context.get("awaiting_handoff"):
        context["awaiting_handoff"] = False
        return {"reply": "Of course. Tell me what you'd like help with, and I'll point you in the right direction.", "context": context, "quick_replies": ["Plan an event", "Plan a trip", "Other services"]}
    if any(w in lower for w in ["human", "person", "team member", "agent", "call me", "contact the team", "speak with", "representative"]):
        return contact_team(context)
    if any(w in lower for w in ["hello", "hi", "hey", "good morning", "good afternoon"]):
        return {"reply": "Hello! Welcome to AMK Hospitality. I can help with weddings & events, travel plans, and our other services. What brings you here today?", "context": context, "quick_replies": ["Plan an event", "Plan a trip", "Other services", "Ask a question"]}
    if any(w in lower for w in ["price", "cost", "how much", "faq", "hours", "where are you", "services"]):
        context["faq_topic"] = "pricing"
        context["faq_replies"] = 1
        return {"reply": "Pricing depends on the service, location, and plans. Choose a service below and I'll ask a few details so the right team can guide you.", "context": context, "quick_replies": ["Plan an event", "Plan a trip", "Other services"]}
    dept = context.get("department") or detect_department(t)
    if not dept:
        return {"reply": "I can help with event planning, travel, or other hospitality services. Which one are you interested in?", "context": context, "quick_replies": ["Plan an event", "Plan a trip", "Other services"]}
    context["department"] = dept
    # The message that identifies a service also starts the requirement slot.
    keys = SLOT_KEYS[dept]
    missing = next((k for k in keys if not context.get(k)), None)
    if missing:
        # Use original user input as the requirement when it identifies the service.
        if missing == "requirement":
            context[missing] = t
            missing = next((k for k in keys if not context.get(k)), None)
        else:
            if missing == "email" and not re.search(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", t):
                return {"reply": "That doesn't look like a valid email yet. Could you check it and send it again?", "context": context, "quick_replies": []}
            context[missing] = "" if missing == "phone" and t.lower() in {"skip", "no", "no thanks", "prefer not"} else t
            missing = next((k for k in keys if not context.get(k)), None)
    if missing:
        idx = keys.index(missing)
        return {"reply": QUESTIONS[dept][idx], "context": context, "quick_replies": []}
    context["handoff"] = True
    return {"reply": f"Thanks, {context['name']}! I've shared your {DEPARTMENTS[dept]} enquiry with the team. They'll follow up at {context['email']} soon.", "context": context, "quick_replies": ["That's all, thanks"], "qualified": True}
