/* AddressSync v2 demo page. Vanilla JS, polls /demo/state for live updates. */

const $ = (id) => document.getElementById(id);
const state = {
  citizenToken: sessionStorage.getItem("citizen_token") || null,
  citizen: null,
  agencyToken: sessionStorage.getItem("agency_token") || null,
  agency: null,
  latest: null,
  log: { q: "", actor: "all", seen: new Set(), ready: false },
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

const fmtDT = (iso) =>
  iso
    ? new Date(iso.endsWith("Z") ? iso : iso + "Z").toLocaleString(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
      })
    : "—";

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
    // once the agency has acted (confirmed/rejected) the consent is archived:
    // read-only, no citizen actions left
    const archived = c.status === "confirmed" || c.status === "rejected";
    const row = document.createElement("div");
    row.className = "consentItem" + (archived ? " archived" : "");
    const meta = [];
    if (c.created_at) meta.push(`sent ${fmtDT(c.created_at)}`);
    if (c.handled_at) meta.push(`action ${fmtDT(c.handled_at)}`);
    if (c.handle_id) meta.push(`ref ${esc(c.handle_id.slice(0, 8))}…`);
    if (c.remark) meta.push(esc(c.remark));
    row.innerHTML =
      `<span class="mono">${esc(c.agency_id)}</span>` +
      `<span class="chip ${esc(c.status)}">${esc(c.status)}</span>` +
      `<span class="mono muted">${esc(c.id.slice(0, 8))}</span>` +
      `<span class="muted">${meta.join(" · ") || "&nbsp;"}</span>`;
    if (!archived) {
      const btn = document.createElement("button");
      btn.className = "btn small primary";
      btn.textContent = "Cancel Request";
      btn.onclick = async () => {
        $("consentErr").textContent = "";
        try {
          await api(`/citizen/consents/${c.agency_id}`, {
            method: "DELETE", token: state.citizenToken,
          });
          refreshCitizen();
        } catch (e) {
          $("consentErr").textContent = e.message;
        }
      };
      row.appendChild(btn);
    }
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

  // pull dropdown: pending (for review) + confirmed consents of the logged-in agency
  if (state.agencyToken && state.agency) {
    const mine = s.consents.filter(
      (c) =>
        c.agency_id === state.agency.id &&
        (c.status === "pending" || c.status === "confirmed")
    );
    $("consentSelect").innerHTML = mine.length
      ? mine
          .map(
            (c) =>
              `<option value="${esc(c.id)}">${c.status === "pending" ? "⏳ " : ""}${esc(c.id.slice(0, 8))} · ${esc(c.purpose)}</option>`
          )
          .join("")
      : `<option value="">no consent requests yet</option>`;
  }

  // pending consents for agency action
  if (state.agencyToken && state.agency) {
    const pending = s.consents.filter(
      (c) => c.agency_id === state.agency.id && c.status === "pending"
    );
    const container = $("pendingConsents");
    if (!pending.length) {
      container.innerHTML = `<div class="empty">No pending requests</div>`;
    } else {
      container.innerHTML = pending
        .map((c) => {
          const reviewed = !!c.reviewed_at;
          return `<div class="consentItem">
            <span class="mono">${esc(c.id.slice(0, 8))}</span>
            <span class="muted">${esc(c.purpose)}</span>
            <span class="mono muted">${esc(c.citizen_ref || c.citizen_id?.slice(0, 8) || "")}</span>
            ${
              reviewed
                ? ""
                : `<span class="review-hint">pull the address to review first</span>`
            }
            <button class="btn small success" data-action="confirm" data-id="${esc(c.id)}" ${reviewed ? "" : "disabled"}>Confirm</button>
            <button class="btn small danger" data-action="reject" data-id="${esc(c.id)}" ${reviewed ? "" : "disabled"}>Reject</button>
          </div>`;
        })
        .join("");
      container.querySelectorAll("button[data-action]").forEach((btn) => {
        btn.onclick = async () => {
          const id = btn.dataset.id;
          const action = btn.dataset.action;
          const endpoint = action === "confirm"
            ? `/agency/consents/${id}/confirm`
            : `/agency/consents/${id}/reject`;
          try {
            await api(endpoint, {
              method: "POST",
              token: state.agencyToken,
            });
            poll();
          } catch (e) {
            btn.textContent = `Error: ${e.message.slice(0, 30)}`;
          }
        };
      });
    }
  }

  // handled consent records for the logged-in agency
  if (state.agencyToken && state.agency) {
    const handled = s.consents.filter(
      (c) => c.agency_id === state.agency.id && c.handle_id
    );
    $("handledBody").innerHTML = handled.length
      ? handled
          .map(
            (c) => `<tr>
              <td class="muted">${timeAgo(c.handled_at)}</td>
              <td>${esc(c.citizen_name || "")}<br><span class="mono muted">${esc(c.citizen_ref || "")}</span></td>
              <td><span class="mono">${esc(c.id.slice(0, 8))}</span><br><span class="muted">${esc(c.purpose)}</span></td>
              <td class="mono" title="${esc(c.handle_id)}">${esc(c.handle_id.slice(0, 13))}…</td>
              <td><span class="chip ${esc(c.status)}">${esc(c.status)}</span></td>
            </tr>`
          )
          .join("")
      : `<tr><td colspan="5" class="muted">nothing handled yet</td></tr>`;
  }

  renderActivity(s);
}

