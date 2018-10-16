# Práce s SQL

Domácí úloha **16. října - 23. října**.

* [Materiály](https://is.muni.cz/auth/el/1433/podzim2018/PV248/um/python.pdf#page=121)
* [Diskusní fórum](https://is.muni.cz/auth/cd/1433/podzim2018/PV248/tyden_4_prace_s_sql)


> Podrobnosti:

> - JSON popis struktury print má obsahovat všechna data dostupná v databázi
(včetně autorů a hlasů)
> - autoři nechť jsou reprezentováni JSON seznamem (stejně tak editoři)
> - jak reprezentujete hlasy nechám na Vás: může být jako klíče "Voice N" přímo ve
slovníku reprezentující score, nebo jako podslovník (tzn. "Voices": { "1": {
"range": "...", "name": "..." }, "3": { ... }  }) nebo jako seznam (tzn.
"Voices": [ { ... }, {}, {...} ])... to co musíte dodržet je korespondence mezi
identifikací hlasu ve výstupu a na vstupu (sloupec 'number' v tabulce 'voice')
> - chybějící hodnoty můžete indikovat pomocí null (speciální JSON hodnota) nebo
pomocí absence příslušného klíče (ale nikoliv "None" nebo None bez uvozovek)
> - rozumné formátování zabezpečíte pomocí parametru indent=4 (nebo 2 nebo
podobně) fci json.dumps; správnost utf-8 výstupu pak parametrem
ensure_ascii=False
> - JSON klíče budou chápány jako case-insensitive (tzn. nezáleží zda vypíšete
"print number", "Print number" nebo "Print Number")