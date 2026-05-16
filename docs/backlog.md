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
- [x] Review/merge

### Status
DONE

## [TASK-2] Integracja z rejestr.io po NIP

### Cel biznesowy
Po wpisaniu NIP użytkownik automatycznie pobiera podstawowe dane organizacji z rejestr.io, co przyspiesza identyfikację podmiotu do analizy konkurencji.

### Zakres

- [x] Dodanie konfiguracji klucza API w zmiennych środowiskowych (`REJESTR_IO_API_KEY`).
- [x] Dodanie konfiguracji URL endpointu (`REJESTR_IO_BASE_URL`, domyślnie `https://rejestr.io/api/v2`).
- [x] Integracja backendu z endpointem `GET /podstawowe-dane-organizacji` rejestr.io.
- [x] Przekazanie NIP z formularza do backendu i wywołanie API rejestr.io.
- [x] Mapowanie odpowiedzi z rejestr.io do modelu odpowiedzi aplikacji.
- [x] Dodanie informacji o statusie KRD (jeśli dostępny w odpowiedzi rejestr.io) do danych zwracanych na frontend.
- [x] Obsługa błędów: brak klucza API, timeout, 4xx/5xx z API zewnętrznego.
- [x] Prezentacja pobranych danych firmy na froncie po poprawnym zapytaniu.

### Minimalny zakres danych do odczytu

- [x] NIP
- [x] Nazwa organizacji
- [x] Status podmiotu (jeśli dostępny w odpowiedzi)
- [x] Miasto / adres (jeśli dostępne w odpowiedzi)
- [x] Informacja o KRD (jeśli dostępna w odpowiedzi)

### Poza zakresem

- Zapisywanie danych do PostgreSQL.
- Cache odpowiedzi z rejestr.io.
- Mechanizm retry z kolejką asynchroniczną.
- Integracje z innymi rejestrami poza rejestr.io.

### Kryteria akceptacji (AC)

- [x] Użytkownik wpisuje poprawny NIP i wysyła formularz.
- [x] Backend wywołuje rejestr.io z kluczem API z ENV.
- [x] Dla poprawnego NIP API aplikacji zwraca dane organizacji.
- [x] Frontend wyświetla pobrane dane organizacji użytkownikowi.
- [x] Frontend wyświetla informację o KRD, jeśli została zwrócona przez API.
- [x] Dla błędu API zewnętrznego użytkownik widzi czytelny komunikat.
- [x] Dla braku klucza API system zwraca kontrolowany błąd konfiguracyjny.

### Definition of Done (DoD)

- [x] Konfiguracja ENV (`REJESTR_IO_API_KEY`, `REJESTR_IO_BASE_URL`)
- [x] Kod backendu integracji z rejestr.io
- [x] Integracja endpointu aplikacji z wywołaniem po NIP
- [x] Aktualizacja frontendu (prezentacja danych organizacji)
- [x] Testy unit (walidacja i mapowanie odpowiedzi)
- [x] Testy integracyjne (mock rejestr.io)
- [x] Aktualizacja dokumentacji
- [ ] Review/merge

### Status
IN PROGRESS

## [TASK-3] Test połączenia z OpenAI API (GUI)

### Cel biznesowy
Potwierdzenie, że aplikacja ma poprawnie skonfigurowane połączenie z OpenAI API i że użytkownik widzi w GUI wynik testu połączenia.

### Zakres

- [ ] Dodanie konfiguracji klucza OpenAI w zmiennych środowiskowych (`OPENAI_API_KEY`).
- [ ] Dodanie konfiguracji URL API (`OPENAI_BASE_URL`, domyślnie `https://api.openai.com/v1`).
- [ ] Dodanie prostego endpointu backendu do testu połączenia z OpenAI.
- [ ] Wywołanie minimalnego requestu do OpenAI potwierdzającego dostępność API.
- [ ] Obsługa błędów: brak klucza, timeout, 4xx/5xx z OpenAI.
- [ ] Prezentacja wyniku testu połączenia w GUI (success/error).

### Minimalny zakres danych do odczytu

- [ ] Status połączenia (`OK` / `ERROR`)
- [ ] Komunikat techniczny (skrót odpowiedzi lub błąd)

### Poza zakresem

- Generowanie analizy konkurencji przez AI.
- Budowanie promptów biznesowych.
- Zapisywanie historii zapytań do OpenAI.
- Fine-tuning / RAG.

### Kryteria akceptacji (AC)

- [ ] System odczytuje `OPENAI_API_KEY` z ENV i nie loguje klucza.
- [ ] Endpoint testowy zwraca `OK` dla poprawnej konfiguracji i dostępnego API.
- [ ] Frontend pokazuje wynik testu połączenia (success/error).
- [ ] Dla błędu OpenAI użytkownik widzi czytelny komunikat.
- [ ] Dla braku klucza API system zwraca kontrolowany błąd konfiguracyjny.

### Definition of Done (DoD)

- [ ] Konfiguracja ENV (`OPENAI_API_KEY`, `OPENAI_BASE_URL`)
- [ ] Kod backendu integracji z OpenAI API
- [ ] Endpoint API testu połączenia
- [ ] Aktualizacja frontendu (przycisk/sekcja testu połączenia)
- [ ] Testy unit/integracyjne endpointu testowego (mock OpenAI API)
- [ ] Testy integracyjne (mock OpenAI API)
- [ ] Aktualizacja dokumentacji
- [ ] Review/merge

### Status
TODO
