const form = document.getElementById("cancelForm");
const statusEl = document.getElementById("status");
const submitBtn = document.getElementById("submitBtn");
const noteEl = document.getElementById("note");
const body = document.body;

const params = new URLSearchParams(window.location.search);
const apiBase = body.dataset.apiBase || "";
const accountId = params.get("account_id") || body.dataset.accountId || "demo";
const cancelKey = params.get("cancel_key") || body.dataset.cancelKey || "";

function readJson(key, fallback) {
  try {
    const raw = sessionStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw);
  } catch (err) {
    return fallback;
  }
}

function readNumber(key) {
  const raw = sessionStorage.getItem(key);
  if (!raw) return null;
  const num = Number(raw);
  return Number.isFinite(num) ? num : null;
}

function sessionDurationSeconds() {
  const startedAt = readNumber("cc_session_start");
  if (!startedAt) return null;
  const diff = Math.round((Date.now() - startedAt) / 1000);
  return diff >= 0 ? diff : null;
}

function lastEvents() {
  const fromStorage = readJson("cc_last_events", []);
  if (Array.isArray(fromStorage) && fromStorage.length) {
    return fromStorage.slice(-3);
  }
  const inline = window.cc_last_events || [];
  return Array.isArray(inline) ? inline.slice(-3) : [];
}

function jsErrors() {
  const fromStorage = readJson("cc_js_errors", []);
  if (Array.isArray(fromStorage) && fromStorage.length) {
    return fromStorage;
  }
  return Array.isArray(window.cc_js_errors) ? window.cc_js_errors : [];
}

function buildPayload(reason) {
  return {
    reason: reason,
    note: noteEl.value.trim(),
    last_page: document.referrer || "",
    last_events: lastEvents(),
    session_duration_seconds: sessionDurationSeconds(),
    browser: navigator.userAgent,
    os: navigator.platform || "",
    js_errors: jsErrors(),
    time_to_first_value_seconds: readNumber("cc_ttfv_seconds"),
    context: {
      screen: `${screen.width}x${screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      locale: navigator.language || ""
    }
  };
}

function setStatus(message) {
  if (statusEl) statusEl.textContent = message || "";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const selected = form.querySelector('input[name="reason"]:checked');
  if (!selected) {
    setStatus("Please select a reason.");
    return;
  }

  submitBtn.disabled = true;
  setStatus("Sending...");

  const payload = buildPayload(selected.value);

  try {
    const headers = { "Content-Type": "application/json" };
    if (cancelKey) {
      headers["X-Cancel-Key"] = cancelKey;
    }
    const response = await fetch(
      `${apiBase}/api/cancel/${encodeURIComponent(accountId)}`,
      {
        method: "POST",
        headers: headers,
        body: JSON.stringify(payload)
      }
    );

    if (!response.ok) {
      throw new Error("Request failed");
    }

    window.location.href = "success.html";
  } catch (error) {
    setStatus("Could not send cancellation. Please try again.");
    submitBtn.disabled = false;
  }
});
