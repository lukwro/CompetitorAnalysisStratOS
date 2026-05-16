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

const competitorForm = document.getElementById("competitor-form");
const companyNameInput = document.getElementById("company-name");
const mainActivityInput = document.getElementById("main-activity");
const competitorLimitInput = document.getElementById("competitor-limit");
const competitorMessageEl = document.getElementById("competitor-message");
const competitorsTableBody = document.getElementById("competitors-table-body");

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
    const response = await fetch(`${API_BASE_URL}/api/company`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const contentType = response.headers.get("content-type") || "";
    let body;
    if (contentType.includes("application/json")) {
      body = await response.json();
    } else {
      body = { detail: (await response.text()) || "Nieznany błąd serwera." };
    }

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
    const response = await fetch(`${API_BASE_URL}/api/competitors/find`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const contentType = response.headers.get("content-type") || "";
    let body;
    if (contentType.includes("application/json")) {
      body = await response.json();
    } else {
      body = { detail: (await response.text()) || "Nieznany błąd serwera." };
    }

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

fetchCompanies();

