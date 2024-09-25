import os
import numpy as np


# Vytvoření prázdného seznamu pro ukládání průměrů
prumery = []

# Procházíme všechny soubory ve složce
for soubor in os.listdir("./zaznamy_mereni"):
    if soubor.endswith(".txt"):
        cesta_k_souboru = os.path.join("./zaznamy_mereni", soubor)
        
        # Otevření souboru a načtení hodnot ze třetího sloupce
        with open(cesta_k_souboru, 'r') as f:
            hodnoty = [float(line.split()[2]) for line in f]

        # Vypočítání průměru a přidání do seznamu průměrů
        prumer = round(np.mean(hodnoty), 2)
        prumery.append(prumer)

        # Výpis na výstup
        print(f"{soubor} Průměr: {prumer}")

# Vypočítání celkového průměru
celkovy_prumer = round(np.mean(prumery), 2)
print(f"Celkový průměr všech souborů: {celkovy_prumer}")

# Výpočet směrodatné odchylky jednotlivých průměrů od celkového průměru
odchylky = [round(prumer - celkovy_prumer, 2) for prumer in prumery]
print(f"Směrodatná odchylka od celkového průměru: {odchylky}")
# Výpočet a výpis celkové směrodatné odchylky
celkova_odchylka = round(np.std(prumery), 2)
print(f"Celková směrodatná odchylka: {celkova_odchylka}")
procentualni_odchylky = [round(100-abs((odchylka / celkovy_prumer) * 100), 2) for odchylka in odchylky]
print(f"Procentuální přesnost senzoru: {procentualni_odchylky}")