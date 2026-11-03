# AMK Hospitality — AI concierge demo

A Django + SQLite prototype for AMK Hospitality's first point of contact. The interface combines a guest-facing chat preview with a lead operations dashboard. The chat handles greetings and common questions on its own, gathers enquiry details, then routes a qualified summary to Weddings & Events, AMK Travels, or Other Services.

## Run locally

Requires Python 3.8+.

On macOS, double-click `open_demo.command`. It creates a private Python environment, installs Django on the first run, runs database migrations, and opens the dashboard in Chrome. An internet connection is needed for the one-time Django install. Keep the Terminal window open while using the demo. **Do not open `chatbot/templates/chatbot/dashboard.html` directly**: Django must render that template and serve its CSS and JavaScript.

```bash
cd amk_hospitality
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) and choose **Preview assistant**. Try “Plan an event” or “Plan a trip”; the assistant collects the requirement, location, date, budget, name, email, and an optional call number before saving a lead. Return to the dashboard to see the routed summary.

## What is implemented

- Django endpoints at `/api/chat/`, `/api/leads/`, `/api/channels/`, `/api/health/`, and `/webhooks/meta/`.
- SQLite lead persistence, department assignment, a lead status field, and saved guest/assistant messages that load when the same browser returns.
- Saying “That’s all, thanks” after a handoff closes that conversation and automatically opens a clean chat session for the next guest.
- Lead detail view with saved status updates: New, Contacted, Converted, or Closed.
- Selecting **Ask a question** opens only the 10 clickable topic buttons; selecting a topic prompts the guest to type their question. FAQ state is kept during the exchange so a follow-up doesn't fall back into the generic pricing reply.
- **Contact Our Team** displays the WhatsApp number and offers Ask another question, End conversation, or Open WhatsApp chat. Ending closes and resets the guest session.
- A responsive dashboard whose totals, seven-day mini charts, latest reply, and Meta channel status come from saved database records and runtime configuration. It refreshes the lead inbox every 15 seconds so social webhook leads appear without reloading.
- An Instagram-only webhook at `/webhooks/meta/` that verifies the webhook challenge and `X-Hub-Signature-256`, processes incoming Instagram DMs through the qualification engine, stores the conversation/lead, and replies through Instagram's Send API.
- Rule-based conversation and qualification engine that runs locally without an API key. This is a working local chatbot, not a generative AI service. To produce open-ended AI answers, connect an LLM provider and key in `chatbot/engine.py` while keeping qualification and routing rules as server-side policy.
- Safe text rendering in the chat and escaped lead values in the dashboard.

## Qualification and routing

The assistant classifies event, travel, and other-service intents. It asks for a requirement, location, date, budget range, name, and email, plus a phone number (the guest can type “skip”). It creates a lead only after the contact and enquiry details are collected. FAQs and greetings do not create leads. A direct request for a person is handled in the same conversation and can be recorded with the details already supplied.

## Website and social integrations

The website preview uses the same-origin Django chat endpoint. For a public website, host this app at a public HTTPS URL and embed the chat client or proxy the chat endpoint through the company's site.

Instagram DM webhook handling for `@indianweddingplanners` is implemented at `/webhooks/meta/`. It uses Instagram API with Instagram Login, the same chat engine, and stores messages and qualified leads in SQLite. Facebook Messenger is not included. To connect the account:

1. Ensure `@indianweddingplanners` is an Instagram professional (Business or Creator) account.
2. Create a Meta developer app and configure Instagram API with Instagram Login. Request the current `instagram_business_manage_messages` permission and complete Meta app review/advanced access as needed.
3. Copy `.env.example` to `.env` and add the Instagram user access token, Instagram professional account ID, app secret, and a private webhook verification token.
4. Deploy behind a public HTTPS URL (or use a secure HTTPS tunnel during development). Set the callback URL to `https://YOUR_HOST/webhooks/meta/`, enter the same verification token, and subscribe to Instagram message events.
5. Send a test DM to `@indianweddingplanners` from an account allowed by the app. The channel card changes from Setup/Waiting to Connected after the first inbound message; qualified conversations appear in the lead inbox.

The dashboard also has direct DM links: Instagram opens `@indianweddingplanners`; WhatsApp opens `wa.me/919251966666` with a prefilled greeting. `WHATSAPP_NUMBER` can be changed in `.env` and should include country code with digits only. The project assumes India (+91) for the provided 10-digit number. The WhatsApp link opens the user's WhatsApp chat; it does not run the AMK chatbot inside WhatsApp. Automating WhatsApp replies requires separate WhatsApp Business Platform credentials/webhooks.

The Instagram account credentials, public host, Meta app review, and account permissions are external requirements, so automated Instagram replies remain in Setup until these are supplied. The handle alone is not an API credential; the integration needs the account's Instagram Login token and Instagram-scoped account ID. Instagram Login supports professional Business/Creator accounts and the Instagram messaging permission; a Facebook Messenger/Page integration is not included. Do not commit `.env`. Instagram conversations start when a user messages the professional account; replies are sent through the Instagram Send API. See Meta's [Instagram API with Instagram Login](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/) and [Instagram messaging guide](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/messaging-api/).

## Production checklist

This is an interview/demo build. Before public deployment, use environment-managed secrets, `DEBUG=False`, HTTPS, authenticated staff access to the dashboard and leads endpoint, CSRF protection or signed webhook verification, rate limiting, consent and retention policies, email/CRM notifications, and appropriate PII access controls. The deterministic engine is a starting point and should be tuned against AMK's approved FAQ and qualification policy.
