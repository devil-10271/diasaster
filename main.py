"""
FastAPI backend — AI-Driven Cyclone & Coastal Disaster Early Warning System
Exposes REST endpoints for each agent and the full orchestration flows.
"""

from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional
import os

import orchestrator
from agents import (
    cyclone_prediction,
    fishermen_alert,
    evacuation_planning,
    resource_coordination,
    damage_assessment,
)

app = FastAPI(
    title="AI-Driven Cyclone & Coastal Disaster Early Warning System",
    description="Multi-agent IBM Watsonx.ai powered disaster management API",
    version="1.0.0",
)

# Mount static files (frontend)
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ============================================================
# Request Models
# ============================================================

class CyclonePredictionRequest(BaseModel):
    storm_name: str = Field("Cyclone-Alpha", description="Storm identifier")
    lat: float = Field(14.5, description="Current storm centre latitude (°N)")
    lon: float = Field(82.0, description="Current storm centre longitude (°E)")
    sea_surface_temp_c: float = Field(29.5, description="Sea-surface temperature °C")
    central_pressure_hpa: float = Field(960.0, description="Central pressure hPa")
    max_wind_speed_kmh: float = Field(185.0, description="Max sustained wind speed km/h")
    additional_context: Optional[str] = Field("", description="Extra notes")


class FishermenAlertRequest(BaseModel):
    storm_name: str = "Cyclone-Alpha"
    hours_to_landfall: float = Field(36.0, ge=0)
    landfall_location: str = "Visakhapatnam coast, Andhra Pradesh"
    max_wind_kmh: float = 185.0
    wave_height_m: float = 6.5
    active_fishing_zones: Optional[list[str]] = ["Bay of Bengal Zone-3", "Kakinada Bay"]
    fleet_count: int = Field(0, ge=0)
    additional_context: Optional[str] = ""


class EvacuationRequest(BaseModel):
    storm_name: str = "Cyclone-Alpha"
    district: str = "Visakhapatnam"
    state: str = "Andhra Pradesh"
    population_at_risk: int = Field(250000, ge=0)
    hours_to_landfall: float = Field(36.0, ge=0)
    inundation_zone_km: float = Field(5.0, ge=0)
    available_shelters: int = Field(120, ge=0)
    shelter_capacity: int = Field(80000, ge=0)
    additional_context: Optional[str] = ""


class ResourceCoordinationRequest(BaseModel):
    storm_name: str = "Cyclone-Alpha"
    affected_districts: list[str] = ["Visakhapatnam", "Srikakulam", "Vizianagaram"]
    total_population_affected: int = Field(800000, ge=0)
    storm_category: int = Field(4, ge=1, le=5)
    hours_to_landfall: float = Field(36.0, ge=0)
    available_ndrf_teams: int = Field(8, ge=0)
    nearest_depot_km: float = Field(120.0, ge=0)
    additional_context: Optional[str] = ""


class DamageAssessmentRequest(BaseModel):
    storm_name: str = "Cyclone-Alpha"
    landfall_location: str = "Visakhapatnam coast, Andhra Pradesh"
    storm_category: int = Field(4, ge=1, le=5)
    hours_since_landfall: float = Field(12.0, ge=0)
    reported_casualties: int = Field(0, ge=0)
    houses_damaged: int = Field(15000, ge=0)
    roads_blocked_km: float = Field(340.0, ge=0)
    power_outage_villages: int = Field(2200, ge=0)
    crop_loss_hectares: float = Field(45000.0, ge=0)
    boats_damaged: int = Field(320, ge=0)
    additional_context: Optional[str] = ""


class PreLandfallRequest(BaseModel):
    storm_name: str = "Cyclone-Alpha"
    lat: float = 14.5
    lon: float = 82.0
    sea_surface_temp_c: float = 29.5
    central_pressure_hpa: float = 960.0
    max_wind_kmh: float = 185.0
    hours_to_landfall: float = 36.0
    landfall_location: str = "Visakhapatnam coast, Andhra Pradesh"
    wave_height_m: float = 6.5
    district: str = "Visakhapatnam"
    state: str = "Andhra Pradesh"
    population_at_risk: int = 250000
    inundation_zone_km: float = 5.0
    available_shelters: int = 120
    shelter_capacity: int = 80000
    affected_districts: list[str] = ["Visakhapatnam", "Srikakulam", "Vizianagaram"]
    total_population_affected: int = 800000
    storm_category: int = Field(4, ge=1, le=5)
    available_ndrf_teams: int = 8
    nearest_depot_km: float = 120.0
    fleet_count: int = 250
    active_fishing_zones: Optional[list[str]] = ["Bay of Bengal Zone-3", "Kakinada Bay"]


class PostLandfallRequest(BaseModel):
    storm_name: str = "Cyclone-Alpha"
    landfall_location: str = "Visakhapatnam coast, Andhra Pradesh"
    storm_category: int = Field(4, ge=1, le=5)
    hours_since_landfall: float = 12.0
    reported_casualties: int = 0
    houses_damaged: int = 15000
    roads_blocked_km: float = 340.0
    power_outage_villages: int = 2200
    crop_loss_hectares: float = 45000.0
    boats_damaged: int = 320
    affected_districts: list[str] = ["Visakhapatnam", "Srikakulam", "Vizianagaram"]
    total_population_affected: int = 800000
    available_ndrf_teams: int = 8
    nearest_depot_km: float = 120.0
    additional_context: Optional[str] = ""


# ============================================================
# Individual Agent Endpoints
# ============================================================

