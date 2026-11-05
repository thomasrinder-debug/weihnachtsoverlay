# Ideen für Szenen

Typische weltliche Weihnachtsfiguren, alle frei gestaltet: Schneemann, Wichtel, Lebkuchenmann, Nussknacker (Holzsoldat), Pinguin, Eisbär, Rentier, geschmückter Tannenbaum, Geschenke, Weihnachtsstrumpf, Lichterkette, Zuckerstange, Plätzchen.

Bewusst weggelassen: alles Religiöse (Krippe, Engel, Christkind, Heilige, Stern von Bethlehem; der Baum trägt deshalb eine Spitze statt eines Sterns) und geschützte Figuren oder Marken (kein bekanntes Rentier mit roter Leuchtnase, kein grüner Weihnachtsmuffel, kein Schneemann mit Zylinder und Maiskolbenpfeife, keine Film- oder Werbefiguren).

## Umgesetzt

| Name | Rand | Gag |
|---|---|---|
| nase | unten | Schneemann niest sich die Möhre aus dem Gesicht und steckt sie verkehrt wieder an |
| bau | unten | drei Schneekugeln rollen herein und stapeln sich zum Schneemann |
| lebkuchen | unten | Lebkuchenmann flieht nach dem ersten Biss |
| jagd | unten | Wichtel jagt Weihnachtsmann, dann umgekehrt, dann rauscht ein Pinguin heran |
| pinguin | unten | Bauchrutscher, Ausrutscher, Sterne sehen |
| geschenk | unten | Paket hüpft, Wichtel schnellt auf einer Feder heraus |
| nussknacker | unten | Walnuss springt in den Mund, Knack, Kiefer klappt herunter |
| tannenbaum | unten | Baum schleicht auf Stiefelchen, verliert Kugeln, die ihm nachkullern |
| schneeball | unten + Seite | Treffer an die Mütze, empörter Blick ins Publikum |
| eisbaer | unten | Schlafblase platzt, beide fliehen |
| lichter | unten | Lichterkette einstecken, Stromschlag, rußiges Gesicht |
| glatteis | unten | Rudern, Rückenlage, kopfüber davonschlittern |
| muetze | unten | Wind reißt die Mütze weg, Glatze |
| hangeln | oben | Wichtel hangelt an einer Lichterkette unter dem Rand |
| strumpf | oben | Strumpf schwebt herab, Wichtel schaut heraus |
| baerspaeht | Seite | Eisbär fängt Schneeflocken mit der Zunge und niest |
| gespann | unten | Rentier rennt mit leerem Schlitten weg und holt ihn dann ab |

## Zweite Runde

Die Vorschläge stammen aus einem Dialog mit ChatGPT; weggelassen wurden die, die es oben schon ähnlich gibt (Eisbär, Lichterkette, Strumpf, Nussknacker, Schneeball, Schneemann baut sich selbst). Running Gag: ein Wichtel mit steifer Mütze, deren Spitze rechtwinklig abknickt. Nach einer Panne richtet er sie würdevoll gerade, und sie knickt sofort wieder ab (`muetze_richten()` in `basis.py`, Figur `WichtelSteif`).

| Name | Rand | Gag |
|---|---|---|
| eiszapfen | oben, Ecke | Wichtel poliert einen Eiszapfen, der bricht, unten poliert er das Bruchstück weiter (Mützen-Gag) |
| rodeln | Seite | senkrecht die Kante hinunterrodeln, mit dem Schlitten die Wand wieder hinaufmarschieren (Mützen-Gag) |
| skisprung | unten | flacher Sprung, kopfüber in der Wehe, die Ski stellen sich brav parallel |
| zimtstern | unten | Eichhörnchen zerrt am Riesen-Zimtstern, beißt eine Zacke ab, rollt ihn kippelnd davon |
| nieslawine | Ecke | Flocke auf der Nase, Niesen, Lawine, nur die Mütze schaut heraus |
| schal | unten | Wichtel wickelt sich zur Wolltonne, die Mütze versinkt obenauf |
| besen | unten | der Besen fegt den Wichtel aufs Kehrblech (Mützen-Gag) |
| geschenkband | unten | Wichtel verschnürt sich selbst und rückt die Schleife gerade |
| keks | unten | harter Keks sägt ein Tännchen ab, die Spitze landet als Mütze |
| schaufel | unten | geschippter Schnee kommt als Würfel zurück, immer wieder |
| turm | unten | Geschenketurm auf dem Kopf, Balancieren, Kippen |
| plaetzchen | unten + Seite | Hand stibitzt Plätzchen, Wichtel haut mit dem Kochlöffel drauf |
| trapez | oben | Trapez aus Zuckerstangen, kopfüber winken, Abflug über den Rand |

## Dritte Runde: Pinguine, Katzen, Winterfiguren

Wunsch nach Figuren aus einem bekannten Eiskönigin-Film und nach einem bekannten grünen Weihnachtsmuffel: beides geschützt, deshalb eigene Figuren (Frostfee, Wichtelschwestern, Grummelkater).

| Name | Rand | Gag |
|---|---|---|
| pinguinfamilie | unten | Mama und drei Küken rutschen im Gänsemarsch, das Kleinste purzelt |
| angeln | unten | Pinguin angelt eine Socke, dann springt ihm ein Fisch auf den Kopf |
| katzekugel | oben | Katze läuft kopfüber an der Kante und spielt mit einer Christbaumkugel |
| katzekarton | unten | Katze im Geschenk, Deckel drauf, Katze landet auf seiner Mütze |
| grummelkater | unten | mürrischer Kater schubst Kugeln vom Bäumchen und schiebt es weg |
| frostfee | unten | Frostfee tippt ihn an, er steckt im Eisblock |
| schlittschuh | unten | elegante und wackelige Wichtelschwester, Zusammenstoß |
| eispalast | unten | Eisblock-Schloss, ein Block zu viel (Mützen-Gag) |


## Vierte Runde: Spiel mit dem echten Bildschirm

Diese Szenen tun nur so, als veränderten sie andere Programme. `abgreifen.py` holt ein Bildschirmfoto und die Lage der Symbole bzw. der Schreibmarke, `bildanalyse.py` schneidet Symbol oder Zeile aus und baut einen Flicken zum Abdecken. Die Szene deckt das Original ab und spielt mit der Kopie. Findet sich nichts Passendes, fällt die Szene aus.

| Name | Ort | Gag |
|---|---|---|
| taskleiste | Taskleiste | ein Programmsymbol zappelt, wächst ruckweise, glüht, platzt in Scherben, Funken und Rauch und taucht mit Nachzittern wieder auf |
| tippkatze | getippte Zeile | nach einer Tipppause öffnet sich ein Spalt zwischen zwei Wörtern, eine Katze schaut heraus, trampelt auf der Zeile, Buchstaben hüpfen und tauschen die Plätze; nur über den eigenen Auslöser in der Automatik, liegt ausnahmsweise mitten im Bild |

Verworfen: tanzende Desktopsymbole (Thomas, November 2026).
