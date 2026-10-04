# apprologic.de – Webseite

Next.js-Projekt für die neue ApproLogic-Webseite. Alle Texte liegen als Markdown-Dateien in `content/pages`, die Seitenstruktur in `content/site.ts`. Der Build erzeugt statische HTML-Dateien, die auf jedem Webserver laufen.

## Texte ändern

| Was | Wo |
| --- | --- |
| Text einer Seite | `content/pages/<pfad>.md` – Dateipfad = URL, z. B. `content/pages/funktionen/wartung.md` → `/funktionen/wartung/` |
| Startseite | `content/pages/index.md` |
| Titel, Einleitung, Brotkrumen, Vor/Zurück | Frontmatter oben in der jeweiligen `.md`-Datei |
| Hauptnavigation, Untermenüs, Fußzeile | `content/site.ts` |
| Adresse, Telefon, E-Mail, CTA-Beschriftung | `content/site.ts` (`site`) |

### Frontmatter einer Seite

```yaml
---
title: "Überschrift der Seite (H1)"
seoTitle: "Kurzer Titel für Google und Browser-Tab"   # optional, höchstens ca. 45 Zeichen; " | ApproLogic" kommt dazu. Ohne seoTitle wird title genommen
eyebrow: "Kleine Zeile über der Überschrift"       # optional
lead: "Einleitungstext unter der Überschrift"       # optional, dient auch als Meta-Beschreibung
description: "Eigene Meta-Beschreibung"             # empfohlen, höchstens ca. 160 Zeichen
section: "funktionen"                                # markiert den aktiven Hauptmenüpunkt
heroImage: { src: "/bilder/ki-assistent.svg", alt: "Bildbeschreibung" }   # optional: Bild rechts neben der Überschrift
breadcrumbs: [{ label: "Funktionen", href: "/funktionen/" }, { label: "Wartung", href: "" }]
prev: { label: "Serviceanfragen", href: "/funktionen/serviceanfragen/" }   # optional
next: { label: "Ersatzteile", href: "/funktionen/ersatzteile/" }           # optional
---
```

### Eigene Blöcke im Markdown

Neben normalem Markdown (Überschriften `##`, Listen, Tabellen, Links) gibt es fünf Blöcke als Code-Fences:

````markdown
```tiles
Titel der ersten Kachel
Text der Kachel, beliebig lang.
-> /funktionen/ Linktext           (optional: macht die Kachel klickbar)

Titel der zweiten Kachel
Text.
```

```numbers
−20 % | Erläuterung zur Zahl
−30 % | Erläuterung zur Zahl
```

```cta
Überschrift des Abschlussblocks
Optionaler Text.
-> /kontakt/ Demo anfragen          (erster Link = primärer Button)
-> /funktionen/ Funktionen ansehen
```

```image
/bilder/datei.svg                  (optional: Pfad zu einer Datei in public/, dahinter optional "logos" für eine Logoleiste)
Beschreibung des Bildes             (Alt-Text; ohne Pfad erscheint ein Platzhalter)
```

```video
/video/datei.mp4 /video/datei.jpg   (MP4 in public/, dahinter optional ein Vorschaubild)
Beschreibung des Videos             (für Screenreader; die Datei lädt erst beim Klick auf Abspielen)
```

```form
```
````

## Entwickeln und bauen

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # statischer Export nach ./out
```

Der Inhalt von `out/` wird auf den Webserver kopiert. Interne Links enden mit `/` (`trailingSlash`), damit die Ordnerstruktur ohne Rewrites funktioniert.

## Suchmaschinen (SEO)

Bereits eingebaut, ohne weiteres Zutun bei jedem Build:

- Titel und Beschreibung je Seite aus dem Frontmatter (`seoTitle`, `description`), Canonical-Link auf `https://www.apprologic.de` (`site.url` in `content/site.ts`)
- `sitemap.xml` und `robots.txt` (aus allen Seiten in `content/pages`)
- Vorschau beim Teilen (Open Graph, Twitter Card) mit `public/vorschau.png` (1200 × 630). Vorlage: `assets/vorschau.svg`; nach Änderungen neu als PNG exportieren
- Strukturierte Daten (JSON-LD) in `components/StructuredData.tsx`: Unternehmen und Brotkrümel auf jeder Seite, das Produkt auf Start- und Produktseite
- Deutsche Fehlerseite `404.html` (Texte in `content/site.ts`, `notFoundPage`), von Suchmaschinen ausgeschlossen

## Nach dem Livegang

1. **Weiterleitungen einrichten:** `http://` und `apprologic.de` ohne www per 301 auf `https://www.apprologic.de`, siehe [server/nginx-weiterleitungen.conf](server/nginx-weiterleitungen.conf). Prüfen: `curl -sI http://apprologic.de/produkt/ | grep -i location` muss `https://www.apprologic.de/produkt/` zeigen.
2. **Fehlerseite ausliefern:** In nginx im Server-Block `error_page 404 /404.html;` setzen, damit unbekannte Adressen die deutsche Fehlerseite mit Status 404 zeigen.
3. **Google Search Console:** Unter https://search.google.com/search-console die Property `https://www.apprologic.de` (oder die Domain `apprologic.de`) anlegen und per DNS-Eintrag bestätigen. Unter *Sitemaps* `https://www.apprologic.de/sitemap.xml` einreichen. Start- und Produktseite unter *URL-Prüfung* einmal zur Indexierung anfordern.
4. **Bing Webmaster Tools:** https://www.bing.com/webmasters, Website aus der Search Console importieren (deckt auch DuckDuckGo und Ecosia ab).
5. **Prüfen:** Strukturierte Daten mit https://search.google.com/test/rich-results, Vorschaubild mit dem LinkedIn Post Inspector (https://www.linkedin.com/post-inspector/).
6. **Alte Adressen umleiten:** Hatte die bisherige Webseite andere Seitenadressen, die von außen verlinkt sind (aus Google oder von Partnerseiten), diese per 301 auf die passende neue Seite umleiten. Die Search Console zeigt nach einigen Tagen unter *Seiten* die nicht gefundenen Adressen.