@app.post("/agents/cyclone-prediction", tags=["Agents"])
def api_cyclone_prediction(req: CyclonePredictionRequest):
    """Agent 1 — Cyclone Track & Intensity Prediction"""
    try:
        return cyclone_prediction.run(
            sea_surface_temp_c=req.sea_surface_temp_c,
            central_pressure_hpa=req.central_pressure_hpa,
            max_wind_speed_kmh=req.max_wind_speed_kmh,
            lat=req.lat,
            lon=req.lon,
            storm_name=req.storm_name,
            additional_context=req.additional_context or "",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/agents/fishermen-alert", tags=["Agents"])
def api_fishermen_alert(req: FishermenAlertRequest):
    """Agent 2 — Fishermen Safety Alert"""
    try:
        return fishermen_alert.run(
            storm_name=req.storm_name,
            hours_to_landfall=req.hours_to_landfall,
            landfall_location=req.landfall_location,
            max_wind_kmh=req.max_wind_kmh,
            wave_height_m=req.wave_height_m,
            active_fishing_zones=req.active_fishing_zones,
            fleet_count=req.fleet_count,
            additional_context=req.additional_context or "",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/agents/evacuation-plan", tags=["Agents"])
def api_evacuation_plan(req: EvacuationRequest):
    """Agent 3 — Evacuation Route Planning"""
    try:
        return evacuation_planning.run(
            storm_name=req.storm_name,
            district=req.district,
            state=req.state,
            population_at_risk=req.population_at_risk,
            hours_to_landfall=req.hours_to_landfall,
            inundation_zone_km=req.inundation_zone_km,
            available_shelters=req.available_shelters,
            shelter_capacity=req.shelter_capacity,
            additional_context=req.additional_context or "",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/agents/resource-coordination", tags=["Agents"])
def api_resource_coordination(req: ResourceCoordinationRequest):
    """Agent 4 — Relief Resource Coordination"""
    try:
        return resource_coordination.run(
            storm_name=req.storm_name,
            affected_districts=req.affected_districts,
            total_population_affected=req.total_population_affected,
            storm_category=req.storm_category,
            hours_to_landfall=req.hours_to_landfall,
            available_ndrf_teams=req.available_ndrf_teams,
            nearest_depot_km=req.nearest_depot_km,
            additional_context=req.additional_context or "",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/agents/damage-assessment", tags=["Agents"])
def api_damage_assessment(req: DamageAssessmentRequest):
    """Agent 5 — Post-Disaster Damage Assessment"""
    try:
        return damage_assessment.run(
            storm_name=req.storm_name,
            landfall_location=req.landfall_location,
            storm_category=req.storm_category,
            hours_since_landfall=req.hours_since_landfall,
            reported_casualties=req.reported_casualties,
            houses_damaged=req.houses_damaged,
            roads_blocked_km=req.roads_blocked_km,
            power_outage_villages=req.power_outage_villages,
            crop_loss_hectares=req.crop_loss_hectares,
            boats_damaged=req.boats_damaged,
            additional_context=req.additional_context or "",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ============================================================
# Orchestration Endpoints
# ============================================================

@app.post("/orchestrate/pre-landfall", tags=["Orchestrator"])
def api_pre_landfall(req: PreLandfallRequest):
    """
    Run all pre-landfall agents in parallel and return fused Executive Briefing.
    Calls: Cyclone Prediction + Fishermen Alert + Evacuation Plan + Resource Coordination
    """
    try:
        return orchestrator.run_pre_landfall(
            storm_name=req.storm_name,
            lat=req.lat,
            lon=req.lon,
            sea_surface_temp_c=req.sea_surface_temp_c,
            central_pressure_hpa=req.central_pressure_hpa,
            max_wind_kmh=req.max_wind_kmh,
            hours_to_landfall=req.hours_to_landfall,
            landfall_location=req.landfall_location,
            wave_height_m=req.wave_height_m,
            district=req.district,
            state=req.state,
            population_at_risk=req.population_at_risk,
            inundation_zone_km=req.inundation_zone_km,
            available_shelters=req.available_shelters,
            shelter_capacity=req.shelter_capacity,
            affected_districts=req.affected_districts,
            total_population_affected=req.total_population_affected,
            storm_category=req.storm_category,
            available_ndrf_teams=req.available_ndrf_teams,
            nearest_depot_km=req.nearest_depot_km,
            fleet_count=req.fleet_count,
            active_fishing_zones=req.active_fishing_zones,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/orchestrate/post-landfall", tags=["Orchestrator"])
def api_post_landfall(req: PostLandfallRequest):
    """
    Run post-landfall agents: Damage Assessment + Resource Coordination → fused briefing.
    """
    try:
        return orchestrator.run_post_landfall(
            storm_name=req.storm_name,
            landfall_location=req.landfall_location,
            storm_category=req.storm_category,
            hours_since_landfall=req.hours_since_landfall,
            reported_casualties=req.reported_casualties,
            houses_damaged=req.houses_damaged,
            roads_blocked_km=req.roads_blocked_km,
            power_outage_villages=req.power_outage_villages,
            crop_loss_hectares=req.crop_loss_hectares,
            boats_damaged=req.boats_damaged,
            affected_districts=req.affected_districts,
            total_population_affected=req.total_population_affected,
            available_ndrf_teams=req.available_ndrf_teams,
            nearest_depot_km=req.nearest_depot_km,
            additional_context=req.additional_context or "",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ============================================================
# Health check
# ============================================================

@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "system": "AI-Driven Cyclone & Coastal Disaster Early Warning System"}


# ============================================================
# Serve frontend
# ============================================================

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
