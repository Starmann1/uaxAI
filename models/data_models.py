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
