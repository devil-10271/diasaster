"""
Agent 2 — Fishermen Safety Alert Agent
Generates targeted alerts for fishing communities based on storm data,
active fishing zones, boat types, and current fleet positions.
"""

from watsonx_client import generate


SYSTEM_PROMPT = """You are a coastal safety AI agent responsible for protecting fishing communities
during cyclones and severe weather. You generate actionable, life-saving alerts in plain language.
Your alerts must cover:
  1. Immediate action required (return to harbour / do not venture out)
  2. Estimated safe return window (hours before landfall)
  3. Dangerous zones / areas to avoid (coordinates or named fishing grounds)
  4. Shelter-in-place instructions if unable to return
  5. Emergency contact numbers and VHF radio channels
  6. Translated advisory summary (include Hindi or regional language note)
Be direct, urgent, and use simple language fishermen can act on immediately."""


def run(
    storm_name: str,
    hours_to_landfall: float,
    landfall_location: str,
    max_wind_kmh: float,
    wave_height_m: float,
    active_fishing_zones: list[str] | None = None,
    fleet_count: int = 0,
    additional_context: str = "",
) -> dict:
    """
    Run the Fishermen Safety Alert Agent.

    Parameters
    ----------
    storm_name : str
    hours_to_landfall : float   — Time in hours until expected landfall
    landfall_location : str     — Expected landfall location name
    max_wind_kmh : float        — Maximum sustained wind speed km/h
    wave_height_m : float       — Expected wave height in metres
    active_fishing_zones : list — Named fishing grounds currently occupied
    fleet_count : int           — Estimated number of boats at sea
    additional_context : str    — Extra details (boat types, radio coverage, etc.)

    Returns
    -------
    dict with alert content and metadata
    """
    zones_str = (
        ", ".join(active_fishing_zones)
        if active_fishing_zones
        else "open coastal waters"
    )

    prompt = f"""{SYSTEM_PROMPT}

### Storm & Fleet Data
- Cyclone name         : {storm_name}
- Hours to landfall    : {hours_to_landfall:.1f} h
- Landfall location    : {landfall_location}
- Max wind speed       : {max_wind_kmh} km/h
- Expected wave height : {wave_height_m} m
- Active fishing zones : {zones_str}
- Estimated boats at sea: {fleet_count}
{f'- Notes: {additional_context}' if additional_context else ''}

### Task
Generate a complete Fishermen Safety Alert covering all 6 points. Start with a bold WARNING header.
End with ALERT SEVERITY: (Advisory / Watch / Warning / Emergency).
"""
    result = generate(prompt, max_new_tokens=700)
    return {
        "agent": "Fishermen Safety Alert",
        "storm_name": storm_name,
        "hours_to_landfall": hours_to_landfall,
        "landfall_location": landfall_location,
        "fleet_count": fleet_count,
        "alert": result,
    }
