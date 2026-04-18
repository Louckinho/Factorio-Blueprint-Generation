from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union

class OptionsSchema(BaseModel):
    tileable_block: bool = False
    max_machines_per_block: int = Field(default=15, ge=1, le=100)

class TechTierSchema(BaseModel):
    belt: str = "express-transport-belt"
    inserter: str = "fast-inserter"
    machine: str = "assembling-machine-3"
    oil_recipe: str = "advanced-oil-processing"

class ModulesSchema(BaseModel):
    beaconized: bool = False
    beacon_entity: str = "beacon"
    machine_modules: List[str] = Field(default_factory=lambda: ["productivity-module-3"])
    beacon_modules: List[str] = Field(default_factory=lambda: ["speed-module-3"])

class SimpleModeRequest(BaseModel):
    mode: str = Field(default="simple", pattern="^simple$")
    target: str
    rate_per_minute: float = Field(gt=0)
    options: OptionsSchema = Field(default_factory=OptionsSchema)
    tech_tier: TechTierSchema = Field(default_factory=TechTierSchema)
    modules: ModulesSchema = Field(default_factory=ModulesSchema)

class AdvancedNodeSchema(BaseModel):
    item: str
    amount: float
    type: str = "machine"
    recipe: Optional[str] = None

class AdvancedModeRequest(BaseModel):
    mode: str = Field(default="advanced", pattern="^advanced$")
    nodes: List[AdvancedNodeSchema]
    outputs_to: str
    tech_tier: TechTierSchema = Field(default_factory=TechTierSchema)
    modules: ModulesSchema = Field(default_factory=ModulesSchema)

BlueprintRequestSchema = Union[SimpleModeRequest, AdvancedModeRequest]
