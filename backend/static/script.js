let userToken = localStorage.getItem("userToken") || "";
let agencyToken = localStorage.getItem("agencyToken") || "";
let currentUser = null;
const API_BASE = "http://localhost:8000";

// Demo data from test script
const DEMO_AGENCIES = [
  {
    id: "municipal_bangalore",
    name: "Bangalore Municipal Corporation",
    email: "bmc@bangalore.gov.in",
    password: "BMC@12345",
  },
  {
    id: "municipal_mumbai",
    name: "Mumbai Municipal Corporation",
    email: "mmc@mumbai.gov.in",
    password: "MMC@12345",
  },
  {
    id: "municipal_delhi",
    name: "Delhi Municipal Corporation",
    email: "dmc@delhi.gov.in",
    password: "DMC@12345",
  },
];

const DEMO_USERS = [
  {
    aadhaar: "123456789012",
    name: "Rajesh Kumar",
    password: "Rajesh@1234",
  },
  {
    aadhaar: "234567890123",
    name: "Priya Sharma",
    password: "Priya@1234",
  },
  { aadhaar: "345678901234", name: "Amit Patel", password: "Amit@1234" },
  { aadhaar: "456789012345", name: "Neha Gupta", password: "Neha@1234" },
];

// Show toast notification
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = "slideOut 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// API call with better error handling
async function apiCall(method, endpoint, data = null, token = null) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const options = { method, headers };
  if (data) options.body = JSON.stringify(data);

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    let result;
    try {
      result = await response.json();
    } catch (e) {
      result = { error: "Server returned invalid response" };
    }
    return { status: response.status, data: result };
  } catch (error) {
    showToast("Network error: " + error.message, "error");
    return { status: 500, data: { error: error.message } };
  }
}

function renderAgenciesList() {
  const container = document.getElementById("agencies-list");
  if (!container) return;

  container.innerHTML = DEMO_AGENCIES.map(
    (agency) => `
                <div class="agency-item" onclick="selectAgency('${agency.id}', '${agency.name}')">
                    <div class="agency-name">🏢 ${agency.name}</div>
                    <div class="agency-id">ID: ${agency.id}</div>
                </div>
            `,
  ).join("");
}

function selectAgency(agencyId, agencyName) {
  document.getElementById("selected-agency").value =
    `${agencyName} (${agencyId})`;
  document.getElementById("selected-agency").dataset.agencyId = agencyId;
  showToast(`Selected: ${agencyName}`, "info");
}

function switchAgency(agencyId) {
  const agency = DEMO_AGENCIES.find((a) => a.id === agencyId);
  if (agency) {
    document.getElementById("org-id").value = agency.id;
    document.getElementById("org-password").value = agency.password;
    showToast(`Switched to ${agency.name}`, "info");
  }
}

function renderRequestList(
  requests,
  containerId,
  showActions = false,
  onApprove = null,
  onReject = null,
) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!requests || requests.length === 0) {
    container.innerHTML =
      '<p style="color: #666; text-align: center;">No requests found</p>';
    return;
  }

  container.innerHTML = requests
    .map(
      (req) => `
                <div class="request-item">
                    <div class="request-header">
                        <span class="request-id">🔖 ID: ${req.id}</span>
                        <span class="status-badge status-${req.status}">${req.status.toUpperCase()}</span>
                    </div>
                    <div class="request-details">
                        ${req.user_name ? `<div>👤 User: ${req.user_name} (${req.user_aadhaar})</div>` : ""}
                        ${req.user_aadhaar && !req.user_name ? `<div>👤 User: ${req.user_aadhaar}</div>` : ""}
                        ${req.agency_id ? `<div>🏢 Agency: ${req.agency_id}</div>` : ""}
                        <div>📍 New Address: ${req.new_address}</div>
                        ${req.reason ? `<div>📝 Reason: ${req.reason}</div>` : ""}
                        <div>📅 Created: ${new Date(req.created_at).toLocaleString()}</div>
                    </div>
                    ${
                      showActions && req.status === "pending"
                        ? `
                        <div style="margin-top: 10px;">
                            <button class="success" onclick="updateRequestStatus('${req.id}', 'approved', '')" style="margin-right: 5px;">✓ Approve</button>
                            <button class="danger" onclick="rejectRequest('${req.id}')">✗ Reject</button>
                        </div>
                    `
                        : ""
                    }
                </div>
            `,
    )
    .join("");
}

// ============ USER FUNCTIONS ============
async function loginUser() {
  const data = {
    aadhaar_number: document.getElementById("req-aadhaar").value,
    password: document.getElementById("req-password").value,
  };
  const response = await apiCall("POST", "/users/login", data);

  if (response.status === 200 && response.data.access_token) {
    userToken = response.data.access_token;
    localStorage.setItem("userToken", userToken);
    document.getElementById("req-token-info").style.display = "block";
    document.getElementById("req-token-display").textContent = userToken;
    document.getElementById("req-user-name").textContent =
      response.data.user?.name || "User";
    showToast("Login successful!", "success");
    loadMyRequests();
  } else {
    showToast(
      "Login failed: " + (response.data?.detail || "Invalid credentials"),
      "error",
    );
  }
}

