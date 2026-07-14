import pytest

from models.data_models import BatchRecord, ProductionRecord
from repositories.csv_repository import CSVRepository, RepositoryError


def test_load_automotive_records():
    repo = CSVRepository("data/automotive/production.csv", ProductionRecord)
    records = repo.load_records()
    assert len(records) == 8
    assert all(isinstance(r, ProductionRecord) for r in records)
    assert records[0].line_id == "Assembly Line 1"
    assert records[0].units_produced == 120
    assert records[0].oee == 85.2

def test_load_pharma_records():
    repo = CSVRepository("data/pharma/batches.csv", BatchRecord)
    records = repo.load_records()
    assert len(records) == 8
    assert all(isinstance(r, BatchRecord) for r in records)
    assert records[0].batch_id == "BAT-001"
    assert records[0].critical_temp == 37.2
    assert records[0].quality_status == "Pass"

def test_load_missing_csv():
    repo = CSVRepository("data/nonexistent.csv", ProductionRecord)
    with pytest.raises(RepositoryError) as exc_info:
        repo.load_records()
    assert "Failed to read CSV file" in str(exc_info.value)

def test_load_invalid_data_schema(tmp_path):
    # Write CSV missing the required field 'units_produced'
    csv_file = tmp_path / "invalid_data.csv"
    csv_file.write_text("timestamp,line_id,defects,downtime_minutes,oee\n2026-07-12,Line A,2,0.0,88.0\n", encoding="utf-8")
    
    repo = CSVRepository(str(csv_file), ProductionRecord)
    with pytest.raises(RepositoryError) as exc_info:
        repo.load_records()
    assert "Validation failed" in str(exc_info.value)
