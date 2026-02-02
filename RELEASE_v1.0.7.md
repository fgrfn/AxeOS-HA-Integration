# Release Notes v1.0.7

## 🎉 Neue Features

### Number Entitäten für editierbare Werte
- **Fan Speed**: Lüftergeschwindigkeit direkt in Home Assistant einstellen (0-100%)
- **Frequency**: Mining-Frequenz anpassen (200-600 MHz)
- **Core Voltage**: Kernspannung konfigurieren (1000-1400 mV)

### Custom Services
Drei neue Services für die Miner-Steuerung:
- `axeos_ha_integration.restart_miner`: Miner neustarten
- `axeos_ha_integration.set_frequency`: Frequenz setzen (mit Validierung)
- `axeos_ha_integration.set_voltage`: Spannung setzen (mit Validierung)

Alle Services sind im Home Assistant UI verfügbar mit benutzerfreundlichen Eingabefeldern.

### Unit Tests
- Umfassende Test-Suite mit pytest
- Tests für API, Sensoren und Binary-Sensoren
- Über 30 Testfälle für bessere Code-Qualität
- Coverage-Reports verfügbar

## 🔧 Verbesserungen
- Services werden automatisch registriert und beim Entfernen aufgeräumt
- Neue API-Methoden für Miner-Steuerung
- Bessere Dokumentation im Test-Verzeichnis

## 📝 Für Entwickler
```bash
# Tests ausführen
pip install -r requirements-test.txt
pytest tests/

# Mit Coverage
pytest --cov=custom_components.axeos_ha_integration --cov-report=html tests/
```

## 🔗 Links
- [Vollständiger Changelog](CHANGELOG.md)
- [GitHub Repository](https://github.com/fgrfn/AxeOS-HA-Integration)
