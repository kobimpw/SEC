import requests
import pandas as pd 
from openpyxl import workbook 

'-____________________________________________________________________________________________'
''' 1.opis funkcji
wysyłamy zapytanie do API SEC, aby pobrać CIK oraz tickery spółek
- zamieniamy dane na dataframe
- uzupełniamy CIK do 10 znaków
- wybieramy tickery, które nas interesują
- zmienna która docelowo bedzie wykorzystywana w nastepnych funkcjach to cik_wybrane oraz ticker_wybrany
'''
def sec():
    try:    
        import requests
        import pandas as pd 
        from openpyxl import workbook

        headers = {'user-Agent':'przyklad@gmail.com'}

        # tu się podłączyłem do danych 
        company_tickers = requests.get("https://www.sec.gov/files/company_tickers.json",headers = headers) 
        
        # zamiana danych na dateframe
        CompanyData = pd.DataFrame.from_dict(company_tickers.json(),orient='index')

        # uzupelnienie cik do 10 znakow
        CompanyData['cik_str'] = CompanyData['cik_str'].astype(str).str.zfill(10) 
        
        # wskazujemy tickery, które nas interesują
        tickery = ['AAPL','NVDA', 'MSFT','AMZN', "GOOGL",'META', 'TSLA']
        
        # zwróci numer wybranych tickera
        numer_ticker = CompanyData.index[CompanyData['ticker'].isin(tickery)].to_list() 
        
        # zwróci cik wybranych tickerów
        cik_wybrane = CompanyData.iloc[numer_ticker].cik_str 
        
        #cik apple w celach testowych
        cik_stary = CompanyData.iloc[2].cik_str

        # zwróci listę wybranych tickerów
        ticker_wybrany = CompanyData.iloc[numer_ticker].ticker



        # print(sorted(ticker_wybrany.to_list()))
        # print(sorted(tickery))

        #test czy tickery zostały pobrane poprawnie
        if sorted(tickery) == sorted(ticker_wybrany.to_list()):
            print('listy są takie same\nkontynuujemy wykonanie kodu\n')
        else:

            tickery_set = set(tickery)
            ticker_wybrany_set = set(ticker_wybrany.to_list())
            tylko_w_ticker = tickery_set - ticker_wybrany_set
            print(f'ERROR: listy są różne \nponiżej przedstawione elementy, których nie udało się pobrać:\n {tylko_w_ticker}\n')
            # print(tylko_w_ticker)
            return None, None, None, None

        #komuniakt jeśli udało się połączyć z API SEC
        print(f"podłączenie do API SEC zakończone sukcesem\nprzechodzimy do funkcji: pobieranie_danych\n")
        return headers, cik_stary, cik_wybrane, ticker_wybrany    
        
    except:
        print(f" ERROR: podłączenie do API SEC niepowiodło się")
        return None, None, None, None   
headers, cik_stary, cik_wybrane, ticker_wybrany = sec() 
'-____________________________________________________________________________________________'
#region : 2.przychody tu są przechowywane hasła pod, którymi mogą być przychody
'hasła pod, którymi mogą być przychody'
p1 = 'SalesRevenueNet'
p2 ='RevenueFromContractWithCustomerExcludingAssessedTax'
p3 = 'Revenues'
p4 = "TOTAL_REVENUES"
p4_1 = 'Total_Revenues'
p4_2 = 'Total_revenues'
p5 = 'SALES'
p5_1 = 'Sales'

