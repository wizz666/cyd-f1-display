# CYD F1 Display

A full-featured Formula 1 race display for the **ESP32-2432S028** ("Cheap Yellow Display") built with ESPHome and Home Assistant. Shows countdown to next race, live race data, championship standings, circuit layout images and more — all updating automatically without reflashing.

---

## Screenshots / Layout

```
┌──────────────────────────────────────────────────┐
│ [F1]  Japanese Grand Prix         18.4°C         │  ← Header
│       Suzuka Circuit              15:22 (+7h)    │
├──────────────────────────────────────────────────┤
│                        │ SENASTE RACE            │
│  Lör 29 Mar 09:00      │ Chinese Grand Prix      │
│  KVAL   8d 14h         │ 1 Antonelli             │
│                        │ 2 Russell               │
│  Sön 30 Mar 15:00      │ 3 Hamilton              │
│  RACE   9d 11h         ├─────────────────────────┤
│                        │ FÖRARMÄSTERSKAPET       │
│   [Suzuka circuit]     │ 1 RUS  62p              │
│                        │ 2 ANT  54p              │
│                        │ 3 NOR  48p              │
│                        │ 4 LEC  41p              │
│                        │ 5 PIA  38p              │
│                        ├─────────────────────────┤
│                        │   Tis 19 Mar  15:04     │
└────────────────────────┴─────────────────────────┘
```

### During a live race

```
┌──────────────────────────────────────────────────┐
│ [F1]  Japanese Grand Prix         22.1°C         │
│       Suzuka Circuit              15:22 (+7h)    │
├──────────────────────────────────────────────────┤
│                        │ LIVE                    │
│  YOUR DRIVERS           │ GREEN FLAG              │
│  1  VER  Leader        │ Varv 32                 │
│           S  12v       │ TRACK CLEAR             │
│  4  HAM  +8.4s         │ AFTER INC T3            │
│           M   8v       ├─────────────────────────┤
│  8  ALO  +22.1s        │ LIVE RACE               │
│           H   3v       │ 1 VER  Leader S         │
│                        │ 2 NOR  +2.1s  M         │
│   [Suzuka circuit]     │ 3 HAM  +8.4s  H         │
│                        │ 4 LEC  +12.1s S         │
│                        │ 5 PIA  +18.3s M         │
│                        ├─────────────────────────┤
│                        │   Tis 29 Mar  15:22     │
└────────────────────────┴─────────────────────────┘
```

---

## Hardware

| Component | Details |
|-----------|---------|
| **Display** | ESP32-2432S028 ("Cheap Yellow Display" / CYD) |
| **Screen** | ILI9341, 320×240px, landscape |
| **MCU** | ESP32 (dual-core, Wi-Fi) |
| **Purchase** | Available on AliExpress — search "ESP32-2432S028" |

> **Note:** There are several CYD variants. This config is for the **TPM408-2.8** variant which requires `mirror_x: true` and `model: M5STACK` in ESPHome. Using `model: ILI9341` clips the display at x=240.

---

## Required Home Assistant Integrations

### 1. pyscript (HACS)
Runs the Python scripts that feed data to the display.
- Install via HACS → Integrations → search "pyscript"
- Enable `allow_all_imports: true` in `configuration.yaml`:
  ```yaml
  pyscript:
    allow_all_imports: true
  ```

### 2. F1 Sensor (HACS)
Provides next race info, results, standings and weather.
- Install via HACS → Integrations → search "F1 Sensor"
- Provides: `sensor.f1_next_race`, `sensor.f1_last_race_results`, `sensor.f1_driver_standings`, `sensor.f1_race_track_time`, `sensor.f1_weather`

### 3. OpenF1 pyscript integration (custom)
Provides live session data — positions, flags, tyres, Race Control messages.
- See the [OpenF1 integration](../pyscript/openf1.py)
- Requires `packages/openf1.yaml` for input helpers
- Provides: `sensor.f1_session_status`, `sensor.f1_grid_display`, `sensor.f1_flag`, `sensor.f1_lap`, `sensor.f1_race_control_msg`, `sensor.f1_d1/d2/d3_*`

### 4. ESPHome (HACS or built-in)
For compiling and flashing the display firmware.
- Install via HACS or use the official ESPHome add-on in HA

