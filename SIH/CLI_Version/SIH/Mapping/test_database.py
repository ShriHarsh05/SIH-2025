#!/usr/bin/env python3
"""
Test script for database integration
"""

import json
from database import MappingDatabase, log_mapping_session
from datetime import datetime

def test_database():
    """Test database functionality"""
    
    print("=" * 70)
    print("DATABASE INTEGRATION TEST")
    print("=" * 70)
    
    # Test data
    test_data = {
        "practitioner_id": "test-practitioner-001",
        "encounter_id": "test-encounter-001",
        "patient_id": "test-patient-001",
        "selected_system": "ayurveda",
        "query": "joint pain and stiffness",
        "tm_candidates": [
            {
                "code": "SP42",
                "term": "pRuShTha-grahaH",
                "english": "Lumbar spondylosis disorder",
                "definition": "It is characterised by backache of various degrees.",
                "score": 0.8542
            },
            {
                "code": "SP43",
                "term": "test-term",
                "english": "Test disorder",
                "definition": "Test definition",
                "score": 0.7234
            }
        ],
        "icd11_standard_candidates": [
            {
                "code": "FA20.0",
                "title": "Low back pain",
                "definition": "Pain localized to the lower back region.",
                "score": 0.7823
            }
        ],
        "icd11_tm2_candidates": [
            {
                "code": "SP42",
                "title": "Lumbar spondylosis disorder (TM2)",
                "definition": "It is characterised by backache.",
                "score": 0.8123
            }
        ],
        "selected_tm_candidate": {
            "code": "SP42",
            "term": "pRuShTha-grahaH",
            "english": "Lumbar spondylosis disorder",
            "definition": "It is characterised by backache of various degrees.",
            "score": 0.8542
        },
        "selected_icd11_standard": {
            "code": "FA20.0",
            "title": "Low back pain",
            "definition": "Pain localized to the lower back region.",
            "score": 0.7823
        },
        "selected_icd11_tm2": {
            "code": "SP42",
            "title": "Lumbar spondylosis disorder (TM2)",
            "definition": "It is characterised by backache.",
            "score": 0.8123
        },
        "fhir_json": {
            "resourceType": "Condition",
            "id": "test-condition-001",
            "code": {
                "coding": [
                    {
                        "system": "http://who.int/icd/tm2/ayurveda",
                        "code": "SP42",
                        "display": "Lumbar spondylosis disorder"
                    }
                ]
            }
        }
    }
    
    # Test 1: Log a mapping session
    print("\n[TEST 1] Logging mapping session...")
    try:
        record_id = log_mapping_session(**test_data)
        print(f"✓ Session logged successfully (Record ID: {record_id})")
    except Exception as e:
        print(f"✗ Failed to log session: {e}")
        return
    
    # Test 2: Retrieve the record
    print("\n[TEST 2] Retrieving record by ID...")
    try:
        with MappingDatabase() as db:
            record = db.get_record_by_id(record_id)
            if record:
                print(f"✓ Record retrieved successfully")
                print(f"  - Timestamp: {record['timestamp']}")
                print(f"  - Practitioner: {record['practitioner_id']}")
                print(f"  - System: {record['selected_system']}")
                print(f"  - Query: {record['query']}")
                print(f"  - TM Code: {record['selected_tm_code']} (Rank: #{record['selected_tm_rank']})")
                print(f"  - ICD-11 Std: {record['selected_icd11_standard_code']} (Rank: #{record['selected_icd11_standard_rank']})")
                print(f"  - ICD-11 TM2: {record['selected_icd11_tm2_code']} (Rank: #{record['selected_icd11_tm2_rank']})")
            else:
                print(f"✗ Record not found")
    except Exception as e:
        print(f"✗ Failed to retrieve record: {e}")
    
    # Test 3: Get statistics
    print("\n[TEST 3] Getting database statistics...")
    try:
        with MappingDatabase() as db:
            stats = db.get_statistics()
            print(f"✓ Statistics retrieved successfully")
            print(f"  - Total records: {stats['total_records']}")
            print(f"  - Records by system: {stats['by_system']}")
            if stats['average_ranks']['tm']:
                print(f"  - Average TM rank: #{stats['average_ranks']['tm']}")
    except Exception as e:
        print(f"✗ Failed to get statistics: {e}")
    
    # Test 4: Get recent records
    print("\n[TEST 4] Getting recent records...")
    try:
        with MappingDatabase() as db:
            records = db.get_recent_records(limit=5)
            print(f"✓ Retrieved {len(records)} recent records")
            for i, rec in enumerate(records, 1):
                print(f"  {i}. ID={rec['id']}, System={rec['selected_system']}, TM={rec['selected_tm_code']}")
    except Exception as e:
        print(f"✗ Failed to get recent records: {e}")
    
    # Test 5: Get records by practitioner
    print("\n[TEST 5] Getting records by practitioner...")
    try:
        with MappingDatabase() as db:
            records = db.get_records_by_practitioner(test_data['practitioner_id'])
            print(f"✓ Retrieved {len(records)} records for practitioner {test_data['practitioner_id']}")
    except Exception as e:
        print(f"✗ Failed to get records by practitioner: {e}")
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70)
    print("\nDatabase file location: mapping_records.db")
    print("You can now run the CLI app and test the full workflow!")

if __name__ == "__main__":
    test_database()
