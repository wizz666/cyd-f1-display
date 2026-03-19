#!/usr/bin/env python3
"""
Kopierar rätt F1 circuit-bild till /config/esphome/f1_circuit.png.
Alla bilder är förprocessade (BGR-swap, 130×73px, mörk bakgrund) och
sparade i /config/esphome/circuits/<slug>.png.

Usage: python3 update_f1_circuit.py "<circuit_name>"
"""

import sys
import shutil
from pathlib import Path

CIRCUITS_DIR = Path("/config/esphome/circuits")
OUTPUT_PATH  = Path("/config/esphome/f1_circuit.png")

# Mappning: nyckelord i circuit_name → filnamn (slug = filnamn i circuits/)
# Baserat på 2026 F1-kalender: 22 GP
CIRCUIT_TO_SLUG = {
    # Australien
    "albert park":          "australia",
    "melbourne":            "australia",
    # Kina
    "shanghai":             "china",
    # Japan
    "suzuka":               "japan",
    # Miami
    "miami":                "miami",
    # Kanada
    "canada":               "canada",
    "montreal":             "canada",
    "gilles villeneuve":    "canada",
    # Monaco
    "monaco":               "monaco",
    # Spanien (Barcelona)
    "barcelona":            "barcelona-catalunya",
    "catalonia":            "barcelona-catalunya",
    "catalunya":            "barcelona-catalunya",
    # Österrike
    "red bull ring":        "austria",
    "spielberg":            "austria",
    # Storbritannien
    "silverstone":          "great-britain",
    # Belgien
    "spa":                  "belgium",
    # Ungern
    "hungaroring":          "hungary",
    "budapest":             "hungary",
    # Nederländerna
    "zandvoort":            "netherlands",
    # Italien
    "monza":                "italy",
    # Spanien (Madrid – ny 2026)
    "madrid":               "spain",
    "ifema":                "spain",
    # Azerbajdzjan
    "baku":                 "azerbaijan",
    # Singapore
    "marina bay":           "singapore",
    "singapore":            "singapore",
    # USA (Austin)
    "americas":             "united-states",
    "austin":               "united-states",
    # Mexiko
    "mexico":               "mexico",
    "hermanos":             "mexico",
    # Brasilien
    "interlagos":           "brazil",
    "sao paulo":            "brazil",
    "jose carlos pace":     "brazil",
    # Las Vegas
    "las vegas":            "las-vegas",
    # Qatar
    "losail":               "qatar",
    "qatar":                "qatar",
    # Abu Dhabi
    "yas marina":           "united-arab-emirates",
    "abu dhabi":            "united-arab-emirates",
}


def circuit_to_slug(circuit_name):
    name_lower = circuit_name.lower()
    for key, slug in CIRCUIT_TO_SLUG.items():
        if key in name_lower:
            return slug
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: update_f1_circuit.py <circuit_name>", file=sys.stderr)
        sys.exit(1)

    circuit_name = " ".join(sys.argv[1:])
    slug = circuit_to_slug(circuit_name)

    if not slug:
        print(f"ERROR: okänd bana '{circuit_name}'", file=sys.stderr)
        sys.exit(1)

    src = CIRCUITS_DIR / f"{slug}.png"
    if not src.exists():
        print(f"ERROR: bildfil saknas: {src}", file=sys.stderr)
        sys.exit(1)

    shutil.copy2(str(src), str(OUTPUT_PATH))
    print(f"OK: {circuit_name!r} → {slug}.png → f1_circuit.png")


if __name__ == "__main__":
    main()
