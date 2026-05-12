# Test Cases

Dokumentacja przypadków testowych. 

Przykład 

TC-PARSE-XHTML-001: Parsowanie danych z pliku XHTML 
Given: plik backend/tests/fixtures/files/SF_INP_2024.xhtml zostal zapisany w systemie 
When: backend uruchamia parser XHTML/pdf2htmlEX dla zapisanego pliku Then: parser odczytuje tekst dokumentu, zapisuje rozpoznane metadane i co najmniej kilka pozycji finansowych do bazy Then: nierozpoznane pola nie przerywaja importu, a raport otrzymuje czytelny status parsowania