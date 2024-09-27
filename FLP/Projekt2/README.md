# FLP projekt - Turinguv stroj
# Autor: Jiri Vaclavic, xvacla31

## Preklad a spusteni
make
./flp23-log < tests/input1.txt

## Porovnani spravnosti vystupu
./flp23-log < tests/input1.txt > Output1_generated.txt
diff Output1_generated tests/Output.txt

## Struktura kódu

Kód je rozdělen do několika hlavních predikátů:

- `read_line/2`, `read_lines/1`: Čtení vstupních dat.
- `remove_every_second/2`, `splitLine/5`: Zpracování vstupních řádků a extrakce informací o pravidlech.
- `createRules/2`: Vytváření pravidel z extrahovaných dat a jejich ukládání.
- `applyRules/5`: Aplikace pravidel na vstupní pásku a simulace výpočtu.
- `check_for_F_rule`: Kontrola, zda existuje přechod do finálního stavu 'F'.

-  Program hleda reseni, ktera ma nejmene konfigurace
-  V kazde iteraci se uklada nova konfigurace do promenne Configs a vypise se pouze tehdy, kdyz se dojde do konecneho stavu 'F'
-  Abnormalni zastaveni je provedeno pomoci predikatu halt(1)