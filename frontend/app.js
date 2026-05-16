const API_BASE_URL =
  window.location.protocol === "file:"
    ? "http://127.0.0.1:8000"
    : "";

const form = document.getElementById("company-form");
const nameInput = document.getElementById("name");
const messageEl = document.getElementById("message");
const tableBody = document.getElementById("companies-table-body");

function showMessage(text, type) {
  messageEl.textContent = text;
  messageEl.className = `message ${type}`;
}

function addRow(company) {
  const row = document.createElement("tr");

  const idCell = document.createElement("td");
  idCell.textContent = String(company.id);

  const nameCell = document.createElement("td");
  nameCell.textContent = company.name;

  row.appendChild(idCell);
  row.appendChild(nameCell);
  tableBody.appendChild(row);
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

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage("", "");

  const payload = {
    name: nameInput.value,
  };

  try {
    const response = await fetch(`${API_BASE_URL}/api/company`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const body = await response.json();

    if (!response.ok) {
      throw new Error(body.detail || "Nie udało się zapisać firmy.");
    }

    addRow(body);
    form.reset();
    showMessage("Nazwa firmy zapisana poprawnie.", "success");
  } catch (error) {
    showMessage(error.message, "error");
  }
});

fetchCompanies();
