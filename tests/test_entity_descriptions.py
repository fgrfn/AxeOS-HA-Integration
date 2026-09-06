"""Tests for entity descriptions and translated names."""

import json
from pathlib import Path

from custom_components.axeos_ha_integration.binary_sensor import BINARY_SENSOR_TYPES
from custom_components.axeos_ha_integration.button import RESTART_BUTTON_DESCRIPTION
from custom_components.axeos_ha_integration.number import NUMBER_TYPES
from custom_components.axeos_ha_integration.sensor import SENSOR_TYPES
from custom_components.axeos_ha_integration.switch import SWITCH_TYPES

INTEGRATION_DIR = Path(__file__).parent.parent / "custom_components" / "axeos_ha_integration"


def descriptions_by_domain():
    """Return all entity descriptions grouped by platform."""
    return {
        "sensor": SENSOR_TYPES.values(),
        "binary_sensor": BINARY_SENSOR_TYPES.values(),
        "number": NUMBER_TYPES,
        "switch": SWITCH_TYPES,
        "button": (RESTART_BUTTON_DESCRIPTION,),
    }


def test_every_entity_has_english_and_german_name():
    """Every description references a name in all shipped languages."""
    translation_files = (
        INTEGRATION_DIR / "strings.json",
        INTEGRATION_DIR / "translations" / "en.json",
        INTEGRATION_DIR / "translations" / "de.json",
    )

    for path in translation_files:
        translations = json.loads(path.read_text(encoding="utf-8"))["entity"]
        for domain, descriptions in descriptions_by_domain().items():
            for description in descriptions:
                assert description.translation_key in translations[domain]
                assert translations[domain][description.translation_key]["name"]