async function createRequest() {
  if (!userToken) {
    showToast("Please login first", "error");
    return;
  }

  const agencyInput = document.getElementById("selected-agency");
  let agencyId = agencyInput.dataset.agencyId;

  if (!agencyId) {
    agencyId = document.getElementById("manual-agency-id").value;
    if (!agencyId) {
      showToast("Please select an agency", "error");
      return;
    }
  }

  const newAddress = document.getElementById("req-new-address").value;
  if (!newAddress) {
    showToast("Please enter new address", "error");
    return;
  }

  const data = { agency_id: agencyId, new_address: newAddress };
  const response = await apiCall("POST", "/requests/create", data, userToken);

  if (response.status === 200) {
    showToast("Request created successfully!", "success");
    loadMyRequests();
  } else {
    showToast(
      "Failed to create request: " + (response.data?.detail || "Unknown error"),
      "error",
    );
  }
}

async function loadMyRequests() {
  if (!userToken) return;
  const response = await apiCall(
    "GET",
    "/requests/my-requests",
    null,
    userToken,
  );
  if (response.status === 200 && response.data) {
    renderRequestList(response.data, "my-requests-list");
  }
}

// ============ AGENCY FUNCTIONS ============
async function loginAgency() {
  const data = {
    id: document.getElementById("org-id").value,
    password: document.getElementById("org-password").value,
  };
  const response = await apiCall("POST", "/agencies/login", data);

  if (response.status === 200 && response.data.access_token) {
    agencyToken = response.data.access_token;
    localStorage.setItem("agencyToken", agencyToken);
    document.getElementById("org-token-info").style.display = "block";
    document.getElementById("org-token-display").textContent = agencyToken;
    document.getElementById("org-name-display").textContent =
      response.data.agency?.name || "Agency";
    showToast("Login successful!", "success");
    loadPendingRequests();
    loadAgencyRequests();
  } else {
    showToast(
      "Login failed: " + (response.data?.detail || "Invalid credentials"),
      "error",
    );
  }
}

async function updateRequestStatus(requestId, status, reason) {
  if (!agencyToken) {
    showToast("Please login as agency first", "error");
    return;
  }

  const data = { status };
  if (reason) data.reason = reason;

  const response = await apiCall(
    "PUT",
    `/requests/${requestId}`,
    data,
    agencyToken,
  );

  if (response.status === 200) {
    showToast(`Request ${status}!`, "success");
    loadPendingRequests();
    loadAgencyRequests();
    loadAllRequests();
  } else {
    showToast(`Failed to ${status} request`, "error");
  }
}

function rejectRequest(requestId) {
  const reason = prompt(
    "Enter reason for rejection:",
    "Invalid address format",
  );
  if (reason && reason.trim()) {
    updateRequestStatus(requestId, "rejected", reason);
  } else if (reason === "") {
    showToast("Please provide a reason for rejection", "warning");
  }
}

async function loadPendingRequests() {
  if (!agencyToken) return;
  const response = await apiCall(
    "GET",
    "/requests/pending-requests",
    null,
    agencyToken,
  );
  if (response.status === 200 && response.data) {
    renderRequestList(response.data, "pending-requests-list", true);
  }
}

async function loadAgencyRequests() {
  if (!agencyToken) return;
  const response = await apiCall(
    "GET",
    "/requests/agency-requests",
    null,
    agencyToken,
  );
  if (response.status === 200 && response.data) {
    renderRequestList(response.data, "agency-requests-list");
  }
}

// ============ GLOBAL REQUESTS ============
async function loadAllRequests() {
  const status = document.getElementById("global-status-filter").value;

  if (agencyToken) {
    const endpoint = status
      ? `/requests/agency-requests?status=${status}`
      : "/requests/agency-requests";
    const response = await apiCall("GET", endpoint, null, agencyToken);
    if (response.status === 200 && response.data) {
      renderRequestList(response.data, "all-requests-list");
    }
  } else if (userToken) {
    const response = await apiCall(
      "GET",
      "/requests/my-requests",
      null,
      userToken,
    );
    if (response.status === 200 && response.data) {
      renderRequestList(response.data, "all-requests-list");
    }
  } else {
    document.getElementById("all-requests-list").innerHTML =
      '<p style="color: #666; text-align: center;">Please login as user or agency to view requests</p>';
  }
}

function switchTab(tab) {
  document
    .querySelectorAll(".tab")
    .forEach((t) => t.classList.remove("active"));
  document
    .querySelectorAll(".tab-content")
    .forEach((c) => c.classList.remove("active"));

  if (tab === "requester") {
    document.querySelectorAll(".tab")[0].classList.add("active");
    document.getElementById("requester-tab").classList.add("active");
    renderAgenciesList();
    if (userToken) loadMyRequests();
  } else if (tab === "organization") {
    document.querySelectorAll(".tab")[1].classList.add("active");
    document.getElementById("organization-tab").classList.add("active");
    if (agencyToken) {
      loadPendingRequests();
      loadAgencyRequests();
    }
  } else {
    document.querySelectorAll(".tab")[2].classList.add("active");
    document.getElementById("requests-tab").classList.add("active");
    loadAllRequests();
  }
}

// Initialize
renderAgenciesList();

if (userToken) {
  document.getElementById("req-token-info").style.display = "block";
  document.getElementById("req-token-display").textContent = userToken;
  loadMyRequests();
}
if (agencyToken) {
  document.getElementById("org-token-info").style.display = "block";
  document.getElementById("org-token-display").textContent = agencyToken;
}