---

## Files

| File | Purpose |
|------|---------|
| `esphome/cyd_countdown.yaml` | Main ESPHome firmware config |
| `pyscript/cyd_f1_esphome.py` | HA sensor logic (runs every minute + on events) |
| `scripts/update_f1_circuit.py` | Circuit image utility (kept as fallback) |
| `esphome/f1_logo.png` | F1 logo (52×26px, BGR-swapped) |
| `esphome/Roboto-Regular.ttf` | Font (regular) |
| `esphome/Roboto-Bold.ttf` | Font (bold) |
| `esphome/circuits/*.png` | 22 pre-processed circuit layout images |

---

## Installation

### Step 1 – Install required integrations
Install pyscript, F1 Sensor and OpenF1 as described above.

### Step 2 – Copy files
Copy all files to your HA config directory maintaining the folder structure:
```
config/
├── esphome/
│   ├── cyd_countdown.yaml
│   ├── f1_logo.png
│   ├── Roboto-Regular.ttf
│   ├── Roboto-Bold.ttf
│   └── circuits/
│       ├── australia.png
│       ├── japan.png
│       └── ... (all 22 circuits)
├── pyscript/
│   └── cyd_f1_esphome.py
└── scripts/
    └── update_f1_circuit.py
```

### Step 3 – Configure secrets
Add to `secrets.yaml`:
```yaml
wifi_ssid: "YourWiFiName"
wifi_password: "YourWiFiPassword"
fallback_ap_password: "cyd-fallback"
api_encryption_key: "generate-with-esphome-dashboard"
ota_password: "generate-random-hex"
```

### Step 4 – Flash the display
1. Open ESPHome dashboard in HA
2. Add the `cyd_countdown.yaml` device
3. Connect the CYD via USB
4. Click **Install → Plug into this computer**
5. First flash must be wired. Subsequent updates can be OTA (wireless)

