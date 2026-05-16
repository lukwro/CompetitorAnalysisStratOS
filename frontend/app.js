const API_BASE_URL =
  window.location.protocol === "file:"
    ? "http://127.0.0.1:8000"
    : "";

const form = document.getElementById("company-form");
const nipInput = document.getElementById("nip");
const messageEl = document.getElementById("message");
const tableBody = document.getElementById("companies-table-body");
const debugOutput = document.getElementById("debug-output");
const openAiTestBtn = document.getElementById("openai-connection-test-btn");
const openAiResultEl = document.getElementById("openai-connection-result");
const combinedFlowBtn = document.getElementById("combined-flow-btn");
const clearCompaniesBtn = document.getElementById("clear-companies-btn");

const competitorForm = document.getElementById("competitor-form");
const companyNameInput = document.getElementById("company-name");
const mainActivityInput = document.getElementById("main-activity");
const competitorLimitInput = document.getElementById("competitor-limit");
const competitorMessageEl = document.getElementById("competitor-message");
const competitorsTableBody = document.getElementById("competitors-table-body");
let isCombinedFlowRunning = false;

function showMessage(text, type) {
  messageEl.textContent = text;
  messageEl.className = `message ${type}`;
}

function showCompetitorMessage(text, type) {
  competitorMessageEl.textContent = text;
  competitorMessageEl.className = `message ${type}`;
}

function showDebug(debugData) {
  if (!debugData) {
    debugOutput.textContent = "Brak danych debug.";
    return;
  }
  debugOutput.textContent = JSON.stringify(debugData, null, 2);
}

function showOpenAiConnectionResult(text, type) {
  openAiResultEl.textContent = text;
  openAiResultEl.className = `message ${type}`;
}

function setCombinedFlowLoading(isLoading) {
  isCombinedFlowRunning = isLoading;
  combinedFlowBtn.disabled = isLoading;
  combinedFlowBtn.textContent = isLoading ? "Przetwarzanie..." : "Pobierz dane i znajdź konkurencję";
}

function addRow(company) {
  const row = document.createElement("tr");

  const cells = [
    String(company.id ?? ""),
    company.nip ?? "",
    company.organization_name ?? "-",
    company.organization_status ?? "-",
    company.predominant_activity ?? "-",
    company.city ?? "-",
    company.address ?? "-",
    company.krd_status ?? "-",
  ];

  cells.forEach((value) => {
    const cell = document.createElement("td");
    cell.textContent = value;
    row.appendChild(cell);
  });

  tableBody.appendChild(row);
}

function renderCompetitors(competitors) {
  competitorsTableBody.innerHTML = "";

  competitors.forEach((item) => {
    const row = document.createElement("tr");
    const cells = [item.name ?? "-", item.similarity_reason ?? "-", item.confidence ?? "-"];

    cells.forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.appendChild(cell);
    });

    competitorsTableBody.appendChild(row);
  });
}

async function readResponseBody(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return { detail: (await response.text()) || "Nieznany błąd serwera." };
}

async function postJson(path, payload) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  const body = await readResponseBody(response);
  return { response, body };
}

