# =============================================================================
# CYD F1 ESPHome – Sätter HA-states för CYD countdown-display  v2.0
# =============================================================================
# Uppdaterar sensor-states som ESPHome-displayen prenumererar på:
#   - Klocka hanteras av ESPHome självt (HA time-sync)
#   - F1: nästa race, kval, nedräkning med färgkodning varje minut
#   - F1: föregående race topp-3 vid startup + varje timme
#   - F1: live race – positioner, flagg, varv, RC-meddelande
# =============================================================================

import datetime

CIRCUIT_SLUGS = {
    "albert park":       "australia",
    "melbourne":         "australia",
    "shanghai":          "china",
    "suzuka":            "japan",
    "miami":             "miami",
    "canada":            "canada",
    "montreal":          "canada",
    "gilles villeneuve": "canada",
    "monaco":            "monaco",
    "barcelona":         "barcelona-catalunya",
    "catalonia":         "barcelona-catalunya",
    "catalunya":         "barcelona-catalunya",
    "red bull ring":     "austria",
    "spielberg":         "austria",
    "silverstone":       "great-britain",
    "spa":               "belgium",
    "hungaroring":       "hungary",
    "budapest":          "hungary",
    "zandvoort":         "netherlands",
    "monza":             "italy",
    "madrid":            "spain",
    "ifema":             "spain",
    "baku":              "azerbaijan",
    "marina bay":        "singapore",
    "singapore":         "singapore",
    "americas":          "united-states",
    "austin":            "united-states",
    "mexico":            "mexico",
    "hermanos":          "mexico",
    "interlagos":        "brazil",
    "sao paulo":         "brazil",
    "jose carlos pace":  "brazil",
    "las vegas":         "las-vegas",
    "losail":            "qatar",
    "qatar":             "qatar",
    "yas marina":        "united-arab-emirates",
    "abu dhabi":         "united-arab-emirates",
}

COMPOUND_SHORT = {
    "SOFT": "S", "MEDIUM": "M", "HARD": "H",
    "INTERMEDIATE": "I", "INTER": "I", "WET": "W",
}

FLAG_COLOR = {
    "GREEN":       "green",
    "YELLOW":      "yellow",
    "RED":         "red",
    "SAFETY CAR":  "yellow",
    "SC":          "yellow",
    "VSC":         "yellow",
    "CHEQUERED":   "green",
}

DAYS   = ["Mån", "Tis", "Ons", "Tor", "Fre", "Lör", "Sön"]
MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "Maj", "Jun",
          "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]


def _circuit_slug(circuit_name):
    name_lower = circuit_name.lower()
    for key, slug in CIRCUIT_SLUGS.items():
        if key in name_lower:
            return slug
    return "japan"  # fallback


def _sget(entity, default=""):
    try:
        v = state.get(entity)
        return v if v not in (None, "unknown", "unavailable") else default
    except Exception:
        return default


def _countdown_color(seconds_left):
    if seconds_left <= 0:
        return "green"
    elif seconds_left < 3600:
        return "green"
    elif seconds_left < 86400:
        return "yellow"
    else:
        return "red"


