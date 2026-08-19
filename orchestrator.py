"""
Multi-Agent Orchestrator — AI-Driven Cyclone & Coastal Disaster Early Warning System
Coordinates all five specialist agents and fuses their outputs into a unified
Disaster Response Briefing.
"""

from __future__ import annotations
import concurrent.futures
from typing import Any

from agents import cyclone_prediction, fishermen_alert, evacuation_planning
from agents import resource_coordination, damage_assessment
from watsonx_client import generate


# ---------------------------------------------------------------------------
# Helper: fusion summary
# ---------------------------------------------------------------------------

FUSION_SYSTEM = """You are the Chief Disaster Management AI Coordinator.
You receive outputs from 5 specialist agents and synthesise them into a
concise Executive Briefing (max 300 words) for the district administration.
Cover: overall threat level, top 3 immediate actions, resource gaps, and ETA to normalcy.
End with an OVERALL STATUS line: (Green / Yellow / Orange / Red)."""


def _fusion_summary(agent_outputs: dict[str, Any]) -> str:
    """Fuse all agent outputs into an executive summary."""
    sections = []
    for name, data in agent_outputs.items():
        content = (
            data.get("prediction")
            or data.get("alert")
            or data.get("plan")
            or data.get("assessment")
            or ""
        )
        sections.append(f"[{name}]\n{content[:600]}")  # cap each section

    combined = "\n\n".join(sections)
    prompt = f"""{FUSION_SYSTEM}

### Agent Summaries
{combined}

### Task
Write the Executive Briefing now.
"""
    return generate(prompt, max_new_tokens=450)


# ---------------------------------------------------------------------------
# Pre-landfall orchestration
# ---------------------------------------------------------------------------

def run_pre_landfall(
    storm_name: str,
    lat: float,
    lon: float,
    sea_surface_temp_c: float,
    central_pressure_hpa: float,
    max_wind_kmh: float,
    hours_to_landfall: float,
    landfall_location: str,
    wave_height_m: float,
    district: str,
    state: str,
    population_at_risk: int,
    inundation_zone_km: float,
    available_shelters: int,
    shelter_capacity: int,
    affected_districts: list[str],
    total_population_affected: int,
    storm_category: int,
    available_ndrf_teams: int,
    nearest_depot_km: float,
    fleet_count: int = 0,
    active_fishing_zones: list[str] | None = None,
) -> dict:
    """
    Run all pre-landfall agents concurrently and return fused briefing.
    Agents run in parallel using a thread pool to minimise wall-clock time.
    """

    def _cyclone():
        return cyclone_prediction.run(
            sea_surface_temp_c=sea_surface_temp_c,
            central_pressure_hpa=central_pressure_hpa,
            max_wind_speed_kmh=max_wind_kmh,
            lat=lat,
            lon=lon,
            storm_name=storm_name,
        )

    def _fishermen():
        return fishermen_alert.run(
            storm_name=storm_name,
            hours_to_landfall=hours_to_landfall,
            landfall_location=landfall_location,
            max_wind_kmh=max_wind_kmh,
            wave_height_m=wave_height_m,
            active_fishing_zones=active_fishing_zones,
            fleet_count=fleet_count,
        )

    def _evacuation():
        return evacuation_planning.run(
            storm_name=storm_name,
            district=district,
            state=state,
            population_at_risk=population_at_risk,
            hours_to_landfall=hours_to_landfall,
            inundation_zone_km=inundation_zone_km,
            available_shelters=available_shelters,
            shelter_capacity=shelter_capacity,
        )

    def _resources():
        return resource_coordination.run(
            storm_name=storm_name,
            affected_districts=affected_districts,
            total_population_affected=total_population_affected,
            storm_category=storm_category,
            hours_to_landfall=hours_to_landfall,
            available_ndrf_teams=available_ndrf_teams,
            nearest_depot_km=nearest_depot_km,
        )

    tasks = {
        "Cyclone Prediction": _cyclone,
        "Fishermen Alert": _fishermen,
        "Evacuation Plan": _evacuation,
        "Resource Coordination": _resources,
    }

    agent_outputs: dict[str, Any] = {}
    errors: dict[str, str] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fn): name for name, fn in tasks.items()}
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                agent_outputs[name] = future.result()
            except Exception as exc:
                errors[name] = str(exc)

    executive_summary = ""
    if agent_outputs:
        try:
            executive_summary = _fusion_summary(agent_outputs)
        except Exception as exc:
            executive_summary = f"[Fusion error: {exc}]"

    return {
        "phase": "pre_landfall",
        "storm_name": storm_name,
        "agent_outputs": agent_outputs,
        "errors": errors,
        "executive_summary": executive_summary,
    }


# ---------------------------------------------------------------------------
# Post-landfall orchestration
# ---------------------------------------------------------------------------

def run_post_landfall(
    storm_name: str,
    landfall_location: str,
    storm_category: int,
    hours_since_landfall: float,
    reported_casualties: int,
    houses_damaged: int,
    roads_blocked_km: float,
    power_outage_villages: int,
    crop_loss_hectares: float,
    boats_damaged: int,
    # Resource replenishment
    affected_districts: list[str],
    total_population_affected: int,
    available_ndrf_teams: int,
    nearest_depot_km: float = 0.0,
    additional_context: str = "",
) -> dict:
    """
    Run post-landfall agents (Damage Assessment + Resource Coordination) and fuse.
    """

    def _damage():
        return damage_assessment.run(
            storm_name=storm_name,
            landfall_location=landfall_location,
            storm_category=storm_category,
            hours_since_landfall=hours_since_landfall,
            reported_casualties=reported_casualties,
            houses_damaged=houses_damaged,
            roads_blocked_km=roads_blocked_km,
            power_outage_villages=power_outage_villages,
            crop_loss_hectares=crop_loss_hectares,
            boats_damaged=boats_damaged,
            additional_context=additional_context,
        )

    def _resources():
        return resource_coordination.run(
            storm_name=storm_name,
            affected_districts=affected_districts,
            total_population_affected=total_population_affected,
            storm_category=storm_category,
            hours_to_landfall=0,
            available_ndrf_teams=available_ndrf_teams,
            nearest_depot_km=nearest_depot_km,
            additional_context=f"Post-landfall recovery phase. {additional_context}",
        )

    agent_outputs: dict[str, Any] = {}
    errors: dict[str, str] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            pool.submit(_damage): "Damage Assessment",
            pool.submit(_resources): "Resource Coordination",
        }
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                agent_outputs[name] = future.result()
            except Exception as exc:
                errors[name] = str(exc)

    executive_summary = ""
    if agent_outputs:
        try:
            executive_summary = _fusion_summary(agent_outputs)
        except Exception as exc:
            executive_summary = f"[Fusion error: {exc}]"

    return {
        "phase": "post_landfall",
        "storm_name": storm_name,
        "agent_outputs": agent_outputs,
        "errors": errors,
        "executive_summary": executive_summary,
    }