async function fetchCompanies() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/companies`);
    if (!response.ok) {
      throw new Error("Nie udało się pobrać danych.");
    }

    const companies = await response.json();
    tableBody.innerHTML = "";
    companies.forEach(addRow);
  } catch (error) {
    showMessage(error.message, "error");
  }
}

openAiTestBtn.addEventListener("click", async () => {
  showOpenAiConnectionResult("Trwa test połączenia z OpenAI...", "");

  try {
    const response = await fetch(`${API_BASE_URL}/api/openai/connection-test`);
    const contentType = response.headers.get("content-type") || "";
    let body;
    if (contentType.includes("application/json")) {
      body = await response.json();
    } else {
      body = { detail: (await response.text()) || "Nieznany błąd serwera." };
    }

    if (!response.ok) {
      throw new Error(body.detail || "Test połączenia OpenAI nie powiódł się.");
    }

    showOpenAiConnectionResult(`${body.status}: ${body.detail}`, "success");
  } catch (error) {
    showOpenAiConnectionResult(error.message, "error");
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage("", "");

  const payload = {
    nip: nipInput.value,
  };

  try {
    const { response, body } = await postJson("/api/company", payload);

    if (!response.ok) {
      showDebug({ request: { method: "POST", path: "/api/company", payload }, response: body });
      throw new Error(body.detail || "Nie udało się pobrać danych organizacji.");
    }

    addRow(body);
    showDebug(body.debug);
    form.reset();
    showMessage("Dane organizacji pobrane poprawnie.", "success");
  } catch (error) {
    showMessage(error.message, "error");
  }
});

competitorForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  showCompetitorMessage("Szukam konkurencji...", "");

  const limitValue = Number(competitorLimitInput.value);
  const payload = {
    company_name: companyNameInput.value,
    main_activity: mainActivityInput.value,
    limit: Number.isNaN(limitValue) ? undefined : limitValue,
  };

  try {
    const { response, body } = await postJson("/api/competitors/find", payload);

    if (!response.ok) {
      showDebug({ request: { method: "POST", path: "/api/competitors/find", payload }, response: body });
      throw new Error(body.detail || "Nie udało się wyszukać konkurencji.");
    }

    renderCompetitors(body.competitors || []);
    showCompetitorMessage("Lista konkurencji została wygenerowana.", "success");
  } catch (error) {
    showCompetitorMessage(error.message, "error");
  }
});

combinedFlowBtn.addEventListener("click", async () => {
  if (isCombinedFlowRunning) {
    return;
  }

  setCombinedFlowLoading(true);
  showMessage("Pobieram dane firmy...", "");
  showCompetitorMessage("", "");
  competitorsTableBody.innerHTML = "";

  const companyPayload = { nip: nipInput.value };
  try {
    const companyResult = await postJson("/api/company", companyPayload);
    if (!companyResult.response.ok) {
      showDebug({ request: { method: "POST", path: "/api/company", payload: companyPayload }, response: companyResult.body });
      throw new Error(companyResult.body.detail || "Nie udało się pobrać danych organizacji.");
    }

    addRow(companyResult.body);
    showDebug(companyResult.body.debug);
    showMessage("Dane firmy pobrane. Trwa wyszukiwanie konkurencji...", "success");

    const companyName = (companyResult.body.organization_name || "").trim();
    const mainActivityFallback = (mainActivityInput.value || "").trim();
    const mainActivity = (companyResult.body.predominant_activity || mainActivityFallback).trim();
    const limitValue = Number(competitorLimitInput.value);
    const competitorPayload = {
      company_name: companyName,
      main_activity: mainActivity,
      limit: Number.isNaN(limitValue) ? undefined : limitValue,
    };

    const competitorsResult = await postJson("/api/competitors/find", competitorPayload);
    if (!competitorsResult.response.ok) {
      showDebug({ request: { method: "POST", path: "/api/competitors/find", payload: competitorPayload }, response: competitorsResult.body });
      showCompetitorMessage(competitorsResult.body.detail || "Nie udało się wyszukać konkurencji.", "error");
      showMessage("Dane firmy pobrane, ale wyszukiwanie konkurencji nie powiodło się.", "error");
      return;
    }

    renderCompetitors(competitorsResult.body.competitors || []);
    showCompetitorMessage("Lista konkurencji została wygenerowana.", "success");
    showMessage("Proces zakończony sukcesem: pobrano dane i konkurencję.", "success");
  } catch (error) {
    showMessage(error.message, "error");
  } finally {
    setCombinedFlowLoading(false);
  }
});

clearCompaniesBtn.addEventListener("click", () => {
  tableBody.innerHTML = "";
  showMessage("Tabela firm została wyczyszczona.", "success");
});

fetchCompanies();