def _format_countdown(seconds_left):
    if seconds_left <= 0:
        return "NU!"
    days  = int(seconds_left // 86400)
    hours = int((seconds_left % 86400) // 3600)
    mins  = int((seconds_left % 3600) // 60)
    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {mins}m"
    else:
        return f"{mins}m"


def _format_dt(iso_str):
    if not iso_str:
        return ""
    try:
        dt       = datetime.datetime.fromisoformat(iso_str)
        day_name = DAYS[dt.weekday()]
        month    = MONTHS[dt.month]
        return f"{day_name} {dt.day} {month} {dt.strftime('%H:%M')}"
    except Exception:
        return ""


def _seconds_until(iso_str):
    if not iso_str:
        return 999999
    try:
        dt_event = datetime.datetime.fromisoformat(iso_str)
        dt_now   = datetime.datetime.now(tz=dt_event.tzinfo)
        return (dt_event - dt_now).total_seconds()
    except Exception:
        return 999999


def _update_cyd_standings():
    """Skriver förarmästerskap (topp 5) till cyd_ms1-5."""
    standings_raw = _sget("sensor.f1_driver_standings", "")
    if "|" in standings_raw:
        entries = [e for e in standings_raw.split("|") if e.strip()]
        ms_keys = ["cyd_ms1", "cyd_ms2", "cyd_ms3", "cyd_ms4", "cyd_ms5"]
        for i in range(5):
            if i < len(entries):
                dot = entries[i].find(".")
                val = entries[i][dot+1:].strip() if dot >= 0 else entries[i].strip()
                state.set(f"sensor.{ms_keys[i]}", val)
            else:
                state.set(f"sensor.{ms_keys[i]}", "–")


def _parse_compound(raw):
    """Parsar '🔴 SOFT' → ('S', 'S') — kort bokstav för display."""
    raw_upper = raw.upper()
    for key, short in COMPOUND_SHORT.items():
        if key in raw_upper:
            return short
    return "?"


def _split_rc_msg(msg, max_len=19):
    """Delar RC-meddelande i två displayrader (max_len tecken per rad)."""
    if not msg or msg in ("–", "unknown", "unavailable"):
        return "–", ""
    msg = msg.upper()
    if len(msg) <= max_len:
        return msg, ""
    split_at = msg.rfind(" ", 0, max_len)
    if split_at == -1:
        split_at = max_len
    line2 = msg[split_at + 1:split_at + 1 + max_len]
    return msg[:split_at], line2


# ---------------------------------------------------------------------------
# F1 nedräkning – uppdateras varje minut
# ---------------------------------------------------------------------------

@time_trigger("startup", "cron(* * * * *)")
def cyd_esphome_update_f1():
    """Uppdaterar F1-states för ESPHome-display varje minut."""
    attrs = state.getattr("sensor.f1_next_race") or {}

    race_name    = attrs.get("race_name", "–")
    circuit_name = attrs.get("circuit_name", "–")
    if len(race_name) > 22:
        race_name = race_name[:21] + "."
    if len(circuit_name) > 22:
        circuit_name = circuit_name[:21] + "."

    state.set("sensor.cyd_race_name",    race_name)
    state.set("sensor.cyd_circuit_name", circuit_name)
    state.set("sensor.cyd_circuit_slug", _circuit_slug(circuit_name))

    # Kval
    qual_disp = attrs.get("qualifying_start")
    if qual_disp:
        secs = _seconds_until(qual_disp)
        state.set("sensor.cyd_qual_date",  _format_dt(qual_disp))
        state.set("sensor.cyd_qual_count", _format_countdown(secs))
        state.set("sensor.cyd_qual_color", _countdown_color(secs))
    else:
        state.set("sensor.cyd_qual_date",  "–")
        state.set("sensor.cyd_qual_count", "–")
        state.set("sensor.cyd_qual_color", "red")

    # Sprint (visas bara om sprint_start finns)
    sprint_disp = attrs.get("sprint_start")
    if sprint_disp and sprint_disp != "None":
        secs = _seconds_until(sprint_disp)
        state.set("sensor.cyd_sprint_date",  _format_dt(sprint_disp))
        state.set("sensor.cyd_sprint_count", _format_countdown(secs))
        state.set("sensor.cyd_sprint_color", _countdown_color(secs))
        state.set("sensor.cyd_sprint_show",  "1")
    else:
        state.set("sensor.cyd_sprint_date",  "–")
        state.set("sensor.cyd_sprint_count", "–")
        state.set("sensor.cyd_sprint_color", "red")
        state.set("sensor.cyd_sprint_show",  "0")

    # Race
    race_disp = attrs.get("race_start")
    if race_disp:
        secs = _seconds_until(race_disp)
        state.set("sensor.cyd_race_date",  _format_dt(race_disp))
        state.set("sensor.cyd_race_count", _format_countdown(secs))
        state.set("sensor.cyd_race_color", _countdown_color(secs))
    else:
        state.set("sensor.cyd_race_date",  "–")
        state.set("sensor.cyd_race_count", "–")
        state.set("sensor.cyd_race_color", "red")

    # Circuit lokaltid
    track_time = _sget("sensor.f1_race_track_time", "")
    if track_time:
        t_attrs = state.getattr("sensor.f1_race_track_time") or {}
        offset = t_attrs.get("utc_offset", "")
        try:
            circuit_utc_h = int(str(offset).replace("+", "").strip()) // 100
            local_utc_h = int(datetime.datetime.now().astimezone().utcoffset().total_seconds() // 3600)
            rel = circuit_utc_h - local_utc_h
            rel_str = f"+{rel}h" if rel >= 0 else f"{rel}h"
            state.set("sensor.cyd_circuit_time", f"{track_time} ({rel_str})")
        except Exception:
            state.set("sensor.cyd_circuit_time", track_time)
    else:
        state.set("sensor.cyd_circuit_time", "–")

    # Banväder
    w_raw = _sget("sensor.f1_weather", "")
    try:
        state.set("sensor.cyd_circuit_temp", f"{float(w_raw):.1f}")
    except Exception:
        state.set("sensor.cyd_circuit_temp", w_raw if w_raw else "–")


# ---------------------------------------------------------------------------
# F1 föregående race topp-3 + förarmästerskap – startup + varje timme
# ---------------------------------------------------------------------------

@time_trigger("startup", "cron(0 * * * *)")
@state_trigger("sensor.f1_last_race_results", "sensor.f1_driver_standings")
def cyd_esphome_update_results_and_price():
    """Uppdaterar föregående race topp-3 och förarmästerskap."""

    # --- Föregående race ---
    attrs   = state.getattr("sensor.f1_last_race_results") or {}
    results = attrs.get("results", [])
    name    = attrs.get("race_name", "–")
    if len(name) > 20:
        name = name[:19] + "."
    state.set("sensor.cyd_last_race", name)

    top3 = sorted(
        [r for r in results if r.get("position") in ("1", "2", "3")],
        key=lambda r: int(r.get("position", 9))
    )
    for i, key in enumerate(["cyd_p1", "cyd_p2", "cyd_p3"]):
        if i < len(top3):
            driver = top3[i].get("driver", {})
            state.set(f"sensor.{key}", driver.get("familyName", "–"))
        else:
            state.set(f"sensor.{key}", "–")

    # --- Förarmästerskap – hoppa över under pågående race ---
    status = _sget("sensor.f1_session_status", "inactive")
    if status not in ("Race", "Sprint"):
        _update_cyd_standings()


# ---------------------------------------------------------------------------
# F1 live race – uppdateras vid sessionsstatus, grid, flagg, varv, RC-msg
# ---------------------------------------------------------------------------

@time_trigger("startup")
@state_trigger("sensor.f1_session_status", "sensor.f1_grid_display",
               "sensor.f1_flag", "sensor.f1_lap", "sensor.f1_race_control_msg")
def cyd_esphome_update_live(**kwargs):
    """Hanterar live race-läge: positioner, flagg, varv och RC-meddelande."""
    status  = _sget("sensor.f1_session_status", "inactive")
    is_live = status in ("Race", "Sprint")

    state.set("sensor.cyd_live_mode", "1" if is_live else "0")

    if is_live:
        # --- Live positioner (topp 5) ---
        grid_raw = _sget("sensor.f1_grid_display", "")
        if "|" in grid_raw:
            entries = [e for e in grid_raw.split("|") if e.strip()]
            ms_keys = ["cyd_ms1", "cyd_ms2", "cyd_ms3", "cyd_ms4", "cyd_ms5"]
            for i in range(5):
                if i < len(entries):
                    dot = entries[i].find(".")
                    val = entries[i][dot+1:].strip() if dot >= 0 else entries[i].strip()
                    state.set(f"sensor.{ms_keys[i]}", val[:14])
                else:
                    state.set(f"sensor.{ms_keys[i]}", "–")

        # --- Flagg ---
        flag_raw = _sget("sensor.f1_flag", "GREEN").upper()
        state.set("sensor.cyd_flag",       flag_raw[:12])
        state.set("sensor.cyd_flag_color", FLAG_COLOR.get(flag_raw, "yellow"))

        # --- Varv ---
        lap = _sget("sensor.f1_lap", "")
        state.set("sensor.cyd_lap", f"Varv {lap}" if lap else "–")

        # --- RC-meddelande (två rader) ---
        rc = _sget("sensor.f1_race_control_msg", "")
        line1, line2 = _split_rc_msg(rc)
        state.set("sensor.cyd_rc_line1", line1)
        state.set("sensor.cyd_rc_line2", line2)

        # --- Följda förare (d1/d2/d3) ---
        for n in range(1, 4):
            pos       = _sget(f"sensor.f1_d{n}_position", "–")
            name      = _sget(f"sensor.f1_d{n}_name",     "–")
            gap       = _sget(f"sensor.f1_d{n}_gap",      "–")
            compound  = _sget(f"sensor.f1_d{n}_compound", "")
            tyre_age  = _sget(f"sensor.f1_d{n}_tyre_age", "")
            comp_short = _parse_compound(compound)
            tyre_str   = f"{comp_short} {tyre_age}v" if tyre_age else comp_short
            state.set(f"sensor.cyd_d{n}_pos",  str(pos))
            state.set(f"sensor.cyd_d{n}_name", str(name))
            state.set(f"sensor.cyd_d{n}_gap",  str(gap)[:10])
            state.set(f"sensor.cyd_d{n}_tyre", tyre_str)

    else:
        # --- Återställ mästerskap när race är slut ---
        _update_cyd_standings()
        state.set("sensor.cyd_flag",       "–")
        state.set("sensor.cyd_flag_color", "red")
        state.set("sensor.cyd_lap",        "–")
        state.set("sensor.cyd_rc_line1",   "–")
        state.set("sensor.cyd_rc_line2",   "")
        for n in range(1, 4):
            state.set(f"sensor.cyd_d{n}_pos",  "–")
            state.set(f"sensor.cyd_d{n}_name", "–")
            state.set(f"sensor.cyd_d{n}_gap",  "–")
            state.set(f"sensor.cyd_d{n}_tyre", "–")
