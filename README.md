**Overview**
Cancel Context Collector captures why users cancel and the context right before it happened. It is lightweight, privacy-safe, and sends founders a clean alert immediately.

**Quick Start**
1. Create a virtual environment and install dependencies from `requirements.txt`.
2. Run the API with `uvicorn app.main:app --reload`.
3. Visit `http://localhost:8000/cancel.html?account_id=demo`.

**Configuration**
Set these in `.env` or your environment.
- `DATABASE_URL` (default: `sqlite:///./cancel_context.db`)
- `DEFAULT_FOUNDER_EMAIL` (required for auto-account creation)
- `DEFAULT_ACCOUNT_NAME` (optional)
- `DEFAULT_SLACK_WEBHOOK_URL` (optional)
- `DEFAULT_ACCOUNT_API_KEY` (optional, API key for auto-created accounts)
- `ALLOW_AUTO_ACCOUNT` (default: `true`)
- `CANCEL_API_KEY` (optional, adds `X-Cancel-Key` protection to the cancel endpoint)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_USE_TLS`, `EMAIL_FROM`
- `DASHBOARD_API_KEY` (optional, for dashboard endpoints)
- `ALLOWED_REASONS` (comma-separated allowlist for cancellation reasons)
- `CANCEL_RATE_LIMIT_PER_MINUTE` (default: 30)
- `CANCEL_RATE_LIMIT_WINDOW_SECONDS` (default: 60)
- `SENTRY_DSN`, `SENTRY_TRACES_SAMPLE_RATE`
- `REDIS_URL` (required to enable background notification worker)
- `NOTIFICATION_QUEUE_NAME` (default: `notifications`)
- `NOTIFICATION_RETRY_INTERVALS` (default: `10,60,300`)
- `NOTIFICATION_MAX_ATTEMPTS` (default: `4`)
- `AUTO_CREATE_TABLES` (default: `true`)
- `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_PRE_PING`

**Billing Flow**
Redirect your Stripe or Paddle cancel action to:
- `https://your-domain/cancel.html?account_id=your_account_id&cancel_key=ACCOUNT_API_KEY`

**Context Capture Snippet (Optional)**
Drop this into your SaaS app to capture lightweight context before the cancel page.

```html
<script>
(function () {
  if (!sessionStorage.getItem("cc_session_start")) {
    sessionStorage.setItem("cc_session_start", Date.now().toString());
  }

  const events = [];
  function track(name, meta) {
    events.push({ name: name, meta: meta || {}, ts: Date.now() });
    sessionStorage.setItem("cc_last_events", JSON.stringify(events.slice(-10)));
  }

  window.ccTrackEvent = track;
  document.addEventListener("click", function (event) {
    const target = event.target;
    if (target && target.tagName) {
      track("click", { tag: target.tagName.toLowerCase() });
    }
  });

  window.addEventListener("error", function (event) {
    const existing = JSON.parse(sessionStorage.getItem("cc_js_errors") || "[]");
    existing.push(event.message || "unknown error");
    sessionStorage.setItem("cc_js_errors", JSON.stringify(existing.slice(-5)));
  });
})();
</script>
```

**Background Worker**
Notifications are processed asynchronously via Redis + RQ.
- Start the API: `uvicorn app.main:app --reload`
- Start the worker: `python -m app.worker`

**Migrations (Alembic)**
1. Set `DATABASE_URL` to your Postgres database.
2. Run: `alembic upgrade head`

**Docker (Production)**
Use `docker-compose.yml` to run API, worker, Postgres, and Redis together.
1. `docker compose up --build`
2. `docker compose exec web alembic upgrade head`
3. Visit `http://localhost:8000/`

**Admin UI**
Open `http://localhost:8000/admin.html` and enter `DASHBOARD_API_KEY` to manage accounts and API keys.

**Waitlist Deployment (Vercel)**
This repo includes a static waitlist landing page in `cancel context waitlist/`.
1. Import the repo in Vercel.
2. Set the root directory to the repo root (not the folder).
3. Vercel will use `vercel.json` to serve the waitlist page.

**API**
- `POST /api/cancel/{account_id}`
- `GET /api/dashboard/cancellations`
- `GET /api/dashboard/summary`
- `POST /api/dashboard/test-email?to_address=you@example.com`
