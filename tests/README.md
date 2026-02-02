# Tests für AxeOS HA Integration

Diese Integration enthält Unit-Tests für die Hauptkomponenten.

## Installation der Test-Abhängigkeiten

```bash
pip install -r requirements-test.txt
```

## Tests ausführen

Alle Tests ausführen:
```bash
pytest tests/
```

Mit Coverage-Report:
```bash
pytest --cov=custom_components.axeos_ha_integration --cov-report=html tests/
```

Einzelne Test-Dateien ausführen:
```bash
pytest tests/test_api.py
pytest tests/test_sensor.py
pytest tests/test_binary_sensor.py
```

## Test-Struktur

- `test_api.py` - Tests für die API-Kommunikation mit dem BitAxe Miner
- `test_sensor.py` - Tests für die Sensor-Entitäten
- `test_binary_sensor.py` - Tests für die Binary-Sensor-Entitäten
- `conftest.py` - Pytest-Konfiguration und gemeinsame Fixtures

## Hinweise

Die Tests verwenden Mocks für aiohttp und Home Assistant Komponenten, daher ist keine echte BitAxe-Hardware erforderlich.