/* ---------------- Live activity feed ---------------- */

const debounce = (fn, ms) => {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
};

const shortRef = (v) =>
  v
    ? `<span class="mono muted">${esc(String(v).slice(0, 8))}…</span>`
    : "";

function auditLine(a) {
  const who =
    a.actor || (a.actor_type === "system" ? "system" : a.actor_type || "system");
  const d = a.detail || {};
  const ref = shortRef(d.consent_id);
  switch (a.action) {
    case "otp.requested":
      return `<b>${esc(who)}</b> requested a login OTP`;
    case "login.otp_success":
      return `<b>${esc(who)}</b> logged in via OTP`;
    case "agency.registered":
      return `<b>${esc(a.actor_id)}</b> registered as an agency`;
    case "webhook.configured":
      return `<b>${esc(who)}</b> configured its webhook endpoint`;
    case "demo.reset":
      return `demo data reset`;
    case "consent.requested":
      return `<b>${esc(who)}</b> requested consent from <span class="mono">${esc(d.agency_id || "?")}</span> ${ref}`;
    case "consent.re_requested":
      return `<b>${esc(who)}</b> re-requested consent from <span class="mono">${esc(d.agency_id || "?")}</span> ${ref}`;
    case "consent.cancelled":
      return `<b>${esc(who)}</b> cancelled before any decision ${ref}`;
    case "address.pulled":
      return `<b>${esc(who)}</b> ${d.review ? "reviewed" : "pulled"} address v${d.version ?? "?"} ${ref}`;
    case "consent.confirmed":
      return `<b>${esc(who)}</b> confirmed · ref ${shortRef(d.handle_id)} ${ref}`;
    case "consent.rejected":
      return `<b>${esc(d.remark ? `${who} — ${d.remark}` : who)}</b> rejected the request ${ref}`;
    default:
      return `<b>${esc(who)}</b> ${esc(a.action)}`;
  }
}

function deliveryEntry(e, signatureById) {
  const signed = signatureById.get(e.id);
  const dot =
    e.status === "delivered" ? "ok"
    : e.status === "failed" ? "bad"
    : e.attempts > 1 ? "warn"
    : "";
  let html = `<b>${esc(e.type)}</b> → <span class="mono">${esc(e.agency_id)}</span>`;
  if (e.status === "delivered") {
    html += ` delivered ✓${signed === false ? " · ⚠ invalid signature" : ""}`;
  } else if (e.status === "failed") {
    html += ` failed ✗`;
  } else if (e.attempts > 1) {
    html += ` retrying (try ${e.attempts})`;
  } else {
    html += ` pending`;
  }
  if (e.last_error && e.status !== "delivered") {
    html += `<br><span class="muted mono">${esc(String(e.last_error).slice(0, 60))}</span>`;
  }
  return { id: `e:${e.id}`, ts: e.created_at, kind: "delivery", dot, html };
}

function renderActivity(s) {
  const box = $("logList");
  const q = state.log.q.trim().toLowerCase();
  const actor = state.log.actor;
  const signatureById = new Map(
    (s.receipts || []).map((r) => [r.event_id, r.signature_valid])
  );

  const items = [];
  (s.audit || []).forEach((a) =>
    items.push({
      id: `a:${a.id}`,
      ts: a.ts,
      kind: a.actor_type || "system",
      dot:
        a.actor_type === "citizen" ? "citizen"
        : a.actor_type === "agency" ? "agency"
        : "",
      html: auditLine(a),
    })
  );
  (s.events || []).forEach((e) => items.push(deliveryEntry(e, signatureById)));
  items.sort((x, y) => String(y.ts || "").localeCompare(String(x.ts || "")));

  const filtered = items.filter(
    (it) =>
      (actor === "all" || it.kind === actor) &&
      (!q ||
        it.html.replace(/<[^>]*>/g, " ").toLowerCase().includes(q))
  );

  if (!filtered.length) {
    box.innerHTML = `<div class="empty">nothing matches</div>`;
  } else {
    box.innerHTML = filtered
      .map((it) => {
        const fresh = state.log.ready && !state.log.seen.has(it.id);
        state.log.seen.add(it.id);
        return `<div class="logrow${fresh ? " fresh" : ""}">
          <span class="logdot ${it.dot}"></span>
          <span class="logtime">${timeAgo(it.ts)}</span>
          <span class="logmsg">${it.html}</span>
        </div>`;
      })
      .join("");
  }
  state.log.ready = true;
}

$("logSearch").addEventListener(
  "input",
  debounce(() => {
    state.log.q = $("logSearch").value;
    if (state.latest) renderActivity(state.latest);
  }, 150)
);

document.querySelectorAll("#actorPills .pill").forEach((pill) => {
  pill.onclick = () => {
    document
      .querySelectorAll("#actorPills .pill")
      .forEach((p) => p.classList.remove("active"));
    pill.classList.add("active");
    state.log.actor = pill.dataset.actor;
    if (state.latest) renderActivity(state.latest);
  };
});

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
