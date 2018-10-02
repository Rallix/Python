# Objekty a tøídy

Domácí úloha **25. záøí - 2. øíjna**.

* [Materiály](https://is.muni.cz/auth/el/1433/podzim2018/PV248/um/python.pdf#page=51)
* [Diskusní fórum](https://is.muni.cz/auth/cd/1433/podzim2018/PV248/02)

>* pokud obsahuje 'Voice N:' podøetìzec '--', znaky okolo jsou chápány jako rozsah (range), jinak je range None; rozpoznaný range a pøípadná èárka a mezera za ním je z textu odstranìna a zbytek (je-li neprázdný) je použit jako 'name'
* pokud Voice neobsahuje rozsah ale je neprázdný, je celý chápán jako 'name'
* roky narození a úmrtí staèí uvažovat opìt jsou-li ve formátu 4 èíslice; je ale potøeba rozeznávat všechny pøípady formátování (jeden nebo oba roky, jednoduché i dvojité pomlky a znaèky * pro narození resp. + pro úmrtí)
* pro výpis narození/úmrtí použijte formát s '--' (tzn. tøeba 1750--, --1800 nebo 1750--1800)
* pokud je nìjaká hodnota None, nemusí se ve výpisu pomoci format() odpovídající øádek vùbec objevit, nebo mùže být prázdný
* sekvence load() › format() › load() › format() by mìla dát stejný výsledek jako samotné load() › format() [tzn. load() + format() by mìlo být idempotentní]
