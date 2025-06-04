# AxeOS-HA-Integration

**AxeOS HA Integration** ist eine Home Assistant Custom Component zur Überwachung und Steuerung von BitAxe Miner-Geräten (AxeOS).

## Installation über HACS

1. Öffne Home Assistant und navigiere zu **HACS → Einstellungen → Custom Repositories**.
2. Füge die Repository-URL hinzu (zum Beispiel: `https://github.com/deinusername/ha-axeos-integration`) und wähle als Kategorie **Integration**.
3. Gehe zu **HACS → Integrationen**, suche nach **AxeOS-HA-Integration** und installiere sie.
4. Starte Home Assistant neu.
5. Navigiere zu **Einstellungen → Integrationen → + Hinzufügen → AxeOS-HA-Integration**, um deinen AxeOS Miner hinzuzufügen.

## Manuelle Installation

1. Lade das Repository herunter.
2. Kopiere den Ordner `axeos` nach `/config/custom_components/`.
3. Home Assistant neu starten.
4. Füge die Integration unter **Einstellungen → Integrationen → + Hinzufügen → AxeOS-HA-Integration** hinzu.

## Konfiguration

Über den Konfigurationsassistenten gibst du die IP-Adresse oder den Hostnamen deines AxeOS Miners und einen optionalen Namen an.

## Unterstützung & Mitwirken

Beiträge und Verbesserungen sind willkommen. Erstelle bitte Pull-Requests auf GitHub, um neue Funktionen oder Fehlerbehebungen hinzuzufügen.