#endregion  
przychody_zmienna = [p1,p2,p3,p4,p4_1,p4_2,p5,p5_1]
'____________________________________________________________________________________________'
''' 3.opis funckji
- wykonuje petle dla cik_wybrane
-podłącza się do api edgar przez companyfacts
- wykonuje petle dla przychody_zmienna w celu przeszukania fraz gdzie mogą być dane
- jesli dane są obecne dodaje je do tymczasowego przechowania w 'kontener'
- po wykonaniu całej przychody_zmienna dodaje dane do kontener_bazowy
- w przypadku błędu dodaje komunikat o błędzie
- wykonuje polecenie dla pozostałych cik_wybrane
- dodanie kolumny company z tickerem
'''
# tymczasowa baza danych dla jednej spolki w celu oczyszczenia danych
kontener_zbiorowy = [] 
def pobieranie_danych():
    i = 0
    for cik in cik_wybrane:
        try:
            companyFacts = requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json', headers=headers)
        
            kontener = []
            for p in przychody_zmienna:
                try:
                    # zdefiniowanie zmiennej z aktualnie obsługiwaną spółką
                    ticker = ticker_wybrany.iloc[i]

                    # polecenie które wywołuje konkretną frazę i sprawdza czy są dane
                    sales = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap'][p]['units']['USD'])
                    
                    # dodanie kolumny z nazwą firmy
                    sales['company'] = ticker
                    
                    # obsługa w przypadku gdy dane znajdują się pod frazą
                    print(f'SUKCES : dla {ticker} - {cik} udało się pobrać {p}')
                    
                    # dodanie obsługiwanej frazy do kontenera z danymi 
                    kontener.append(sales)

                # wprowadzenie obsługi kiedy nie będzie danych pod konkretną frazą
                except:
                    ticker = ticker_wybrany.iloc[i]
                    print(f'BRAK : dla {ticker} - {cik} nie udało się pobrać {p}')
            kontener_zbiorowy.append(kontener)
            i+=1
            print(f'dane dla {ticker} POBRANE')
            # break # wprowadzenie break spowoduje wykonanie się kodu na jednej spółce
            
        except:
            print(f'dane dla {ticker} nie zostały pobrane')
            
    return  
# Sprawdzenie, czy funkcja sec() zakończyła się sukcesem
if headers is not None and cik_stary is not None and cik_wybrane is not None and ticker_wybrany is not None:
    print("Funkcja `sec()` zakończyła się sukcesem. Uruchamiam funkcję `pobieranie_danych()`.")
    pobieranie_danych()
else:
    print("Funkcja `sec()` zakończyła się błędem. Funkcja `pobieranie_danych()` nie zostanie uruchomiona.")
'___________________________________________________________________________________________'

''' 4.opis funkcji:
- w kontener zbiorowy znajduje się lista list 
- 1. otwiera listy i tworzy z niej jedną listę 
- 2.połczenie wszystkich danych spółek w jedną bazę danych 'df'
- 3.przefiltrowanie danych aby wyświetlić jedynie 10-K i 10-Q
- 4. przefiltrowanie raportów półrocznych
'''
def pierwsze_czyszczenie_danych(kontener_zbiorowy):
    try:
        # 1.Spłaszczamy listę list: dla każdej podlisty (sublist) pobieramy jej elementy (df)
        pelna_lista = [df for sublist in kontener_zbiorowy for df in sublist]
        
        # 2.połączenie danych jednej spolki 
        df = pd.concat(pelna_lista, ignore_index=True)   
        
        # 3.wyświetlanie jedynie 10-K i 10-Q
        df = df[df['form'].isin(['10-K', '10-Q'])]
        
        #4
        '''4.czyszczenie raportów polrocznych, opis:__________________________________________
        kod: dokonuje stworzenia nowej kolumny z informacją o okresie sprawozdawczym
        kod czyści dane z sprawozdań półrocznych
        zamienia kolumny start i end na daty 
        '''
        # zamiana kolumn end i start na daty 
        df['start'] = pd.to_datetime(df['start'], errors='coerce')
        df['end'] = pd.to_datetime(df['end'], errors='coerce')

        df['okres sprawozdawczy'] = df['end'] - df['start']# kolumna sprawdza za jaki okres sprawozdawczy jest wynik 
        mask = (df['okres sprawozdawczy'].dt.days > 100) & (df['okres sprawozdawczy'].dt.days < 300)# oczyszczenie danych z raportów półrocznych
        df = df[~mask]#zasosowanie warunku

        print(f'\nPiersze czyszczenie danych zakończone sukcesem\n')
    except:
        print(f'ERROR: nie udało się wykonac pierwszego czyszczenia danych')

        return None    
    return df
