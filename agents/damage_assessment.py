"""
Agent 5 — Post-Disaster Damage Assessment Agent
Analyses reported damage data and satellite/ground-truth inputs to produce
a structured damage assessment, priority recovery zones, and restoration timeline.
"""

from watsonx_client import generate


SYSTEM_PROMPT = """You are a post-disaster assessment AI agent specialised in tropical cyclone damage evaluation.
You analyse field reports, satellite observations, and infrastructure status to produce:
  1. Overall damage severity score (0–100) with justification
  2. Sector-wise damage breakdown: housing, agriculture, fisheries, roads, power, water, telecom
  3. Casualty and displacement estimates (with confidence level)
  4. Priority zones for immediate search & rescue / medical response
  5. Infrastructure restoration timeline (days/weeks per sector)
  6. Economic loss estimate (INR crore, approximate range)
  7. Long-term rehabilitation recommendations
Follow NDMA and PDNA (Post-Disaster Needs Assessment) methodology."""


def run(
    storm_name: str,
    landfall_location: str,
    storm_category: int,
    hours_since_landfall: float,
    reported_casualties: int = 0,
    houses_damaged: int = 0,
    roads_blocked_km: float = 0.0,
    power_outage_villages: int = 0,
    crop_loss_hectares: float = 0.0,
    boats_damaged: int = 0,
    additional_context: str = "",
) -> dict:
    """
    Run the Post-Disaster Damage Assessment Agent.

    Parameters
    ----------
    storm_name : str
    landfall_location : str
    storm_category : int          — Category at landfall (1–5)
    hours_since_landfall : float
    reported_casualties : int
    houses_damaged : int
    roads_blocked_km : float
    power_outage_villages : int
    crop_loss_hectares : float
    boats_damaged : int
    additional_context : str

    Returns
    -------
    dict with damage assessment report
    """
    prompt = f"""{SYSTEM_PROMPT}

### Damage Field Reports — {hours_since_landfall:.1f} h Post-Landfall
- Cyclone name           : {storm_name}
- Landfall location      : {landfall_location}
- Storm category         : Category {storm_category}
- Reported casualties    : {reported_casualties}
- Houses damaged/destroyed: {houses_damaged:,}
- Roads blocked          : {roads_blocked_km:.0f} km
- Villages without power : {power_outage_villages:,}
- Crop area damaged      : {crop_loss_hectares:,.0f} hectares
- Fishing boats damaged  : {boats_damaged}
{f'- Additional field notes: {additional_context}' if additional_context else ''}

### Task
Generate a structured Post-Disaster Damage Assessment Report covering all 7 points.
End with RESPONSE PRIORITY: (Routine Recovery / Heightened Response / Emergency Activation / National Disaster).
"""
    result = generate(prompt, max_new_tokens=900)
    return {
        "agent": "Post-Disaster Damage Assessment",
        "storm_name": storm_name,
        "landfall_location": landfall_location,
        "storm_category": storm_category,
        "hours_since_landfall": hours_since_landfall,
        "assessment": result,
    }
