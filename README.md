# TianJi Astrology MCP Server

**Computation-first astrology tools for AI agents.** Real ephemeris-grade planetary positions, houses, and aspects — not generic sun-sign content.

Built by [TianJi Astrology](https://tianji-astrology.com) on top of [kerykeion](https://github.com/g-battaglia/kerykeion) 6.x (libephemeris engine). Transport: streamable HTTP (MCP spec).

**Live endpoint:** `https://mcp.tianji-astrology.com/mcp`

## Why this server

Most astrology MCP servers wrap horoscope text. TianJi computes the actual chart:

- Swiss-ephemeris-grade planetary longitudes, retrogrades, and house cusps (via kerykeion/libephemeris)
- Full 12-house placement with cusp houses resolved per planet
- Major aspects (conjunction, sextile, square, trine, opposition) computed with standard orbs
- Deterministic output an agent can reason over — no LLM-generated "readings" in the loop

## Tools

### `compute_natal_chart`
Compute a natal (birth) chart from date, time, and place.

Parameters: `name`, `year`, `month`, `day`, `hour` (default 12), `minute` (default 0), `city`, `nation`, `lng`, `lat`, `tz_str`.

Returns JSON: positions for Sun through Pluto (sign, degree, house, retrograde), Ascendant/MC, house cusps, and the aspect list with exact orbits.

### `get_current_transits`
Today's sky: current planetary positions for all ten bodies, with retrograde flags. No parameters.

### `get_sign_profile`
Reference facts for a zodiac sign: element, modality, ruling planet (traditional + modern), date range. Parameter: `sign` (e.g. `"Scorpio"`).

## Usage

### Remote (hosted)

The server runs publicly at `https://mcp.tianji-astrology.com/mcp` (streamable HTTP transport). Point any MCP client that supports remote servers at that URL — no API key required for the reference tools.

Claude Desktop / Claude Code (`claude mcp add`):

```bash
claude mcp add --transport http tianji https://mcp.tianji-astrology.com/mcp
```

Cursor / other clients: add a server entry with type `http` (or `streamable-http`) and the URL above.

### Self-host

```bash
docker build -t tj-mcp .
docker run -p 8033:8033 tj-mcp
```

Or bare Python:

```bash
pip install fastmcp kerykeion
python server.py
```

## Data & privacy

All computation is local to the server. Birth data is used only to compute the chart and is never stored or logged.

## License

MIT — see [LICENSE](LICENSE).

---

*TianJi Astrology: personalized Western astrology, computed. https://tianji-astrology.com*
