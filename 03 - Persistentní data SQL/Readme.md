# Persistentní data SQL

Domácí úloha **9. října - 16. října**.

* [Materiály](https://is.muni.cz/auth/el/1433/podzim2018/PV248/um/python.pdf#page=85)
* [Diskusní fórum](https://is.muni.cz/auth/cd/1433/podzim2018/PV248/tyden_3_persistentni_data_sql)


> Dotazy a nejasnosti ze cvičení:
>
>- sqlite na 'integer primary key' sloupcích provádí autoincrement automaticky
(konkrétní hodnotu dostanete pomocí cursor.lastrowid)
>- tabulka 'score' odpovídá objektu 'Composition' (historické nedopatření, ale
zůstává takto)
>- hodnota 'P' zmíněná v komentáři sloupce 'partiture' se nikdy nepoužije (totéž)
>- sloupec 'year' v tabulce 'edition' můžete nechat vždy null (jinak odpovídá
vstupnímu políčku 'Publication Year')
>- aby nedošlo k nedorozumění, požadavek na unikátnost řádků je smysluplný:
odlišný primární klíč (id) z pohledu tohoto kritéria jinak identické řádky
nerozlišuje [EDIT 2018-10-11: provize o primárním klíči se nevztahuje na tabulku
'print', kde je tento nositelem významné informace pocházející ze vstupních dat]
>
>**EDIT 2018-10-12**:  
Duplikace řádků nezáleží pouze na samotných sloupcích uvnitř
dané tabulky. Třeba tabulky score_author a edition_author reprezentují de-facto
seznam autorů, který rozšiřuje daný řádek tabulky score, resp. edition. Foreign
key v tabulce 'voice' který odkazuje na score podobně kóduje seznam hlasů dané
skladby. Pokud tedy máte skladbu, která se liší pouze autorem (případně pouze
seznamem hlasů), budou v tabulce 'score' dva na pohled identické řádky, které se
liší pouze v 'id'. Provedete-li join na score.id = score_author.score, tyto
řádky rozlišíte. Není ale pravda, že dokážete-li napsat join, který nějaké řádky
rozliší, tak to nejsou duplikáty. Platí to pouze v případě, že příslušný join
modeluje skutečný vztah příslušných entit, popsaný v scorelib.sql.