# RadioList (Web/HTML) – Empfehlungen, HTML‑Muster, Auswahlstrategie

Diese Seite bezieht sich auf Web/HTML. Radio‑Buttons werden im Web über das `name`‑Attribut zu Gruppen zusammengefasst. Eine einheitliche, semantische „Klammer“ ist nicht vorgeschrieben (fieldset ist empfohlen, aber nicht verpflichtend). Diese Seite beschreibt, wie eine RadioList aufgebaut sein sollte, und wie OKW4Robot (treiberunabhängig) die Auswahl vornimmt.

---

## TL;DR / Empfehlungen

- Gruppierung immer über `name="…"` (Pflicht für Exklusivität).
- Semantische Klammer: `fieldset + legend` (empfohlen), alternativ ein Container (z. B. `div`) mit einem stabilen Locator (`data-testid`).
- Jede Option hat ein sichtbares Label (umfassendes `<label>` oder `label for="…"`).
- Im OKW‑YAML: Entweder
  - name‑basiert über `group: <name>` (einfach), oder
  - container‑basiert über `locator: { css: '[data-testid="…"]' }` (robuster für Sync/Scroll).

Benennung in OKW:
- Bevorzugte Klasse für Web: `okw_web_selenium.widgets.webse_radiolist.WebSe_RadioList`
- `RadioList` existiert als Alias/Abwärtskompatibilität.

---

## HTML‑Muster 1: Name‑basierte Gruppe (ohne explizites fieldset)

```html
<form>
  <!-- Klammer optional; entscheidend ist das gemeinsame name -->
  <div>
    <label><input type="radio" name="zahlungsmethode" value="paypal"> PayPal</label>
    <label><input type="radio" name="zahlungsmethode" value="visa"> Visa</label>
    <label><input type="radio" name="zahlungsmethode" value="sepa"> SEPA</label>
  </div>
</form>
```

YAML (OKW):
```yaml
Zahlungsmethode:
  class: okw_web_selenium.widgets.webse_radiolist.WebSe_RadioList
  group: zahlungsmethode   # name‑Attribut der Radios
```

Auswahl in OKW (WebRadioList):
- Select: per `name + value`
- VerifyValue: per Adapter‑Assertion mit `name + expected`

---

## HTML‑Muster 2: Container‑basierte Gruppe (fieldset mit legend)

```html
<form>
  <fieldset data-testid="rl-lieferung">
    <legend>Lieferung</legend>
    <label><input type="radio" name="lieferung" value="DHL"> DHL</label>
    <label><input type="radio" name="lieferung" value="UPS"> UPS</label>
    <label><input type="radio" name="lieferung" value="DPD"> DPD</label>
    <label><input type="radio" name="lieferung" value="Hermes"> Hermes</label>
    <label><input type="radio" name="lieferung" value="Selbstabholung"> Selbstabholung</label>
  </fieldset>
</form>
```

YAML (OKW):
```yaml
Lieferung:
  class: okw_web_selenium.widgets.webse_radiolist.WebSe_RadioList
  locator: { css: '[data-testid="rl-lieferung"]' }
```

Auswahl in OKW (WebRadioList):
- Select: innerhalb des Containers per CSS `input[type='radio'][value='<Wert>']`
- VerifyValue: liest den `:checked`‑Radio innerhalb des Containers und vergleicht dessen `value`

---

## Auswahl‑ und Sync‑Strategie in OKW4Robot (Kurzfassung)

Wenn eine RadioList angesprochen wird, erfolgt die Wahl in dieser Reihenfolge:

1) Locator mit explizitem `name`‑Selektor (z. B. `css:[name="gruppe"]`)
- Auswahl/Prüfung per `name + value` (Adapter‑Funktionen)

2) Container‑Locator (z. B. `fieldset` mit `data-testid`)
- Auswahl per `input[type='radio'][value='<Wert>']` innerhalb des Containers
- Verifikation per `:checked` im Container

3) Fallback: YAML‑Feld `group: <name>`
- Auswahl/Prüfung per `name + value`

Hinweis Scroll/Sync:
- Die Synchronisations‑Schicht (Delay‑Strategie) scrollt, falls vorhanden, den **Container‑Locator** in den Viewport (scrollIntoView). Gibt es keinen Locator (reine name‑Variante), werden elementbezogene Sync‑Checks übersprungen; die Auswahl funktioniert weiterhin über `name`. Details: `docs/synchronization_strategy.md`.

Details zur Sync‑Strategie: `docs/synchronization_strategy.md`.

---

## Häufige Stolpersteine (Web)

- Keine gemeinsame `name`‑Angabe: Dann sind es keine exklusiven Radios; die Gruppe funktioniert nicht wie erwartet.
- Fehlende Labels: Die Optionen sind zwar technisch funktional, aber ohne sichtbaren Text schwer bedienbar/prüfbar (A11y).
- Kein Container/fieldset: Technisch okay, aber Sync/Scroll/Existenz‑Prüfungen sind robuster mit einem Container‑Locator (z. B. `data-testid` auf `fieldset`).

---

## Komplettbeispiel (Demo)

Siehe `docs/examples/widgets_demo.html` und `locators/web/WidgetsDemo.yaml`:
- `Zahlungsmethode` → name‑basierte Gruppe (`group: zahlungsmethode`)
- `Lieferung` → fieldset mit `data-testid="rl-lieferung"` (container‑basiert)

Tests: `tests/WidgetsDemo.robot` enthält Fälle für beide Gruppen inkl. Cycle‑/WCM‑/REGX‑Prüfungen.

---

## Kurzreferenz: Variantenvergleich

| Variante | YAML | Auswahl | Verifikation | Scroll/Sync‑Ziel |
|---------|------|---------|--------------|------------------|
| name‑basiert | `group: <name>` | `name + value` (Adapter) | `name + expected` (Adapter) | kein elementbezogener Scroll (ohne Locator) |
| container‑basiert | `locator: { css: '[data-testid="…"]' }` | innerhalb des Containers: `input[type='radio'][value='<Wert>']` | `:checked` im Container, `value` vergleichen | Container‑Locator (scrollIntoView) |

Hinweis: Beide Varianten sind treiberunabhängig; sie beschreiben HTML‑Struktur, nicht den konkreten Web‑Treiber.

Hinweis: Für Web empfehlen wir die Klasse `WebRadioList`. Die bisherige `RadioList` bleibt als Alias/Abwärtskompatibilität bestehen.
