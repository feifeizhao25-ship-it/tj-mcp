#!/usr/bin/env python3
# TianJi MCP server — computation-first astrology tools for AI agents.
# Engine: kerykeion 6.x (libephemeris). Transport: streamable HTTP (MCP spec).
import json
from datetime import datetime, timezone
from fastmcp import FastMCP
from kerykeion import AstrologicalSubjectFactory

mcp = FastMCP("TianJi Astrology", instructions=(
    "TianJi computes real astrological charts (ephemeris-grade planetary positions, "
    "houses, aspects) — not generic sun-sign content. Use compute_natal_chart for birth "
    "charts, get_current_transits for today's sky, get_sign_profile for reference facts. "
    "All computation, no horoscope fluff. By tianji-astrology.com."
))

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
ELEMENT = {"Aries":"fire","Leo":"fire","Sagittarius":"fire","Taurus":"earth","Virgo":"earth","Capricorn":"earth",
           "Gemini":"air","Libra":"air","Aquarius":"air","Cancer":"water","Scorpio":"water","Pisces":"water"}
MODALITY = {"Aries":"cardinal","Cancer":"cardinal","Libra":"cardinal","Capricorn":"cardinal",
            "Taurus":"fixed","Leo":"fixed","Scorpio":"fixed","Aquarius":"fixed",
            "Gemini":"mutable","Virgo":"mutable","Sagittarius":"mutable","Pisces":"mutable"}
RULER = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun","Virgo":"Mercury",
         "Libra":"Venus","Scorpio":"Pluto (trad. Mars)","Sagittarius":"Jupiter","Capricorn":"Saturn",
         "Aquarius":"Uranus (trad. Saturn)","Pisces":"Neptune (trad. Jupiter)"}

PLANETS = ["sun","moon","mercury","venus","mars","jupiter","saturn","uranus","neptune","pluto"]
HOUSE_WORDS = ["first","second","third","fourth","fifth","sixth","seventh","eighth","ninth","tenth","eleventh","twelfth"]
ASPECTS = [("conjunction", 0, 8), ("sextile", 60, 4), ("square", 90, 7),
           ("trine", 120, 7), ("opposition", 180, 8)]

def _house_num(h):
    s = str(h)
    for i, w in enumerate(HOUSE_WORDS, 1):
        if w.capitalize() in s:
            return i
    try:
        return int(s)
    except Exception:
        return s

def _planet_row(p):
    return {"name": str(p.name).capitalize(), "sign": p.sign, "position": round(p.abs_pos % 30, 3),
            "abs_pos": round(p.abs_pos, 3), "house": _house_num(p.house),
            "retrograde": bool(getattr(p, "retrograde", False))}

def _compute_aspects(planets, max_orbit_delta=0.0):
    out = []
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            sep = abs(planets[i]["abs_pos"] - planets[j]["abs_pos"])
            if sep > 180:
                sep = 360 - sep
            for name, angle, orb in ASPECTS:
                d = abs(sep - angle)
                if d <= orb + max_orbit_delta:
                    out.append({"p1": planets[i]["name"], "p2": planets[j]["name"],
                                "aspect": name, "orbit": round(d, 2)})
                    break
    return sorted(out, key=lambda a: a["orbit"])

def _chart_payload(sub, label):
    planets = [_planet_row(getattr(sub, n)) for n in PLANETS]
    houses = []
    for i, w in enumerate(HOUSE_WORDS, 1):
        h = getattr(sub, f"{w}_house")
        houses.append({"house": i, "sign": h.sign, "position": round(h.abs_pos % 30, 3),
                       "abs_pos": round(h.abs_pos, 3)})
    return {"label": label, "engine": "kerykeion 6 / libephemeris", "zodiac": "tropical",
            "houses_system": "Placidus",
            "planets": planets, "houses": houses,
            "aspects": _compute_aspects(planets),
            "computed_at": datetime.now(timezone.utc).isoformat()}

def _subject(name, year, month, day, hour, minute, city, nation, lng, lat, tz_str):
    kw = dict(name=name, year=year, month=month, day=day, hour=hour, minute=minute)
    if lng is not None and lat is not None and tz_str:
        kw.update(lng=lng, lat=lat, tz_str=tz_str, online=False)
    else:
        kw.update(city=city, nation=nation)
    return AstrologicalSubjectFactory.from_birth_data(**kw)

@mcp.tool
def compute_natal_chart(name: str, year: int, month: int, day: int, hour: int = 12,
                        minute: int = 0, city: str = "Greenwich", nation: str = "GB",
                        lng: float | None = None, lat: float | None = None,
                        tz_str: str | None = None) -> str:
    """Compute a full natal (birth) chart: 10 planets (sign/degree/house/retrograde),
    12 Placidus house cusps, and inter-planetary aspects (major aspects, classic orbs).
    Pass lng/lat/tz_str (e.g. -74.01, 40.71, 'America/New_York') for exact offline
    computation; otherwise city+nation are geocoded online."""
    sub = _subject(name, year, month, day, hour, minute, city, nation, lng, lat, tz_str)
    return json.dumps(_chart_payload(sub, f"natal:{name}"), ensure_ascii=False)

@mcp.tool
def get_current_transits() -> str:
    """Today's planetary positions (UTC now at Greenwich) — the current sky, for
    transit analysis, daily overviews, and timing work."""
    now = datetime.now(timezone.utc)
    sub = _subject("now", now.year, now.month, now.day, now.hour, now.minute,
                   "Greenwich", "GB", 0.0, 51.4769, "UTC")
    return json.dumps(_chart_payload(sub, "transits:now"), ensure_ascii=False)

@mcp.tool
def get_sign_profile(sign: str) -> str:
    """Reference card for a zodiac sign: element, modality, ruling planet."""
    s = sign.strip().capitalize()
    if s not in SIGNS:
        return json.dumps({"error": f"unknown sign '{sign}'", "valid": SIGNS})
    return json.dumps({"sign": s, "element": ELEMENT[s], "modality": MODALITY[s],
                       "ruler": RULER[s]}, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8033, path="/mcp")
