/* AddressSync v2 demo page. Vanilla JS, polls /demo/state for live updates. */

const $ = (id) => document.getElementById(id);
const state = {
  citizenToken: sessionStorage.getItem("citizen_token") || null,
  citizen: null,
  agencyToken: sessionStorage.getItem("agency_token") || null,
  agency: null,
  latest: null,
};

async function api(path, { method = "GET", body, token } = {}) {
  const headers = { "content-type": "application/json" };
  if (token) headers.authorization = `Bearer ${token}`;
  const resp = await fetch(path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(data.detail || `HTTP ${resp.status}`);
  return data;
}

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));

function timeAgo(iso) {
  if (!iso) return "—";
  const s = Math.max(0, (Date.now() - new Date(iso + "Z").getTime()) / 1000);
  if (s < 60) return `${Math.floor(s)}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  return new Date(iso + "Z").toLocaleTimeString();
}

/* ---------------- Citizen ---------------- */

$("otpBtn").onclick = async () => {
  $("citizenErr").textContent = "";
  try {
    const res = await api("/citizen/otp/request", {
      method: "POST",
      body: { aadhaar_number: $("aadhaarInput").value.trim() },
    });
    $("otpRow").classList.remove("hidden");
    $("otpHint").classList.remove("hidden");
    $("otpHint").innerHTML = res.otp
      ? `📩 dev_mode — OTP delivered here instead of SMS: <b>${esc(res.otp)}</b>`
      : "OTP sent via SMS";
  } catch (e) {
    $("citizenErr").textContent = e.message;
  }
};

$("verifyBtn").onclick = async () => {
  $("citizenErr").textContent = "";
  try {
    const res = await api("/citizen/otp/verify", {
      method: "POST",
      body: {
        aadhaar_number: $("aadhaarInput").value.trim(),
        otp: $("otpInput").value.trim(),
      },
    });
    state.citizenToken = res.access_token;
    state.citizen = res.citizen;
    sessionStorage.setItem("citizen_token", res.access_token);
    enterCitizenMode();
  } catch (e) {
    $("citizenErr").textContent = e.message;
  }
};

async function enterCitizenMode() {
  $("citizenLogin").classList.add("hidden");
  $("citizenPanel").classList.remove("hidden");
  await refreshCitizen();
}

async function refreshCitizen() {
  if (!state.citizenToken) return;
  try {
    const me = await api("/citizen/me", { token: state.citizenToken });
    state.citizen = { ...state.citizen, ...me };
    renderCitizen(me);
  } catch (e) {
    citizenLogout(); // token expired
  }
}

function renderCitizen(me) {
  $("profileBox").innerHTML =
    `<b>${esc(me.name)}</b> · <span class="mono">${esc(me.aadhaar_ref)}</span>` +
    `<br><span class="muted">${esc(me.phone)} · dob ${esc(me.dob)}</span>`;
  $("addrVersion").textContent = me.address ? `v${me.address.version}` : "none";

  const f = $("addrForm");
  ["line1", "line2", "city", "state", "pincode"].forEach((k) => {
    f[k].value = me.address?.[k] ?? "";
  });

  const list = $("consentList");
  list.innerHTML = me.consents.length
    ? ""
    : `<div class="muted">no consents yet</div>`;
  me.consents.forEach((c) => {
    const row = document.createElement("div");
    row.className = "consentItem";
    row.innerHTML =
      `<span class="mono">${esc(c.agency_id)}</span>` +
      `<span class="chip ${esc(c.status)}">${esc(c.status)}</span>` +
      `<span class="mono muted">${esc(c.id.slice(0, 8))}</span>`;
    const btn = document.createElement("button");
    btn.className = c.status === "granted" ? "btn small danger" : "btn small primary";
    btn.textContent = c.status === "granted" ? "Revoke" : "Re-grant";
    btn.onclick = async () => {
      $("consentErr").textContent = "";
      try {
        if (c.status === "granted") {
          await api(`/citizen/consents/${c.agency_id}`, {
            method: "DELETE", token: state.citizenToken,
          });
        } else {
          await api("/citizen/consents", {
            method: "POST", token: state.citizenToken,
            body: { agency_id: c.agency_id, purpose: c.purpose },
          });
        }
        refreshCitizen();
      } catch (e) {
        $("consentErr").textContent = e.message;
      }
    };
    row.appendChild(btn);
    list.appendChild(row);
  });

  // agencies without an existing consent row are grantable
  const consented = new Set(me.consents.map((c) => c.agency_id));
  const options = (state.latest?.agencies || [])
    .filter((a) => !consented.has(a.id))
    .map((a) => `<option value="${esc(a.id)}">${esc(a.name)} (${esc(a.id)})</option>`)
    .join("");
  $("consentAgency").innerHTML = options || `<option value="">all agencies consented</option>`;
  $("grantBtn").disabled = !options;
}

$("addrForm").onsubmit = async (ev) => {
  ev.preventDefault();
  $("addrMsg").textContent = "";
  const f = ev.target;
  try {
    const res = await api("/citizen/address", {
      method: "PUT",
      token: state.citizenToken,
      body: {
        line1: f.line1.value.trim(),
        line2: f.line2.value.trim() || null,
        city: f.city.value.trim(),
        state: f.state.value.trim(),
        pincode: f.pincode.value.trim(),
      },
    });
    $("addrMsg").textContent =
      `saved v${res.address.version} → notifying: ${res.agencies_notified.join(", ") || "no active consents"}`;
    refreshCitizen();
  } catch (e) {
    $("addrMsg").textContent = "";
    $("addrMsg").style.color = "var(--bad)";
    $("addrMsg").textContent = e.message;
  }
};

$("grantBtn").onclick = async () => {
  $("consentErr").textContent = "";
  try {
    await api("/citizen/consents", {
      method: "POST",
      token: state.citizenToken,
      body: {
        agency_id: $("consentAgency").value,
        purpose: $("consentPurpose").value.trim(),
      },
    });
    refreshCitizen();
  } catch (e) {
    $("consentErr").textContent = e.message;
  }
};

function citizenLogout() {
  state.citizenToken = null;
  state.citizen = null;
  sessionStorage.removeItem("citizen_token");
  $("citizenPanel").classList.add("hidden");
  $("citizenLogin").classList.remove("hidden");
}
$("logoutBtn").onclick = citizenLogout;

/* ---------------- Agency ---------------- */

$("agencyLoginBtn").onclick = async () => {
  $("agencyErr").textContent = "";
  try {
    const res = await api("/agencies/login", {
      method: "POST",
      body: { api_key: $("apiKeyInput").value.trim() },
    });
    state.agencyToken = res.access_token;
    state.agency = res.agency;
    sessionStorage.setItem("agency_token", res.access_token);
    enterAgencyMode();
  } catch (e) {
    $("agencyErr").textContent = e.message;
  }
};

async function enterAgencyMode() {
  $("agencyLogin").classList.add("hidden");
  $("agencyPanel").classList.remove("hidden");
  try {
    const me = await api("/agency/me", { token: state.agencyToken });
    state.agency = me;
    $("agencyBox").innerHTML = `<b>${esc(me.name)}</b> · <span class="mono">${esc(me.id)}</span>`;
    $("webhookUrl").value = me.webhook_url || "";
  } catch (e) {
    agencyLogout();
  }
}

$("webhookSave").onclick = async () => {
  $("webhookMsg").textContent = "";
  try {
    const res = await api("/agency/webhook", {
      method: "PUT",
      token: state.agencyToken,
      body: { webhook_url: $("webhookUrl").value.trim() },
    });
    $("webhookMsg").textContent = "webhook saved ✓";
  } catch (e) {
    $("webhookMsg").style.color = "var(--bad)";
    $("webhookMsg").textContent = e.message;
  }
};

$("pullBtn").onclick = async () => {
  const box = $("pullResult");
  const consentId = $("consentSelect").value;
  if (!consentId) { box.textContent = "select a consent first"; return; }
  box.textContent = "pulling…";
  try {
    const res = await api(`/agency/addresses/${consentId}`, { token: state.agencyToken });
    box.textContent = JSON.stringify(res, null, 2);
  } catch (e) {
    box.textContent = `⛔ ${e.message}`;
  }
};

function agencyLogout() {
  state.agencyToken = null;
  state.agency = null;
  sessionStorage.removeItem("agency_token");
  $("agencyPanel").classList.add("hidden");
  $("agencyLogin").classList.remove("hidden");
}
$("agencyLogoutBtn").onclick = agencyLogout;

/* ---------------- Live feed + polling ---------------- */

function renderState(s) {
  state.latest = s;

  // agency login dropdown
  const sel = $("agencySelect");
  if (sel.options.length !== s.agencies.length) {
    sel.innerHTML = s.agencies
      .map((a) => `<option value="${esc(a.id)}">${esc(a.name)}</option>`)
      .join("");
    sel.onchange = () => {
      const key = s.demo_credentials?.agencies?.[sel.value];
      if (key) $("apiKeyInput").value = key;
    };
    if (!s.demo_credentials && s.agencies[0]) sel.dispatchEvent(new Event("change"));
  }

  // prefill demo creds once
  if (s.demo_credentials && !$("aadhaarInput").value) {
    $("aadhaarInput").value = s.demo_credentials.aadhaar_number;
    $("apiKeyInput").value =
      s.demo_credentials.agencies[$("agencySelect").value] || "";
  }

  // pull dropdown: consents belonging to the logged-in agency
  if (state.agencyToken && state.agency) {
    const mine = s.consents.filter((c) => c.agency_id === state.agency.id);
    $("consentSelect").innerHTML = mine.length
      ? mine
          .map(
            (c) =>
              `<option value="${esc(c.id)}">${esc(c.id.slice(0, 8))} · ${esc(c.status)} · ${esc(c.purpose)}</option>`
          )
          .join("")
      : `<option value="">no consents yet</option>`;
  }

  // events table
  $("eventsBody").innerHTML = s.events.length
    ? s.events
        .map(
          (e) => `<tr>
            <td class="muted">${timeAgo(e.created_at)}</td>
            <td class="mono">${esc(e.type)}<br><span class="muted">${esc(e.id.slice(0, 8))}${e.attempts > 1 ? ` · try ${e.attempts}` : ""}${e.last_error ? ` · ${esc(e.last_error).slice(0, 40)}` : ""}</span></td>
            <td class="mono">${esc(e.agency_id)}</td>
            <td><span class="chip ${esc(e.status)}">${esc(e.status)}</span></td>
          </tr>`
        )
        .join("")
    : `<tr><td colspan="4" class="muted">no events yet</td></tr>`;

  // receipts table
  $("receiptsBody").innerHTML = s.receipts.length
    ? s.receipts
        .map(
          (r) => `<tr>
            <td class="muted">${timeAgo(r.received_at)}</td>
            <td class="mono">${esc(r.agency_id)}</td>
            <td class="mono">${esc(r.type || "?")}<br><span class="muted">${esc((r.event_id || "").slice(0, 8))}</span></td>
            <td>${r.signature_valid ? "✅ valid" : "⚠️ invalid"}</td>
          </tr>`
        )
        .join("")
    : `<tr><td colspan="4" class="muted">nothing received yet</td></tr>`;
}

async function poll() {
  try {
    renderState(await api("/demo/state"));
    if (state.citizenToken) await refreshCitizen();
  } catch (_) { /* server restarting */ }
}

/* ---------------- Reset ---------------- */

$("resetBtn").onclick = async () => {
  if (!confirm("Wipe all data and reseed?")) return;
  citizenLogout();
  agencyLogout();
  await api("/demo/reset", { method: "POST" });
  poll();
};

/* ---------------- boot ---------------- */

(async () => {
  await poll();
  if (state.citizenToken) await enterCitizenMode();
  if (state.agencyToken) await enterAgencyMode();
  setInterval(poll, 1500);
})();
