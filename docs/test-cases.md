# Test Cases

## TASK-1: Prosta aplikacja z inputem nazwy firmy

### [x] TC-001 - Wyświetlenie formularza
Cel: Potwierdzenie, że użytkownik widzi jedno pole na nazwę firmy i przycisk zapisu.
Kroki:
1. Otwórz stronę aplikacji.
2. Sprawdź sekcję formularza.
Oczekiwany rezultat:
- Widoczne jest jedno pole input `nazwa firmy`.
- Widoczny jest przycisk zapisu.

### [x] TC-002 - Poprawny zapis nazwy firmy
Cel: Weryfikacja poprawnego zapisu danych przez API i prezentacji na stronie.
Kroki:
1. Wpisz poprawną nazwę firmy, np. `Acme Sp. z o.o.`.
2. Kliknij przycisk zapisu.
Oczekiwany rezultat:
- Frontend wysyła `POST /api/company`.
- API zwraca status `201`.
- Zapisana nazwa pojawia się w tabeli na stronie.

### [x] TC-003 - Walidacja pola pustego
Cel: Sprawdzenie walidacji wymaganego pola.
Kroki:
1. Pozostaw pole `nazwa firmy` puste.
2. Kliknij przycisk zapisu.
Oczekiwany rezultat:
- API odrzuca żądanie (status błędu walidacji).
- Użytkownik widzi czytelny komunikat o wymaganym polu.
- W tabeli nie pojawia się nowy rekord.

### [x] TC-004 - Usuwanie spacji z początku i końca
Cel: Sprawdzenie normalizacji danych wejściowych.
Kroki:
1. Wpisz wartość z nadmiarowymi spacjami, np. `   Acme   `.
2. Kliknij przycisk zapisu.
Oczekiwany rezultat:
- Backend trimuje wartość do `Acme`.
- API zwraca status `201`.
- W tabeli i odpowiedzi API widoczna jest wartość bez zewnętrznych spacji.

### [x] TC-005 - Limit długości 200 znaków (wartość graniczna poprawna)
Cel: Potwierdzenie akceptacji wartości o długości dokładnie 200 znaków.
Kroki:
1. Wpisz nazwę firmy o długości 200 znaków.
2. Kliknij przycisk zapisu.
Oczekiwany rezultat:
- API zwraca status `201`.
- Rekord zapisuje się poprawnie.

### [x] TC-006 - Przekroczenie limitu długości
Cel: Sprawdzenie odrzucenia wartości powyżej 200 znaków.
Kroki:
1. Wpisz nazwę firmy o długości 201 znaków.
2. Kliknij przycisk zapisu.
Oczekiwany rezultat:
- API odrzuca żądanie (status błędu walidacji).
- Użytkownik widzi czytelny komunikat o przekroczeniu limitu.
- Brak zapisu nowego rekordu.

### [x] TC-007 - Obsługa błędu backendu/API
Cel: Weryfikacja czytelnego błędu po stronie użytkownika przy awarii zapisu.
Kroki:
1. Zasymuluj błąd API (np. niedostępny backend).
2. Wyślij formularz z poprawną nazwą firmy.
Oczekiwany rezultat:
- Użytkownik otrzymuje czytelny komunikat błędu.
- Aplikacja nie zawiesza się i umożliwia ponowną próbę.

### [x] TC-008 - Test jednostkowy walidacji (backend)
Cel: Potwierdzenie reguł walidacji w testach automatycznych.
Kroki:
1. Uruchom testy jednostkowe walidacji.
2. Zweryfikuj przypadki: puste pole, trim, 200 znaków, 201 znaków.
Oczekiwany rezultat:
- Wszystkie testy walidacji przechodzą zgodnie z założeniami TASK-1.

## TASK-2: Integracja z rejestr.io po NIP

### [ ] TC-201 - Poprawne pobranie danych organizacji po NIP
Cel: Potwierdzenie, że poprawny NIP zwraca dane organizacji z rejestr.io.
Kroki:
1. Wpisz poprawny NIP istniejącej firmy.
2. Wyślij formularz.
Oczekiwany rezultat:
- Backend wywołuje endpoint `rejestr.io/api/info/podstawowe-dane-organizacji`.
- API aplikacji zwraca dane organizacji.
- Frontend wyświetla dane organizacji.
- Frontend wyświetla informację o KRD (jeśli obecna w odpowiedzi).