> **If the device is stuck:** Hold BOOT button → press+release RST → release BOOT → flash via [web.esphome.io](https://web.esphome.io)

### Step 5 – Connect to Home Assistant
After flashing:
1. Go to **Settings → Devices & Services**
2. The CYD should appear as a discovered device
3. Click **Configure** to connect it to HA

### Step 6 – Reload pyscript
In HA Developer Tools → Services → call `pyscript.reload`. The display will start updating within 30 seconds.

---

## Configuring Live Race — Followed Drivers

During a live race the left column shows your 3 **followed drivers** with position, gap to leader and tyre compound. Configure which drivers to follow:

1. Go to **Settings → Devices & Services → Helpers** (or Developer Tools → States)
2. Find `input_number.f1_followed_1`, `f1_followed_2`, `f1_followed_3`
3. Set each to a **driver number** (e.g. 1 = Verstappen, 44 = Hamilton, 63 = Russell)

| input_number | Default | Example |
|---|---|---|
| `f1_followed_1` | 1 (Verstappen) | Set to 63 for Russell |
| `f1_followed_2` | 44 (Hamilton) | Set to 4 for Norris |
| `f1_followed_3` | 77 (Bottas) | Set to 16 for Leclerc |

Set to `0` to disable a slot.

---

## How It Works

### Normal mode (between races)
- **Every minute:** `cyd_f1_esphome.py` reads `sensor.f1_next_race` and updates countdown, dates, circuit time and temperature
- **Every hour + on standings change:** Updates last race top-3 and championship standings
- **On circuit change:** `sensor.cyd_circuit_slug` updates → display lambda picks the correct pre-compiled circuit image within 30 seconds

### Live mode (during Race or Sprint session)
When `sensor.f1_session_status` becomes `Race` or `Sprint`:

1. `cyd_live_mode` → `"1"` (display switches within 30s)
2. **Left column** → YOUR DRIVERS: position, gap to leader, tyre compound+age for your 3 followed drivers
3. **Right top** → LIVE: current flag (color-coded green/yellow/red), lap number, Race Control message
4. **Right bottom** → LIVE RACE: live top-5 positions with gap and tyre
5. When session ends → everything reverts automatically to standings/results

### Circuit images
All 22 circuits for the 2026 F1 calendar are pre-processed and compiled into the firmware:
- BGR-swapped (required for 8BIT color palette)
- Composited onto dark background `Color(13, 17, 23)`
- Resized to 130×73px
- Stored in `esphome/circuits/<slug>.png`

The display selects the correct image at runtime based on `sensor.cyd_circuit_slug` — **no reflashing needed when the circuit changes.**

---

## Circuit Images — 2026 Calendar

| Slug | Grand Prix |
|------|-----------|
| `australia` | Australian GP (Albert Park) |
| `china` | Chinese GP (Shanghai) |
| `japan` | Japanese GP (Suzuka) |
| `miami` | Miami GP |
| `canada` | Canadian GP (Montreal) |
| `monaco` | Monaco GP |
| `barcelona-catalunya` | Spanish GP (Barcelona) |
| `austria` | Austrian GP (Red Bull Ring) |
| `great-britain` | British GP (Silverstone) |
| `belgium` | Belgian GP (Spa) |
| `hungary` | Hungarian GP (Hungaroring) |
| `netherlands` | Dutch GP (Zandvoort) |
| `italy` | Italian GP (Monza) |
| `spain` | Spanish GP (Madrid – new 2026) |
| `azerbaijan` | Azerbaijan GP (Baku) |
| `singapore` | Singapore GP (Marina Bay) |
| `united-states` | US GP (Austin) |
| `mexico` | Mexican GP |
| `brazil` | Brazilian GP (Interlagos) |
| `las-vegas` | Las Vegas GP |
| `qatar` | Qatar GP (Losail) |
| `united-arab-emirates` | Abu Dhabi GP (Yas Marina) |

---

## Tyre Colors

| Compound | Color | Display |
|----------|-------|---------|
| Soft | Red | `S` |
| Medium | Yellow | `M` |
| Hard | White | `H` |
| Intermediate | Green | `I` |
| Wet | Blue | `W` |

---

## Flag Colors

| Flag | Color |
|------|-------|
| GREEN | Green |
| YELLOW / SAFETY CAR / VSC | Yellow |
| RED | Red |
| CHEQUERED | Green |

---

## ESPHome — Critical Configuration Notes

```yaml
display:
  - platform: ili9xxx
    model: M5STACK          # NOT ILI9341 — clips at x=240
    cs_pin: GPIO15
    dc_pin: GPIO2
    color_palette: 8BIT     # REQUIRED — without this: FAILED (out of RAM)
    invert_colors: false
    transform:
      mirror_x: true        # REQUIRED for TPM408-2.8 CYD variant
```

| Issue | Cause | Fix |
|-------|-------|-----|
| Display clipped at x=240 | Using `model: ILI9341` | Use `model: M5STACK` |
| Compilation FAILED | Missing `color_palette: 8BIT` | Add it |
| Display mirrored | Missing `transform: mirror_x: true` | Add it |
| RGB LED turns on | Using `reset_pin: GPIO4` | Remove it — GPIO4 is RGB LED red |
| Images wrong colors | 8BIT palette swaps R/B | PNG files must be BGR-swapped with Pillow |
| Swedish chars broken | Using `gfonts://Roboto` | Use local Roboto TTF with å/ä/ö in glyphs |

---

## SPI Pins (ESP32-2432S028)

| Pin | GPIO |
|-----|------|
| CLK | GPIO14 |
| MOSI | GPIO13 |
| MISO | GPIO12 |
| CS | GPIO15 |
| DC | GPIO2 |
| Backlight | GPIO21 |

---

## Troubleshooting

**Display shows nothing after flash**
- Check that HA API connection is configured (Settings → Devices & Services → Configure on the CYD device)
- Verify pyscript is running: Developer Tools → States → search `cyd_race_name`

**Circuit image not showing / wrong circuit**
- Check `sensor.cyd_circuit_slug` in Developer Tools → States
- Should match one of the slugs in the table above

**Live mode not activating**
- Check `sensor.f1_session_status` — must be `Race` or `Sprint`
- Check `sensor.cyd_live_mode` — should flip to `1` when race starts
- Verify OpenF1 pyscript is loaded and running

**OTA flash fails**
- Hold BOOT → press+release RST → release BOOT
- Flash via [web.esphome.io](https://web.esphome.io) with factory binary

---

## License

MIT — free to use, modify and share.
