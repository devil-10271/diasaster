"""
Agent 4 — Relief Resource Coordination Agent
Optimises pre-positioning and distribution of relief materials (food, water,
medicine, rescue teams) across affected districts using storm severity data.
"""

from watsonx_client import generate


SYSTEM_PROMPT = """You are a disaster relief logistics AI agent responsible for coordinating
pre-positioning and distribution of emergency resources during cyclone response.
Your output must cover:
  1. Resource requirements breakdown (food packets, water litres, medicine kits, tarpaulins, boats)
  2. Pre-positioning strategy — which depots/warehouses to activate and quantities
  3. Deployment of NDRF/SDRF teams and Coast Guard assets with staging areas
  4. Medical emergency preparedness (hospitals on standby, blood bank, trauma teams)
  5. Communication infrastructure (satellite phones, HAM radio nodes, mobile towers backup)
  6. Coordination with NGOs and private sector (list key roles)
  7. 72-hour post-landfall resource release schedule
Base calculations on standard NDMA India norms where applicable."""


def run(
    storm_name: str,
    affected_districts: list[str],
    total_population_affected: int,
    storm_category: int,
    hours_to_landfall: float,
    available_ndrf_teams: int = 0,
    nearest_depot_km: float = 0.0,
    additional_context: str = "",
) -> dict:
    """
    Run the Relief Resource Coordination Agent.

    Parameters
    ----------
    storm_name : str
    affected_districts : list[str]
    total_population_affected : int
    storm_category : int            — 1–5 (Saffir–Simpson / IMD scale)
    hours_to_landfall : float
    available_ndrf_teams : int
    nearest_depot_km : float        — Distance to nearest strategic reserve depot
    additional_context : str

    Returns
    -------
    dict with resource coordination plan
    """
    districts_str = ", ".join(affected_districts) if affected_districts else "multiple coastal districts"

    prompt = f"""{SYSTEM_PROMPT}

### Operational Parameters
- Cyclone name              : {storm_name}
- Affected districts        : {districts_str}
- Total population affected : {total_population_affected:,}
- Storm category            : Category {storm_category}
- Hours to landfall         : {hours_to_landfall:.1f} h
- Available NDRF teams      : {available_ndrf_teams}
- Nearest strategic depot   : {nearest_depot_km:.0f} km
{f'- Notes: {additional_context}' if additional_context else ''}

### Task
Generate a comprehensive Relief Resource Coordination Plan covering all 7 points.
End with LOGISTICS STATUS: (Adequate / Partially Ready / Under-Resourced).
"""
    result = generate(prompt, max_new_tokens=800)
    return {
        "agent": "Relief Resource Coordination",
        "storm_name": storm_name,
        "affected_districts": affected_districts,
        "total_population_affected": total_population_affected,
        "storm_category": storm_category,
        "plan": result,
    }
