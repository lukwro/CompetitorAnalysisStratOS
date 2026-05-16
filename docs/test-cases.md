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

## TASK-3: Test połączenia z OpenAI API (GUI)

### [ ] TC-301 - Poprawny test połączenia OpenAI
Cel: Potwierdzenie, że endpoint testowy poprawnie łączy się z OpenAI API.
Kroki:
1. Uruchom backend z poprawnym `OPENAI_API_KEY`.
2. Wywołaj endpoint testu połączenia.
Oczekiwany rezultat:
- Backend wywołuje OpenAI API.
- API aplikacji zwraca status `OK`.
- GUI wyświetla komunikat o poprawnym połączeniu.

### [ ] TC-302 - Brak klucza `OPENAI_API_KEY`
Cel: Weryfikacja zachowania przy braku konfiguracji API.
Kroki:
1. Uruchom backend bez `OPENAI_API_KEY`.
2. Wywołaj endpoint testu połączenia.
Oczekiwany rezultat:
- API aplikacji zwraca kontrolowany błąd konfiguracji.
- Użytkownik widzi czytelny komunikat.

### [ ] TC-303 - Timeout po stronie OpenAI API
Cel: Sprawdzenie odporności na opóźnienia API zewnętrznego.
Kroki:
1. Zasymuluj timeout wywołania OpenAI.
2. Wywołaj endpoint testu połączenia.
Oczekiwany rezultat:
- Backend zwraca kontrolowany błąd timeout.
- Frontend pokazuje komunikat i umożliwia ponowienie.

### [ ] TC-304 - Błąd 4xx/5xx z OpenAI API
Cel: Weryfikacja mapowania błędów dostawcy.
Kroki:
1. Zasymuluj odpowiedź 4xx lub 5xx z OpenAI API.
2. Wywołaj endpoint testu połączenia.
Oczekiwany rezultat:
- Backend zwraca kontrolowaną odpowiedź błędu.
- Frontend wyświetla czytelny komunikat.

### [ ] TC-305 - Test GUI wyniku połączenia
Cel: Potwierdzenie, że GUI prezentuje wynik testu połączenia.
Kroki:
1. W GUI uruchom test połączenia dla scenariusza success i error.
2. Sprawdź komunikaty w interfejsie.
Oczekiwany rezultat:
- Dla success GUI pokazuje pozytywny status.
- Dla error GUI pokazuje czytelny błąd.

### [ ] TC-306 - Test integracyjny z mockiem OpenAI API
Cel: Potwierdzenie przepływu endpointu testowego bez realnego połączenia do OpenAI.
Kroki:
1. Uruchom test integracyjny z mockowaną odpowiedzią OpenAI.
2. Wywołaj endpoint testu połączenia.
Oczekiwany rezultat:
- Endpoint zwraca poprawny status testu połączenia.
- Test nie wykonuje realnego połączenia sieciowego.

## TASK-4: Wyszukiwanie konkurencji po nazwie firmy i dominującej działalności

### [ ] TC-401 - Poprawne wyszukanie konkurentów
Cel: Potwierdzenie, że dla poprawnych danych wejściowych system zwraca listę konkurencji.
Kroki:
1. Podaj `company_name` i `main_activity` z realnym przypadkiem biznesowym.
2. Wywołaj `POST /api/competitors/find`.
Oczekiwany rezultat:
- API zwraca status `200`.
- Odpowiedź zawiera `input_company`, `input_main_activity`, `competitors[]`.
- Lista zawiera co najmniej 3 pozycje.

### [ ] TC-402 - Walidacja pustego `company_name`
Cel: Sprawdzenie walidacji wymaganego pola nazwy firmy.
Kroki:
1. Wywołaj endpoint z pustym `company_name`.
2. Ustaw poprawne `main_activity`.
Oczekiwany rezultat:
- API zwraca `400` (lub walidacyjny status zgodny z implementacją).
- Zwrócony jest czytelny komunikat walidacyjny.

### [ ] TC-403 - Walidacja pustego `main_activity`
Cel: Sprawdzenie walidacji wymaganego pola działalności.
Kroki:
1. Wywołaj endpoint z pustym `main_activity`.
2. Ustaw poprawne `company_name`.
Oczekiwany rezultat:
- API zwraca `400` (lub walidacyjny status zgodny z implementacją).
- Zwrócony jest czytelny komunikat walidacyjny.

### [ ] TC-404 - Walidacja długości pól wejściowych
Cel: Potwierdzenie limitów długości i ochrony przed zbyt długim inputem.
Kroki:
1. Wywołaj endpoint z `company_name` > 200 znaków.
2. Wywołaj endpoint z `main_activity` > 300 znaków.
Oczekiwany rezultat:
- API odrzuca oba żądania walidacją.
- Komunikaty wskazują przekroczenie limitów.

### [ ] TC-405 - Trimowanie wartości wejściowych
Cel: Potwierdzenie normalizacji danych wejściowych.
Kroki:
1. Wywołaj endpoint z wartościami zawierającymi spacje na początku i końcu.
2. Porównaj wartości wejściowe i wartości zwrócone w polach `input_*`.
Oczekiwany rezultat:
- Wartości są znormalizowane (bez zewnętrznych spacji).
- Przetwarzanie kończy się sukcesem dla poprawnych danych.

