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
