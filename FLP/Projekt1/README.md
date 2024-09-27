# Soubor:	README.md
# Datum:	31.3.2024
# Autor:	Bc. Jiri Vaclavic, xvacla31@stud.fit.vutbr.cz
# Projekt:	FLP, Haskell - Rozhodovaci strom
# Popis:	Implementace rozhodovaciho stromu



Spusteni aplikace:
	./flp-fun -1 <file_path1> <file_path2>

    -Vytvori se rozhodovaci strom specifikovany v textovem souboru <file_pat1>
    -Probehne klasifikace novych dat, ktere jsou specifikovane v textovem souboru <file_path2>
    
    ---------------------
    ./flp-fun -2 <file_path>

    -Pomoci algoritmu CART se vytvori rozhodovaci strom na zaklade dat specifikovanych v textovem souboru <file_path>
    -Pri implementaci jsou vyuzity midpointy

Pozorovane vlastnosti programu:
-Program byl uspesne otestovan pomoci poskytnutych vzorovych testu
-Nedostatek vidim v rychlosti behu programu

Vypis souboru training_test_result.csv:
    penguins_all.csv,0, 1.000, 1.000, 1.000, 1.000, 0.000, 0.992
    penguins_all.csv,0.25, 1.000, 0.988, 1.000, 0.976,-0.012, 0.600
    penguins_all.csv,0.5, 1.000, 0.910, 1.000, 0.958, 0.048, 0.238
    iris_all.csv,0, 1.000, 1.000, 1.000, 1.000, 0.000, 0.156
    iris_all.csv,0.25, 1.000, 1.000, 1.000, 1.000, 0.000, 0.140
    iris_all.csv,0.5, 1.000, 1.000, 1.000, 1.000, 0.000, 0.066
    housing_all.csv,0, 1.000, 1.000, 1.000, 1.000, 0.000, 6.042
    housing_all.csv,0.25, 1.000, 0.636, 1.000, 0.646, 0.010, 2.457
    housing_all.csv,0.5, 1.000, 0.670, 1.000, 0.640,-0.030, 0.894
    wines_all.csv,0, 1.000, 1.000, 1.000, 1.000, 0.000, 107.186
    wines_all.csv,0.25, 1.000, 0.559, 1.000, 0.577, 0.017, 43.786
    wines_all.csv,0.5, 1.000, 0.531, 1.000, 0.531, 0.000, 15.431