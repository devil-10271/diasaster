"""
Agent 1 — Cyclone Track & Intensity Prediction Agent
Analyses meteorological inputs and predicts cyclone trajectory, landfall time,
wind speed category, and storm-surge risk using IBM Granite via Watsonx.ai.
"""

from watsonx_client import generate


SYSTEM_PROMPT = """You are an expert meteorological AI agent specialised in tropical cyclone forecasting.
You analyse sea-surface temperature, atmospheric pressure, wind shear, satellite imagery descriptions,
and historical track data to predict:
  1. Likely 24 h / 48 h / 72 h track (latitude/longitude waypoints)
  2. Intensity category (Saffir–Simpson 1-5 or equivalent IMD scale)
  3. Estimated landfall location and time window
  4. Storm-surge height (metres) at landfall
  5. Key uncertainty factors
Respond concisely with numbered sections. Use metric units."""


def run(
    sea_surface_temp_c: float,
    central_pressure_hpa: float,
    max_wind_speed_kmh: float,
    lat: float,
    lon: float,
    storm_name: str = "unnamed",
    additional_context: str = "",
) -> dict:
    """
    Run the Cyclone Track & Intensity Prediction Agent.

    Parameters
    ----------
    sea_surface_temp_c : float  — Sea-surface temperature in °C
    central_pressure_hpa : float — Central pressure in hPa
    max_wind_speed_kmh : float  — Current maximum sustained wind speed km/h
    lat / lon : float           — Current storm centre coordinates
    storm_name : str            — Storm identifier
    additional_context : str    — Any extra satellite / reanalysis notes

    Returns
    -------
    dict with keys: storm_name, prediction, inputs
    """
    prompt = f"""{SYSTEM_PROMPT}

### Current Cyclone Observations
- Storm name      : {storm_name}
- Position        : {lat:.2f}°N, {lon:.2f}°E
- Sea-surface temp: {sea_surface_temp_c}°C
- Central pressure: {central_pressure_hpa} hPa
- Max wind speed  : {max_wind_speed_kmh} km/h
{f'- Notes: {additional_context}' if additional_context else ''}

### Task
Provide a detailed cyclone track & intensity prediction report covering all 5 points listed above.
End with a one-line RISK LEVEL: (Low / Moderate / High / Extreme).
"""
    result = generate(prompt, max_new_tokens=700)
    return {
        "agent": "Cyclone Track & Intensity Prediction",
        "storm_name": storm_name,
        "inputs": {
            "position": {"lat": lat, "lon": lon},
            "sea_surface_temp_c": sea_surface_temp_c,
            "central_pressure_hpa": central_pressure_hpa,
            "max_wind_speed_kmh": max_wind_speed_kmh,
        },
        "prediction": result,
    }
