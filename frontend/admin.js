const adminKeyInput = document.getElementById("adminKey");
const form = document.getElementById("createAccountForm");
const statusEl = document.getElementById("adminStatus");
const listEl = document.getElementById("accountsList");

function getAdminKey() {
  return adminKeyInput.value.trim();
}

function setStatus(message) {
  statusEl.textContent = message || "";
}

async function fetchAccounts() {
  const headers = {};
  const key = getAdminKey();
  if (key) headers["X-API-Key"] = key;

  const response = await fetch("/api/admin/accounts", { headers });
  if (!response.ok) {
    setStatus("Failed to load accounts. Check API key.");
    return;
  }
  const accounts = await response.json();
  renderAccounts(accounts);
}

function renderAccounts(accounts) {
  if (!accounts.length) {
    listEl.innerHTML = "<p class=\"sub\">No accounts yet.</p>";
    return;
  }
  const rows = accounts
    .map(
      (acct) => `
        <div class="account-row">
          <div>
            <strong>${acct.name}</strong>
            <div class="sub">${acct.founder_email}</div>
          </div>
          <div class="account-meta">
            <div><span class="muted">ID:</span> ${acct.id}</div>
            <div><span class="muted">API Key:</span> ${acct.api_key || "—"}</div>
          </div>
          <button data-id="${acct.id}" class="rotate-btn">Rotate key</button>
        </div>
      `
    )
    .join("");
  listEl.innerHTML = rows;

  document.querySelectorAll(".rotate-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const accountId = btn.getAttribute("data-id");
      await rotateKey(accountId);
    });
  });
}

async function rotateKey(accountId) {
  const headers = {};
  const key = getAdminKey();
  if (key) headers["X-API-Key"] = key;

  const response = await fetch(`/api/admin/accounts/${accountId}/rotate-key`, {
    method: "POST",
    headers
  });
  if (!response.ok) {
    setStatus("Failed to rotate key.");
    return;
  }
  setStatus("API key rotated.");
  await fetchAccounts();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus("Creating...");

  const payload = {
    id: document.getElementById("accountId").value.trim() || null,
    name: document.getElementById("accountName").value.trim(),
    founder_email: document.getElementById("accountEmail").value.trim(),
    slack_webhook_url: document.getElementById("accountSlack").value.trim() || null
  };

  const headers = { "Content-Type": "application/json" };
  const key = getAdminKey();
  if (key) headers["X-API-Key"] = key;

  const response = await fetch("/api/admin/accounts", {
    method: "POST",
    headers,
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    setStatus("Create failed. Check API key and inputs.");
    return;
  }

  setStatus("Account created.");
  form.reset();
  await fetchAccounts();
});

adminKeyInput.addEventListener("change", fetchAccounts);
fetchAccounts();