kontener_zbiorowy = pierwsze_czyszczenie_danych(kontener_zbiorowy)
'___________________________________________________________________________________________'
''' 5.opis funkcji'''
baza_danych = []
def drugie_czyszczenie_danych():
    try: 
        for tic in ticker_wybrany:
            kontener_jednej_spolki = kontener_zbiorowy[kontener_zbiorowy['company'].isin([tic])]
            # print(kontener_jednej_spolki)

            # od tego momentu dane muszą być czyszczone dla jednej spolki
            'pomysl posortowac po okres sprawozdawczy aby roczne trafily na sama gore a nastepnie usunac duplikaty, i w kolejnym kroku posortowac po end '
            kontener_jednej_spolki = kontener_jednej_spolki.sort_values(by='okres sprawozdawczy', ascending=False) # sortuje po okres sprawozdawczy
            kontener_jednej_spolki = kontener_jednej_spolki.drop_duplicates(subset=['end']) # usuwa duplikaty z kolumny end
            kontener_jednej_spolki = kontener_jednej_spolki.sort_values(by='end', ascending=True) # sortuje po end
            kontener_jednej_spolki['dni roznicy'] = kontener_jednej_spolki['end'].shift(-1) -  kontener_jednej_spolki['end'] # tworzenie kolumny sprawdzającej dni różnicy między wynikiem 1 a wynikiem 2 
            mask = (kontener_jednej_spolki['dni roznicy'].dt.days > 100) & (kontener_jednej_spolki['dni roznicy'].dt.days < 300) # oczyszczenie danych z raportów półrocznych. Ponownie, trafiały się wyjątki
            kontener_jednej_spolki = kontener_jednej_spolki[~mask]#zastosowanie warunku
            kontener_jednej_spolki['dni roznicy'] = kontener_jednej_spolki['end'].shift(-1) -  kontener_jednej_spolki['end'] # tworzy kolumne dni roznicy odejmujac w kolumnie end w1 od w2
            # Jeśli pojawi się NaT (ostatni wiersz), wypełnij go poprzednią wartością
            kontener_jednej_spolki['dni roznicy'] = kontener_jednej_spolki['dni roznicy'].ffill()

            '''opis segmentu : obliczanie 4 kwartalu___________________________________
            1. z rocznego sprawozdania został obliczony wynik za 4 kwartał (roku obrotowego społki)
            2. dane zostaly posegregowane na roczne i kwartalne 
            '''
            kontener_jednej_spolki['okres dni'] = kontener_jednej_spolki['okres sprawozdawczy'].dt.days #konwertuje okres sprawozdawczy na liczby 
            df_roczne = kontener_jednej_spolki[kontener_jednej_spolki['okres dni'] > 300].copy() #znajdz wiersze wieksze od >300

            for index, row in df_roczne.iterrows():
                #ten segment kodu sprowadza wyniki roczne do wyniku kwartalnego 
                mask = \
                    (kontener_jednej_spolki['end'] <= row['end']) &\
                    (kontener_jednej_spolki['start'] >= row['start']) &\
                    (kontener_jednej_spolki['okres dni'] <= 300)
                kontener_jednej_spolki.at[index, 'val'] -= kontener_jednej_spolki.loc[mask, 'val'].sum()

            kontener_jednej_spolki.loc[kontener_jednej_spolki['okres dni'] > 300, 'start'] = \
                (kontener_jednej_spolki['end'] - pd.to_timedelta(kontener_jednej_spolki['dni roznicy'].dt.days - 1, unit='D')).dt.strftime('%Y-%m-%d')
                # aktualizacja daty w kolumnie start w sprawozdaniu rocznym 
            '__________________________________________________________________________'

            kontener_jednej_spolki = kontener_jednej_spolki.drop_duplicates(subset=['start']) # usuwa duplikaty z kolumny strat. pojawiały się nieprzeczyszczone
            'w celach testowych zostawiam linijke kodu'
            # kontener_jednej_spolki['ostatni test'] = kontener_jednej_spolki['end'].shift(-1) -  kontener_jednej_spolki['end'] # ponownie w celu weryfikacji ciągłości 

            # usuwanie kolumn
            'accn' 'filed'
            kolumny_do_usunięcia = ['accn','filed','form','fy','fp','dni roznicy','okres dni','frame','okres sprawozdawczy']
            kontener_jednej_spolki = kontener_jednej_spolki.drop(columns=kolumny_do_usunięcia, errors='ignore')
            baza_danych.append(kontener_jednej_spolki)
        print(f'\nDruga faza czyszczenia danych zakończona sukcesem\n')
    except:
        print(f'ERROR: nie udało się wykonać drugiego czyszczenia danych')
        return None
