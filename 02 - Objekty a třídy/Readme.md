# Objekty a t��dy

Dom�c� �loha **25. z��� - 2. ��jna**.

* [Materi�ly](https://is.muni.cz/auth/el/1433/podzim2018/PV248/um/python.pdf#page=51)
* [Diskusn� f�rum](https://is.muni.cz/auth/cd/1433/podzim2018/PV248/02)

>* pokud obsahuje 'Voice N:' pod�et�zec '--', znaky okolo jsou ch�p�ny jako rozsah (range), jinak je range None; rozpoznan� range a p��padn� ��rka a mezera za n�m je z textu odstran�na a zbytek (je-li nepr�zdn�) je pou�it jako 'name'
* pokud Voice neobsahuje rozsah ale je nepr�zdn�, je cel� ch�p�n jako 'name'
* roky narozen� a �mrt� sta�� uva�ovat op�t jsou-li ve form�tu 4 ��slice; je ale pot�eba rozezn�vat v�echny p��pady form�tov�n� (jeden nebo oba roky, jednoduch� i dvojit� pomlky a zna�ky * pro narozen� resp. + pro �mrt�)
* pro v�pis narozen�/�mrt� pou�ijte form�t s '--' (tzn. t�eba 1750--, --1800 nebo 1750--1800)
* pokud je n�jak� hodnota None, nemus� se ve v�pisu pomoci format() odpov�daj�c� ��dek v�bec objevit, nebo m��e b�t pr�zdn�
* sekvence load() � format() � load() � format() by m�la d�t stejn� v�sledek jako samotn� load() � format() [tzn. load() + format() by m�lo b�t idempotentn�]