### [x] TC-209 - Obsługa informacji o KRD
Cel: Weryfikacja poprawnego mapowania i prezentacji informacji KRD.
Kroki:
1. Zasymuluj odpowiedź rejestr.io zawierającą pole dotyczące KRD.
2. Wyślij formularz z poprawnym NIP.
Oczekiwany rezultat:
- API aplikacji zwraca informację o KRD w ustandaryzowanym polu.
- Frontend pokazuje informację KRD w sekcji danych organizacji.

### [x] TC-202 - Brak klucza API w konfiguracji
Cel: Weryfikacja zachowania przy błędnej konfiguracji środowiska.
Kroki:
1. Uruchom backend bez `REJESTR_IO_API_KEY`.
2. Wyślij zapytanie z poprawnym NIP.
Oczekiwany rezultat:
- API aplikacji zwraca kontrolowany błąd konfiguracji.
- Użytkownik widzi czytelny komunikat błędu.

### [x] TC-203 - Niepoprawny format NIP
Cel: Potwierdzenie walidacji danych wejściowych przed wywołaniem API zewnętrznego.
Kroki:
1. Wpisz NIP o niepoprawnym formacie (np. litery lub zła długość).
2. Wyślij formularz.
Oczekiwany rezultat:
- Backend odrzuca żądanie na walidacji.
- API rejestr.io nie jest wywoływane.
- Frontend pokazuje czytelny błąd walidacji.

### [x] TC-204 - NIP nieistniejący lub brak danych w rejestr.io
Cel: Sprawdzenie obsługi scenariusza, gdy API zewnętrzne nie znajduje danych.
Kroki:
1. Wpisz poprawny formalnie, ale nieistniejący NIP.
2. Wyślij formularz.
Oczekiwany rezultat:
- API aplikacji zwraca czytelną informację o braku danych.
- Frontend prezentuje komunikat bez awarii UI.

### [x] TC-205 - Timeout API rejestr.io
Cel: Weryfikacja odporności na opóźnienia po stronie API zewnętrznego.
Kroki:
1. Zasymuluj timeout podczas wywołania rejestr.io.
2. Wyślij formularz z poprawnym NIP.
Oczekiwany rezultat:
- Backend zwraca kontrolowany błąd timeout.
- Użytkownik widzi czytelny komunikat i może ponowić próbę.

### [x] TC-206 - Błąd 5xx z rejestr.io
Cel: Sprawdzenie obsługi awarii dostawcy zewnętrznego.
Kroki:
1. Zasymuluj odpowiedź 5xx z rejestr.io.
2. Wyślij formularz z poprawnym NIP.
Oczekiwany rezultat:
- Backend mapuje błąd zewnętrzny na kontrolowaną odpowiedź.
- Frontend pokazuje komunikat o chwilowej niedostępności usługi.

### [x] TC-207 - Test jednostkowy mapowania odpowiedzi
Cel: Potwierdzenie poprawnego mapowania pól z rejestr.io do modelu API aplikacji.
Kroki:
1. Uruchom testy unit dla funkcji mapującej odpowiedź.
2. Zweryfikuj przypadki pełnej i częściowej odpowiedzi.
Oczekiwany rezultat:
- Pola wymagane mapują się poprawnie.
- Braki pól opcjonalnych nie powodują wyjątku.

### [x] TC-208 - Test integracyjny z mockiem rejestr.io
Cel: Potwierdzenie działania przepływu end-to-end backendu bez zależności od realnego API.
Kroki:
1. Uruchom test integracyjny z mockowaną odpowiedzią rejestr.io.
2. Wyślij żądanie do endpointu aplikacji z NIP.
Oczekiwany rezultat:
- Endpoint aplikacji zwraca poprawny status i payload.
- Test nie wykonuje realnego połączenia sieciowego.
