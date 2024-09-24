/** 
SEM, Projekt1
Autor: Jiri Vaclavic, xvacla31
**/

Vyznam sloupcu v souborech {nazev}.txt:
1. sloupec - datum vytvoreni zaznamu
2. sloupec - cas vytvoreni zaznamu
3. sloupec - namerena teplota
*4. sloupec - namerena vlhkost DHT11 senzoru (pouze u souboru sensor1_{5min/1hour/4hours}.txt)

Spusteni:
-prelozeni, nahrani kodu read_sensors_data.ino na Arduino Uno
-python serial_read.py
-python calculate_results

Soubory ve slozce:
Programy:

-read_sensors_data/read_sensors_data.ino - kod spustitelny na Arduino Uno, vystup programu jsou data o teplote na seriove lince
-serial_read.py - python kod pro cteni dat ze seriove linky, vystup jsou txt soubory zaznamu mereni v case, soubor je ve vychozim nastaveni pro zaznamenani mereni o delce 5 minut, pro ostatni druhy mereni je nutne odkomentovat dane casti kodu
-calculate_results.py - python kod pro
 
Ostatni soubory:
-zaznamy_mereni/sensor{cislo_senzoru}_{doba_mereni}.txt, kde cislo mereni je 1-4 a doba mereni je 5 min, 1 hour, 4 hours
-dokumentace.pdf

