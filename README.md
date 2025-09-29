# SEC
# README

## Opis projektu

Ten skrypt w Pythonie służy do pobierania i przetwarzania danych finansowych (aktualnie przychodów) wybranych spółek publicznych z bazy amerykańskiego regulatora SEC (Securities and Exchange Commission).

## Funkcjonalności

1. **Pobranie listy spółek z tickera i ich CIK (Centralny Identyfikator Podmiotu)**
   - Pobiera aktualne tickery spółek i odpowiadające im numery CIK z API SEC.
   - Ostrzega, jeśli wybrane tickery nie zostały poprawnie pobrane.
2. **Definicja fraz odpowiadających przychodom**
   - Lista zmiennych (frazy kluczowe), które mogą zawierać dane przychodowe w raportach spółek.
3. **Pobieranie danych finansowych z API SEC - xbrl/companyfacts**
   - Dla każdego CIK spółki pobiera dane dotyczące przychodów zgodnie z podanymi frazami.
   - Zapisuje dane w tymczasowej strukturze z dodatkowymi kolumnami (np. ticker).
   - Obsługuje sytuacje braku danych dla poszczególnych fraz.
4. **Wstępne czyszczenie danych**
   - Łączy dane z poszczególnych spółek, filtruje tylko interesujące raporty (10-K, 10-Q).
   - Usuwa dane z raportów półrocznych na podstawie długości okresu sprawozdawczego.
5. **Drugie czyszczenie danych i segmentacja**
   - Dzieli dane na roczne i kwartalne.
   - Usuwa duplikaty i dane półroczne.
   - Przekształca wyniki roczne na wartości kwartalne.
6. **Modyfikacja danych do formatu tabelarycznego gotowego do analizy**
   - Transponuje dane.
   - Zmienia nazwy kolumn.
   - Dodaje kolumnę z tickerem.
   - Porządkuje kolumny, usuwa zbędne elementy.
7. **Zapis wyników do pliku CSV w bieżącym katalogu**

## Jak uruchomić?

1. Upewnij się, że masz zainstalowane biblioteki:
   - requests
   - pandas
   - openpyxl (jeśli używasz Excel, choć w tym skrypcie nie ma zapisu do .xlsx)
2. Wklej kod do pliku `.py`.
3. Uruchom skrypt. Po pobraniu i przetworzeniu danych plik `DATA SEC.csv` zostanie zapisany w katalogu, z którego uruchomiłeś skrypt.

## Uwagi

- Kod zawiera podstawową obsługę błędów i komunikaty ułatwiające monitorowanie, które spółki i które dane zostały pobrane.
- Dane mogą wymagać dalszej analizy i walidacji, szczególnie dane finansowe przetwarzane z raportów SEC.
- Można rozszerzyć obsługę o inne parametry, typy sprawozdań lub dodatkowe metadane.
