# Backlog

## [TASK-1] Prosta aplikacja z inputem nazwy firmy

### Cel biznesowy
Użytkownik może wpisać nazwę firmy, zapisać ją w aplikacji i zobaczyć wynik w tabeli na stronie.

### Zakres

- [x] Przygotowanie prostej strony z jednym polem input: `nazwa firmy`.
- [x] Dodanie przycisku zapisu danych.
- [x] Walidacja podstawowa po stronie backendu:
  - pole wymagane,
  - usunięcie spacji z początku i końca,
  - maksymalna długość 200 znaków.
- [x] Przekazanie danych z frontendu do backendu przez endpoint `POST /api/company`.
- [x] Zwrócenie odpowiedzi API z zapisaną nazwą firmy.
- [x] Wyświetlenie zapisanej nazwy firmy w tabeli na stronie.
- [x] Wyświetlenie czytelnego komunikatu błędu w przypadku niepoprawnych danych.
- [x] Deployment aplikacji na Railway.

### Minimalny zakres danych do odczytu

- `nazwa firmy`.

### Poza zakresem

- Upload plików.
- Parsowanie XHTML/PDF.
- Integracje z zewnętrznymi aplikacjami.
- Zaawansowana analityka finansowa.
- Edycja i usuwanie danych.

### Kryteria akceptacji (AC)

- [x] Użytkownik widzi formularz z jednym polem nazwy firmy.
- [x] Użytkownik może wysłać poprawną nazwę firmy.
- [x] Backend waliduje wymagane pole oraz limit długości.
- [x] Dla poprawnych danych API zwraca status `201`.
- [x] Strona pokazuje zapisaną nazwę firmy w tabeli.
- [x] Dla pustej lub niepoprawnej wartości użytkownik widzi czytelny błąd.

### Definition of Done (DoD)

- [x] Kod frontendu
- [x] Kod backendu
- [x] Endpoint API `POST /api/company`
- [x] Walidacja danych wejściowych
- [x] Obsługa błędów użytkownika
- [x] Testy jednostkowe walidacji
- [x] Aktualizacja dokumentacji
- [ ] Review/merge

### Status
IN PROGRESS
