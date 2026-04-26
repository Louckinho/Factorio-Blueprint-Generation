from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union, Any

class OptionsSchema(BaseModel):
    tileable_block: bool = False
    max_machines_per_block: int = Field(default=15, ge=1, le=100)

class TechTierSchema(BaseModel):
    belt: str = "express-transport-belt"
    inserter: str = "fast-inserter"
    machine: str = "assembling-machine-3"
    furnace: str = "electric-furnace"
    pole: str = "medium-electric-pole"
    oil_recipe: str = "advanced-oil-processing"

class ModulesSchema(BaseModel):
    beaconized: bool = False
    beacon_entity: str = "beacon"
    machine_modules: List[str] = Field(default_factory=lambda: ["productivity-module-3"])
    beacon_modules: List[str] = Field(default_factory=lambda: ["speed-module-3"])

class AIContextSchema(BaseModel):
    block_size_limit: Optional[str] = "15x15"
    custom_instructions: Optional[str] = None
    allow_hallucinations: bool = False

class SimpleModeRequest(BaseModel):
    mode: str = Field(default="simple", pattern="^simple$")
    target: str
    rate_per_minute: float = Field(gt=0)
    options: OptionsSchema = Field(default_factory=OptionsSchema)
    tech_tier: TechTierSchema = Field(default_factory=TechTierSchema)
    modules: ModulesSchema = Field(default_factory=ModulesSchema)
    ai_context: AIContextSchema = Field(default_factory=AIContextSchema)

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

class ADAMRequest(BaseModel):
    mode: str = Field(default="adam", pattern="^adam$")
    target: str
    rate_per_minute: float = Field(gt=0)
    options: OptionsSchema = Field(default_factory=OptionsSchema)
    tech_tier: TechTierSchema = Field(default_factory=TechTierSchema)
    modules: ModulesSchema = Field(default_factory=ModulesSchema)
    ai_context: AIContextSchema = Field(default_factory=AIContextSchema)
    prompt: Optional[str] = None # Tornamos opcional, pois o target/rate é o principal

class MachineRequirement(BaseModel):
    item: str
    count: float
    machine_type: str

class ADAMWorkOrderSchema(BaseModel):
    target_item: str
    total_rate_per_minute: float
    requested_machines: List[MachineRequirement]
    tech_tier: TechTierSchema
    context: AIContextSchema

class ADAMResponseSchema(BaseModel):
    raw_dsl: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    translated_entities: List[Dict[str, Any]] = Field(default_factory=list)
    hallucination_log: List[str] = Field(default_factory=list)

BlueprintRequestSchema = Union[SimpleModeRequest, AdvancedModeRequest, ADAMRequest]
