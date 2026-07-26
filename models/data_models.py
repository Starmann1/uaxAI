from typing import Optional
from pydantic import BaseModel, Field


class ProductionRecord(BaseModel):
    timestamp: str = Field(..., description="Timestamp of the reading")
    line_id: str = Field(..., description="Assembly line identifier")
    units_produced: int = Field(..., description="Number of units produced in this interval")
    defects: int = Field(..., description="Number of defective units found")
    downtime_minutes: float = Field(..., description="Downtime in minutes during this interval")
    oee: float = Field(..., description="Overall Equipment Effectiveness percentage")


class BatchRecord(BaseModel):
    timestamp: str = Field(..., description="Timestamp of the batch reading")
    batch_id: str = Field(..., description="Batch identifier")
    reactor_id: str = Field(..., description="Bioreactor identifier")
    critical_temp: float = Field(..., description="Measured critical temperature in Celsius")
    critical_ph: float = Field(..., description="Measured critical pH level")
    batch_yield_pct: float = Field(..., description="Batch yield percentage")
    quality_status: str = Field(..., description="Quality control status (e.g. Pass, Fail)")


class SupplierRecord(BaseModel):
    supplier_id: int = Field(..., description="Unique supplier identifier")
    supplier_name: str = Field(..., description="Name of the supplier company")
    contact_person: str = Field(..., description="Contact name")
    address: str = Field(..., description="Address details")
    email: str = Field(..., description="Email address")
    phone_number: str = Field(..., description="Phone number")
    supplier_status: str = Field(..., description="Supplier status (e.g. APPROVED, SUSPENDED)")


class MaterialRecord(BaseModel):
    material_code: str = Field(..., description="Unique material code")
    brand_name: str = Field(..., description="Brand name of the material")
    generic_name: str = Field(..., description="Generic pharmaceutical name")
    manufacturer: str = Field(..., description="Manufacturer name")
    formulation: str = Field(..., description="Formulation form")
    strength: Optional[str] = Field(None, description="Strength of the active ingredient")
    schedule_category: str = Field(..., description="Schedule category")
    storage_conditions: str = Field(..., description="Storage condition details")
    reorder_level: int = Field(..., description="Reorder stock level")
    is_active: bool = Field(..., description="Whether material is active")
    preferred_supplier_id: Optional[int] = Field(None, description="Preferred supplier id")
    material_type: str = Field(..., description="Material type (RAW_MATERIAL, PACKAGING, FINISHED_GOOD)")
    unit_of_measure: str = Field(..., description="Unit of measure (e.g. KG, UNITS, BOXES)")


class LocationRecord(BaseModel):
    location_code: str = Field(..., description="Unique location code")
    location_name: str = Field(..., description="Name of the location")
    description: str = Field(..., description="Description of the location")
    capacity: int = Field(..., description="Capacity of the location")


class DeviationRecord(BaseModel):
    id: int = Field(..., description="Unique deviation ID")
    batch_number: str = Field(..., description="Batch number associated with deviation")
    description: str = Field(..., description="Text description of deviation")
    criticality: str = Field(..., description="Criticality rating (MINOR, MAJOR, CRITICAL)")
    status: str = Field(..., description="Deviation workflow status (OPEN, INVESTIGATING, CLOSED)")


class CapaRecord(BaseModel):
    id: int = Field(..., description="Unique CAPA ID")
    deviation_id: int = Field(..., description="Deviation ID associated with CAPA")
    action_plan: str = Field(..., description="Text description of the action plan")
    due_date: str = Field(..., description="Due date for completion")
    status: str = Field(..., description="CAPA status (OPEN, IMPLEMENTED, VERIFIED)")
