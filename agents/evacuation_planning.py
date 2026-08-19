"""
Agent 3 — Evacuation Route Planning Agent
Generates optimised evacuation plans for coastal districts including
primary/alternate routes, shelter locations, special-needs logistics,
and phased timeline based on storm track.
"""

from watsonx_client import generate


SYSTEM_PROMPT = """You are an emergency management AI agent specialised in coastal evacuation planning.
Given storm data and district demographics, you produce a detailed evacuation plan covering:
  1. Phased evacuation timeline (Phase 1 / Phase 2 / Phase 3 with trigger conditions)
  2. Primary evacuation routes with road names / NH numbers and destinations
  3. Alternate routes in case primary routes are flooded or congested
  4. Designated cyclone shelters with capacity and GPS coordinates (approximate)
  5. Special-needs population logistics (elderly, disabled, hospitals, livestock)
  6. Traffic management checkpoints and law enforcement deployment points
  7. Estimated total vehicles and bus requirements
Produce a structured, actionable plan that district collectors can implement immediately."""


def run(
    storm_name: str,
    district: str,
    state: str,
    population_at_risk: int,
    hours_to_landfall: float,
    inundation_zone_km: float,
    available_shelters: int = 0,
    shelter_capacity: int = 0,
    additional_context: str = "",
) -> dict:
    """
    Run the Evacuation Route Planning Agent.

    Parameters
    ----------
    storm_name : str
    district : str              — Affected district name
    state : str                 — State name
    population_at_risk : int    — Estimated people in coastal inundation zone
    hours_to_landfall : float
    inundation_zone_km : float  — Width of expected storm-surge inundation belt (km)
    available_shelters : int    — Number of pre-identified cyclone shelters
    shelter_capacity : int      — Total shelter capacity
    additional_context : str

    Returns
    -------
    dict with evacuation plan and metadata
    """
    prompt = f"""{SYSTEM_PROMPT}

### District & Storm Data
- Cyclone name         : {storm_name}
- District             : {district}, {state}
- Population at risk   : {population_at_risk:,}
- Hours to landfall    : {hours_to_landfall:.1f} h
- Inundation belt width: {inundation_zone_km} km from coast
- Available shelters   : {available_shelters}
- Shelter capacity     : {shelter_capacity:,}
{f'- Notes: {additional_context}' if additional_context else ''}

### Task
Generate a complete, phased Evacuation Route Plan covering all 7 points above.
Include a READINESS STATUS at the end: (Adequate / Stretched / Critical).
"""
    result = generate(prompt, max_new_tokens=800)
    return {
        "agent": "Evacuation Route Planning",
        "storm_name": storm_name,
        "district": district,
        "state": state,
        "population_at_risk": population_at_risk,
        "hours_to_landfall": hours_to_landfall,
        "plan": result,
    }