drugie_czyszczenie_danych()
'-___________________________________________________________________________________________'
baza_danych = pd.concat(baza_danych, ignore_index=True)
# print(baza_danych)

bd_modyfikacja_danych = []
def modyfikacja_danych():
    try:
        for t in ticker_wybrany:
            # przefiltrowanie
            bd_md = baza_danych[baza_danych['company'].isin([t])]
            # transpozycja
            bd_md = bd_md.T
            # zmiana nazwy kolumny val
            bd_md = bd_md.rename(index={'val':'przychody'})
            # dodanie kolumny z tickerem
            bd_md['ticker'] = t
            # usunięcie wiersza company
            bd_md = bd_md.drop('company', axis=0)
            # przeniesienie kolumny ticker na początek
            cols = ['ticker'] + [col for  col in bd_md.columns if col != 'ticker']
            # zastąpienie kolumny ticker
            bd_md = bd_md[cols]

            # Zresetuj indeks, aby 'start', 'end', 'val' były kolumnami
            bd_md = bd_md.reset_index().rename(columns={'index': 'typ'})

            # Usuń godzinę z dat w wierszach 'start' i 'end'
            for row in ['start', 'end']:
                mask = bd_md['typ'] == row
                bd_md.loc[mask, bd_md.columns[2:]] = (
                    bd_md.loc[mask, bd_md.columns[2:]]
                    .map(lambda x: str(x).split(' ')[0] if pd.notnull(x) else x)
                )

            stałe = ['typ', 'ticker']
            wszystkie_kolumny = list(bd_md.columns)
            numery = [col for col in wszystkie_kolumny if col not in stałe]
            if numery:
                # Odwróć kolejność kolumn z numerami
                nowe_kolumny = stałe + numery[::-1]
                bd_md = bd_md[nowe_kolumny]
                # Zmień nazwy kolumn liczbowych na 1, 2, ..., N (od lewej najnowsze)
                nowe_numery = [str(i) for i in range(1, len(numery)+1)]
                bd_md.columns = stałe + nowe_numery
            
            bd_modyfikacja_danych.append(bd_md)
        print(f'\nModyfikacja danych zakończona sukcesem\n')
    except:
        print(f'ERROR: nie udało się wykonać modyfikacji danych')
        return None
    return 
modyfikacja_danych()
bd_modyfikacja_danych = pd.concat(bd_modyfikacja_danych, ignore_index=True) 

''''zadania na przyszłość

'zmienić te cyferki, które wyświetlają się w pierwszym wierszu '
'raport mozna namiezyc po end. accn i filed zle dopasowany, wartosci w kolumnach val sa prawidlowe, aczkolwiek podczas maglowania danymi te numery zostaly dopasowane do innych sprawozdań i z nich zostały wyprowadzone prawidlowo wartosci val'


'''



print(bd_modyfikacja_danych)
'-___________________________________________________________________________________________'

# Nazwa i ścieżka pliku CSV
sciezka = os.path.join(os.getcwd(), "DATA SEC.csv")
bd_modyfikacja_danych.to_csv(sciezka, index=False, encoding='utf-8')

print(f"Dane zostały zapisane do: {sciezka}")
'-___________________________________________________________________________________________'


