"""
SQLite Database Module for Tracking Practitioner Selections
Records all searches, system outputs, and practitioner selections
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class MappingDatabase:
    """Database for tracking TM-ICD mapping sessions"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        if db_path is None:
            db_path = Path(__file__).parent / "mapping_records.db"
        
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        
        # Main mapping records table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mapping_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                practitioner_id TEXT NOT NULL,
                encounter_id TEXT,
                patient_id TEXT,
                selected_system TEXT NOT NULL,
                query TEXT NOT NULL,
                
                -- System outputs (Top 10 lists as JSON)
                tm_system_output TEXT,
                icd11_standard_output TEXT,
                icd11_tm2_output TEXT,
                
                -- Practitioner selections with ranks
                selected_tm_code TEXT,
                selected_tm_rank INTEGER,
                selected_tm_details TEXT,
                
                selected_icd11_standard_code TEXT,
                selected_icd11_standard_rank INTEGER,
                selected_icd11_standard_details TEXT,
                
                selected_icd11_tm2_code TEXT,
                selected_icd11_tm2_rank INTEGER,
                selected_icd11_tm2_details TEXT,
                
                -- FHIR output
                fhir_json TEXT
            )
        ''')
        
        # Index for faster queries
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_practitioner 
            ON mapping_records(practitioner_id)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON mapping_records(timestamp)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_system 
            ON mapping_records(selected_system)
        ''')
        
        self.conn.commit()
    
    def insert_mapping_record(
        self,
        practitioner_id: str,
        encounter_id: str,
        patient_id: str,
        selected_system: str,
        query: str,
        tm_candidates: List[Dict],
        icd11_standard_candidates: List[Dict],
        icd11_tm2_candidates: List[Dict],
        selected_tm_candidate: Dict,
        selected_icd11_standard: Optional[Dict],
        selected_icd11_tm2: Optional[Dict],
        fhir_json: Dict
    ) -> int:
        """
        Insert a new mapping record
        
        Returns:
            Record ID
        """
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Find ranks (position in top 10)
        tm_rank = self._find_rank(selected_tm_candidate, tm_candidates)
        icd11_standard_rank = self._find_rank(selected_icd11_standard, icd11_standard_candidates) if selected_icd11_standard else None
        icd11_tm2_rank = self._find_rank(selected_icd11_tm2, icd11_tm2_candidates) if selected_icd11_tm2 else None
        
        # Prepare system outputs (top 10 as JSON)
        tm_output = json.dumps(tm_candidates[:10], ensure_ascii=False)
        icd11_standard_output = json.dumps(icd11_standard_candidates[:10], ensure_ascii=False)
        icd11_tm2_output = json.dumps(icd11_tm2_candidates[:10], ensure_ascii=False)
        
        # Prepare selection details
        tm_details = json.dumps({
            'code': selected_tm_candidate.get('code'),
            'term': selected_tm_candidate.get('term'),
            'english': selected_tm_candidate.get('english'),
            'definition': selected_tm_candidate.get('definition'),
            'score': selected_tm_candidate.get('score')
        }, ensure_ascii=False)
        
        icd11_standard_details = None
        if selected_icd11_standard:
            icd11_standard_details = json.dumps({
                'code': selected_icd11_standard.get('code'),
                'title': selected_icd11_standard.get('title'),
                'definition': selected_icd11_standard.get('definition'),
                'score': selected_icd11_standard.get('score')
            }, ensure_ascii=False)
        
        icd11_tm2_details = None
        if selected_icd11_tm2:
            icd11_tm2_details = json.dumps({
                'code': selected_icd11_tm2.get('code'),
                'title': selected_icd11_tm2.get('title'),
                'definition': selected_icd11_tm2.get('definition'),
                'score': selected_icd11_tm2.get('score')
            }, ensure_ascii=False)
        
        # FHIR JSON
        fhir_json_str = json.dumps(fhir_json, ensure_ascii=False)
        
        # Insert record
        self.cursor.execute('''
            INSERT INTO mapping_records (
                timestamp, practitioner_id, encounter_id, patient_id,
                selected_system, query,
                tm_system_output, icd11_standard_output, icd11_tm2_output,
                selected_tm_code, selected_tm_rank, selected_tm_details,
                selected_icd11_standard_code, selected_icd11_standard_rank, selected_icd11_standard_details,
                selected_icd11_tm2_code, selected_icd11_tm2_rank, selected_icd11_tm2_details,
                fhir_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp, practitioner_id, encounter_id, patient_id,
            selected_system, query,
            tm_output, icd11_standard_output, icd11_tm2_output,
            selected_tm_candidate.get('code'), tm_rank, tm_details,
            selected_icd11_standard.get('code') if selected_icd11_standard else None,
            icd11_standard_rank, icd11_standard_details,
            selected_icd11_tm2.get('code') if selected_icd11_tm2 else None,
            icd11_tm2_rank, icd11_tm2_details,
            fhir_json_str
        ))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def _find_rank(self, selected_item: Optional[Dict], candidates: List[Dict]) -> Optional[int]:
        """Find the rank (position) of selected item in candidates list"""
        if not selected_item or not candidates:
            return None
        
        selected_code = selected_item.get('code')
        for i, candidate in enumerate(candidates[:10], 1):  # Top 10 only
            if candidate.get('code') == selected_code:
                return i
        
        return None  # Not in top 10
    
    def get_record_by_id(self, record_id: int) -> Optional[Dict]:
        """Get a specific record by ID"""
        self.cursor.execute('''
            SELECT * FROM mapping_records WHERE id = ?
        ''', (record_id,))
        
        row = self.cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        return None
    
    def get_records_by_practitioner(self, practitioner_id: str, limit: int = 100) -> List[Dict]:
        """Get records for a specific practitioner"""
        self.cursor.execute('''
            SELECT * FROM mapping_records 
            WHERE practitioner_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (practitioner_id, limit))
        
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
    
    def get_records_by_system(self, system: str, limit: int = 100) -> List[Dict]:
        """Get records for a specific TM system"""
        self.cursor.execute('''
            SELECT * FROM mapping_records 
            WHERE selected_system = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (system, limit))
        
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
    
    def get_recent_records(self, limit: int = 100) -> List[Dict]:
        """Get most recent records"""
        self.cursor.execute('''
            SELECT * FROM mapping_records 
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        stats = {}
        
        # Total records
        self.cursor.execute('SELECT COUNT(*) FROM mapping_records')
        stats['total_records'] = self.cursor.fetchone()[0]
        
        # Records by system
        self.cursor.execute('''
            SELECT selected_system, COUNT(*) 
            FROM mapping_records 
            GROUP BY selected_system
        ''')
        stats['by_system'] = dict(self.cursor.fetchall())
        
        # Records by practitioner
        self.cursor.execute('''
            SELECT practitioner_id, COUNT(*) 
            FROM mapping_records 
            GROUP BY practitioner_id
            ORDER BY COUNT(*) DESC
            LIMIT 10
        ''')
        stats['top_practitioners'] = dict(self.cursor.fetchall())
        
        # Most common TM codes
        self.cursor.execute('''
            SELECT selected_tm_code, COUNT(*) 
            FROM mapping_records 
            WHERE selected_tm_code IS NOT NULL
            GROUP BY selected_tm_code
            ORDER BY COUNT(*) DESC
            LIMIT 10
        ''')
        stats['top_tm_codes'] = dict(self.cursor.fetchall())
        
        # Most common ICD-11 Standard codes
        self.cursor.execute('''
            SELECT selected_icd11_standard_code, COUNT(*) 
            FROM mapping_records 
            WHERE selected_icd11_standard_code IS NOT NULL
            GROUP BY selected_icd11_standard_code
            ORDER BY COUNT(*) DESC
            LIMIT 10
        ''')
        stats['top_icd11_standard_codes'] = dict(self.cursor.fetchall())
        
        # Average ranks
        self.cursor.execute('''
            SELECT 
                AVG(selected_tm_rank) as avg_tm_rank,
                AVG(selected_icd11_standard_rank) as avg_icd11_standard_rank,
                AVG(selected_icd11_tm2_rank) as avg_icd11_tm2_rank
            FROM mapping_records
        ''')
        row = self.cursor.fetchone()
        stats['average_ranks'] = {
            'tm': round(row[0], 2) if row[0] else None,
            'icd11_standard': round(row[1], 2) if row[1] else None,
            'icd11_tm2': round(row[2], 2) if row[2] else None
        }
        
        return stats
    
    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dictionary"""
        columns = [desc[0] for desc in self.cursor.description]
        record = dict(zip(columns, row))
        
        # Parse JSON fields
        if record.get('tm_system_output'):
            record['tm_system_output'] = json.loads(record['tm_system_output'])
        if record.get('icd11_standard_output'):
            record['icd11_standard_output'] = json.loads(record['icd11_standard_output'])
        if record.get('icd11_tm2_output'):
            record['icd11_tm2_output'] = json.loads(record['icd11_tm2_output'])
        if record.get('selected_tm_details'):
            record['selected_tm_details'] = json.loads(record['selected_tm_details'])
        if record.get('selected_icd11_standard_details'):
            record['selected_icd11_standard_details'] = json.loads(record['selected_icd11_standard_details'])
        if record.get('selected_icd11_tm2_details'):
            record['selected_icd11_tm2_details'] = json.loads(record['selected_icd11_tm2_details'])
        if record.get('fhir_json'):
            record['fhir_json'] = json.loads(record['fhir_json'])
        
        return record
    
    def export_to_csv(self, output_file: str, limit: int = None):
        """Export records to CSV file"""
        import csv
        
        query = 'SELECT * FROM mapping_records ORDER BY timestamp DESC'
        if limit:
            query += f' LIMIT {limit}'
        
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        
        if not rows:
            return
        
        columns = [desc[0] for desc in self.cursor.description]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Convenience function for CLI
def log_mapping_session(
    practitioner_id: str,
    encounter_id: str,
    patient_id: str,
    selected_system: str,
    query: str,
    tm_candidates: List[Dict],
    icd11_standard_candidates: List[Dict],
    icd11_tm2_candidates: List[Dict],
    selected_tm_candidate: Dict,
    selected_icd11_standard: Optional[Dict],
    selected_icd11_tm2: Optional[Dict],
    fhir_json: Dict
) -> int:
    """
    Convenience function to log a mapping session
    
    Returns:
        Record ID
    """
    with MappingDatabase() as db:
        record_id = db.insert_mapping_record(
            practitioner_id=practitioner_id,
            encounter_id=encounter_id,
            patient_id=patient_id,
            selected_system=selected_system,
            query=query,
            tm_candidates=tm_candidates,
            icd11_standard_candidates=icd11_standard_candidates,
            icd11_tm2_candidates=icd11_tm2_candidates,
            selected_tm_candidate=selected_tm_candidate,
            selected_icd11_standard=selected_icd11_standard,
            selected_icd11_tm2=selected_icd11_tm2,
            fhir_json=fhir_json
        )
    return record_id


# Example usage
if __name__ == "__main__":
    # Create database and show statistics
    with MappingDatabase() as db:
        stats = db.get_statistics()
        print("Database Statistics:")
        print(json.dumps(stats, indent=2))
