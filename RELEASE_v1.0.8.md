# Release Notes v1.0.8

## 🎉 NerdAxe Support

Diese Version fügt vollständige Unterstützung für **NerdAxe-Geräte** hinzu!

### Neue Sensoren (25+)

#### Erweiterte Hashrate-Metriken
- **Hashrate (1 Minute)**: Durchschnitt der letzten Minute
- **Hashrate (10 Minuten)**: Durchschnitt der letzten 10 Minuten  
- **Hashrate (1 Stunde)**: Durchschnitt der letzten Stunde
- **Hashrate (1 Tag)**: Durchschnitt der letzten 24 Stunden

#### Erweiterte Power/Voltage-Limits
- **Min/Max Power**: Minimal- und Maximalwerte für Stromverbrauch
- **Min/Max Voltage**: Minimal- und Maximalwerte für Spannung
- **Default Core Voltage**: Werkseinstellung für Kernspannung

#### Lüftersteuerung
- **Manual Fan Speed**: Manuelle Lüftergeschwindigkeit-Einstellung
- **Fan RPM**: Aktuelle Umdrehungen pro Minute

#### PID-Controller
- **PID P/I/D Values**: Temperaturregelungs-Parameter
- **PID Target Temp**: Alternative zum temptarget-Sensor
- **Overheat Temperature**: Überhitzungs-Schwellenwert

#### Stratum Pool Details
- **Pool Mode**: Aktueller Pool-Modus
- **Active Pool Mode**: Aktiver Pool-Modus
- **Pool Balance**: Pool-Balance
- **Stratum Total Best Difficulty**: Kumulierte beste Schwierigkeit
- **Stratum Pool Difficulty**: Aktuelle Pool-Schwierigkeit

#### Hardware-Diagnostik
- **Duplicate HW Nonces**: Fehlerhafte Hardware-Nonces
- **Found Blocks**: In dieser Session gefundene Blöcke
- **Total Found Blocks**: Insgesamt gefundene Blöcke
- **Last Reset Reason**: Grund für letzten Neustart (z.B. POWERON)
- **Running Partition**: Aktive Firmware-Partition

#### Konfiguration
- **Default Frequency**: Werkseinstellung für Frequenz
- **VR Frequency**: Voltage Regulator Frequenz
- **Default VR Frequency**: VR-Frequenz Werkseinstellung
- **Job Interval**: Mining-Job-Intervall
- **Default Theme**: UI-Theme-Einstellung
- **Free Heap (Internal)**: Interner Speicher

### Neue Binary Sensoren (6)

- **Shutdown**: Shutdown-Status
- **Auto Screen Off**: Automatisches Bildschirm-Ausschalten
- **Keep Stratum Connection**: Stratum-Verbindung aufrechterhalten
- **OTP (One-Time Programming)**: OTP-Status
- **Stratum Enonce Subscribe**: Enonce-Abonnement für primären Pool
- **Fallback Stratum Enonce Subscribe**: Enonce-Abonnement für Fallback-Pool

## 🔧 Verbesserungen

### Bessere Geräte-Kompatibilität
- IP-Adresse-Sensor unterstützt jetzt beide Felder: `ip` (BitAxe) und `hostip` (NerdAxe)
- Automatische Erkennung von verschachtelten API-Strukturen
- Verbesserte `get_value()` Funktionen für komplexe Datenstrukturen

### Verschachtelte Datenpfade
Die Integration unterstützt jetzt verschachtelte Objekte in der API-Antwort:
- `stratum.poolMode`, `stratum.usingFallback`, etc.
- Flexible Fallback-Logik für verschiedene API-Versionen

## 📊 Geräte-Unterstützung

Diese Integration funktioniert jetzt mit:
- ✅ **BitAxe** (alle Modelle mit Standard-AxeOS)
- ✅ **NerdAxe** (ESP-Miner-NerdAxe Firmware)

Beide Gerätetypen werden automatisch erkannt und die passenden Sensoren werden erstellt.

## 🔗 Links
- [Vollständiger Changelog](CHANGELOG.md)
- [GitHub Repository](https://github.com/fgrfn/AxeOS-HA-Integration)
- [NerdAxe Firmware](https://github.com/BitMaker-hub/ESP-Miner-NerdAxe)
