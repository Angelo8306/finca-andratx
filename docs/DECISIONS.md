# DECISIONS — Finca Andratx

## Hosting: GitHub Pages
**Entscheidung:** Landingpage auf GitHub Pages hosten
**Grund:** Kostenlos, schnell, einfach zu aktualisieren, HTTPS inklusive
**URL:** https://angelo8306.github.io/finca-andratx/

## Design: Dunkles Farbschema
**Entscheidung:** Dunkler Hintergrund (#1a1a2e, #16213e) mit Gold-Akzenten (#d4a853)
**Grund:** Luxurioese Ausstrahlung passend zum Preisniveau (2,95 Mio EUR), hebt Fotos besser hervor

## Hero-Overlay
**Entscheidung:** Dunkler Gradient-Overlay (rgba 0,0,0,0.55) + Text-Shadow
**Grund:** Text war auf hellem Himmel schlecht lesbar — nachgebessert fuer besseren Kontrast

## Schriftarten
**Entscheidung:** Playfair Display (Headlines) + Lato (Fliesstext)
**Grund:** Playfair = elegant/klassisch passend zu historischer Finca, Lato = gut lesbar auf allen Geraeten

## Sprache: Deutsch + Englisch
**Entscheidung:** Landingpage auf Deutsch, Reels in DE + EN
**Grund:** Zielgruppe sind deutschsprachige und internationale Kaeufer auf Mallorca

## Video-Reels: Ken-Burns-Effekt
**Entscheidung:** Fotos mit langsamen Zoom/Pan animieren statt echtes Video
**Grund:** Kein Videomaterial vorhanden, Ken-Burns gibt statischen Fotos Dynamik

## Voiceover: KI-Stimmen
**Entscheidung:** KI-generierte Voiceovers fuer Reels
**Grund:** Schnell produzierbar, professionelle Qualitaet, mehrsprachig moeglich

## Flaechenangaben: Korrektur 30.03.2026
**Entscheidung:** Alle Flaechenangaben nach Cay-Feedback korrigiert
**Grund:** Obergeschoss war falsch (115,78 statt 77,97 m2), dadurch Gesamtflaeche falsch (231 statt 193,75 m2). Sommersalon (23,78 m2) fehlte. Vordach war leicht ungenau (36 statt 36,35 m2).
**Korrekte Werte:** EG 115,78 + OG 77,97 = 193,75 m2 bebaute Flaeche. Sommersalon 23,78 m2. Terrasse 134 m2 (inkl. 36,35 m2 Vordach). Grundstueck 2.345 m2.

## PDF-Expose: Python + ReportLab
**Entscheidung:** Expose programmatisch mit Python erstellen
**Grund:** Volle Kontrolle ueber Layout, reproduzierbar, keine externe Software noetig

## Grosse Dateien: Nicht ueber GitHub
**Entscheidung:** Video-Reels und PDF nicht ueber GitHub Pages ausliefern
**Grund:** Dateien sind 20-34 MB gross — zu schwer fuer Git-Repository, separat teilen (WeTransfer, Google Drive etc.)