### [ ] TC-406 - Limit liczby wyników (domyślny)
Cel: Weryfikacja domyślnego limitu liczby zwracanych konkurentów.
Kroki:
1. Wywołaj endpoint bez parametru limitu.
2. Sprawdź długość `competitors[]`.
Oczekiwany rezultat:
- API zwraca maksymalnie domyślną liczbę wyników (np. 5).

### [ ] TC-407 - Limit liczby wyników (konfigurowalny zakres 3-10)
Cel: Potwierdzenie działania parametru limitu i jego walidacji.
Kroki:
1. Wywołaj endpoint z limitem w zakresie (np. 3 i 10).
2. Wywołaj endpoint z limitem poza zakresem (np. 2 i 11).
Oczekiwany rezultat:
- Dla wartości poprawnych API zwraca odpowiednią liczbę wyników.
- Dla wartości spoza zakresu API zwraca błąd walidacji.

### [ ] TC-408 - Poprawny format danych konkurenta
Cel: Potwierdzenie spójnego formatu odpowiedzi.
Kroki:
1. Wywołaj endpoint z poprawnym payloadem.
2. Zweryfikuj strukturę każdego wpisu w `competitors[]`.
Oczekiwany rezultat:
- Każdy wpis zawiera `name`, `similarity_reason`, `confidence`.
- Brak wymaganych pól skutkuje błędem mapowania/parsowania.

### [ ] TC-409 - Obsługa timeoutu OpenAI
Cel: Sprawdzenie odporności endpointu na timeout modelu.
Kroki:
1. Zasymuluj timeout po stronie klienta OpenAI.
2. Wywołaj endpoint `POST /api/competitors/find`.
Oczekiwany rezultat:
- API zwraca kontrolowany błąd timeout.
- Frontend pokazuje czytelny komunikat i umożliwia ponowienie.

### [ ] TC-410 - Obsługa błędu 4xx/5xx OpenAI
Cel: Weryfikacja mapowania błędów dostawcy modelu.
Kroki:
1. Zasymuluj odpowiedź 4xx i 5xx z OpenAI.
2. Wywołaj endpoint.
Oczekiwany rezultat:
- API zwraca kontrolowaną odpowiedź błędu.
- Komunikat nie ujawnia danych wrażliwych.

### [ ] TC-411 - Brak konfiguracji `OPENAI_API_KEY`
Cel: Weryfikacja zachowania systemu przy błędnej konfiguracji środowiska.
Kroki:
1. Uruchom backend bez `OPENAI_API_KEY`.
2. Wywołaj endpoint wyszukiwania konkurencji.
Oczekiwany rezultat:
- API zwraca kontrolowany błąd konfiguracyjny.
- Użytkownik otrzymuje czytelny komunikat.

### [ ] TC-412 - Brak konfiguracji `OPENAI_MODEL`
Cel: Potwierdzenie walidacji konfiguracji modelu wymaganego przez TASK-4.
Kroki:
1. Uruchom backend bez `OPENAI_MODEL`.
2. Wywołaj endpoint wyszukiwania konkurencji.
Oczekiwany rezultat:
- API zwraca kontrolowany błąd konfiguracji lub używa bezpiecznej wartości domyślnej (zgodnie z decyzją implementacyjną).
- Zachowanie jest udokumentowane i spójne.

### [ ] TC-413 - Błędny format odpowiedzi modelu
Cel: Sprawdzenie odporności parsera na niezgodny format odpowiedzi AI.
Kroki:
1. Zasymuluj odpowiedź OpenAI bez oczekiwanej struktury JSON.
2. Wywołaj endpoint.
Oczekiwany rezultat:
- API zwraca kontrolowany błąd parsowania/formatu.
- Brak nieobsłużonych wyjątków po stronie backendu.

### [ ] TC-414 - Test GUI prezentacji wyników konkurencji
Cel: Potwierdzenie, że frontend poprawnie pokazuje listę konkurentów.
Kroki:
1. W GUI uruchom wyszukiwanie dla scenariusza success.
2. Sprawdź widok listy/tabeli wyników.
Oczekiwany rezultat:
- Widoczne są nazwa konkurenta, uzasadnienie i poziom pewności.
- UI zachowuje czytelność dla wielu rekordów.

### [ ] TC-415 - Test GUI obsługi błędu wyszukiwania konkurencji
Cel: Potwierdzenie czytelnej obsługi błędów dla użytkownika końcowego.
Kroki:
1. W GUI uruchom wyszukiwanie dla scenariusza błędu (np. timeout).
2. Sprawdź komunikat błędu.
Oczekiwany rezultat:
- Użytkownik widzi zrozumiały komunikat.
- Aplikacja nie zawiesza się i pozwala na ponowną próbę.

### [ ] TC-416 - Test integracyjny endpointu z mockiem OpenAI
Cel: Potwierdzenie działania backendowego przepływu bez realnego połączenia sieciowego.
Kroki:
1. Uruchom test integracyjny z mockowaną odpowiedzią OpenAI.
2. Wywołaj `POST /api/competitors/find`.
Oczekiwany rezultat:
- Endpoint zwraca poprawny status i payload.
- Test nie wykonuje realnego połączenia do OpenAI.
