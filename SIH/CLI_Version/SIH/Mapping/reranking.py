"""
Re-ranking Engine based on Database Selection Counts
Boosts ICD-11 and ICD-11 TM2 codes based on practitioner selection history
"""

import sqlite3
import math
from typing import List, Dict, Optional
from pathlib import Path

# Configuration
DB_FILE = Path(__file__).parent / "mapping_records.db"
MAX_BOOST = 0.5         # Safety Cap: Boost never exceeds 0.5
BOOST_WEIGHT = 0.1      # Multiplier: 10 selections = ~0.2 boost
MIN_SCORE_THRESHOLD = 0.3  # Filter out results below this score


class ReRankingEngine:
    """Re-ranks search results based on database selection history"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_FILE
    
    def get_selection_counts(self, system: str, query: str = None) -> Dict[str, Dict[str, int]]:
        """
        Get selection counts from database for a specific system
        
        Args:
            system: TM system (siddha, ayurveda, unani, ayurveda-sat)
            query: Optional query filter (not used currently, for future enhancement)
        
        Returns:
            Dictionary with counts for each code type:
            {
                'tm_codes': {'SP42': 15, 'SP43': 8, ...},
                'icd11_standard': {'MG26': 12, '1A00': 5, ...},
                'icd11_tm2': {'SR40': 20, 'SP42': 10, ...}
            }
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            counts = {
                'tm_codes': {},
                'icd11_standard': {},
                'icd11_tm2': {}
            }
            
            # Query for TM code selections
            cursor.execute("""
                SELECT selected_tm_code, COUNT(*) as count
                FROM mapping_records
                WHERE selected_system = ?
                AND selected_tm_code IS NOT NULL
                GROUP BY selected_tm_code
            """, (system,))
            
            for code, count in cursor.fetchall():
                counts['tm_codes'][code] = count
            
            # Query for ICD-11 Standard selections
            cursor.execute("""
                SELECT selected_icd11_standard_code, COUNT(*) as count
                FROM mapping_records
                WHERE selected_system = ?
                AND selected_icd11_standard_code IS NOT NULL
                GROUP BY selected_icd11_standard_code
            """, (system,))
            
            for code, count in cursor.fetchall():
                counts['icd11_standard'][code] = count
            
            # Query for ICD-11 TM2 selections
            cursor.execute("""
                SELECT selected_icd11_tm2_code, COUNT(*) as count
                FROM mapping_records
                WHERE selected_system = ?
                AND selected_icd11_tm2_code IS NOT NULL
                GROUP BY selected_icd11_tm2_code
            """, (system,))
            
            for code, count in cursor.fetchall():
                counts['icd11_tm2'][code] = count
            
            conn.close()
            return counts
            
        except sqlite3.Error as e:
            print(f"⚠️  Database error: {e}")
            return {'tm_codes': {}, 'icd11_standard': {}, 'icd11_tm2': {}}
        except Exception as e:
            print(f"⚠️  Error getting selection counts: {e}")
            return {'tm_codes': {}, 'icd11_standard': {}, 'icd11_tm2': {}}
    
    def calculate_boost(self, selection_count: int) -> float:
        """
        Calculate boost value based on selection count
        Uses logarithmic growth to prevent over-boosting
        
        Args:
            selection_count: Number of times code was selected
        
        Returns:
            Boost value (0.0 to MAX_BOOST)
        """
        if selection_count <= 0:
            return 0.0
        
        # Logarithmic growth: log10(count + 1) * weight
        log_boost = math.log10(selection_count + 1) * BOOST_WEIGHT
        
        # Cap at MAX_BOOST
        return min(log_boost, MAX_BOOST)
    
    def apply_boost_to_results(
        self,
        results: List[Dict],
        selection_counts: Dict[str, int],
        code_field: str = 'code'
    ) -> List[Dict]:
        """
        Apply boost to search results based on selection counts
        
        Args:
            results: List of search results
            selection_counts: Dictionary of {code: count}
            code_field: Field name containing the code
        
        Returns:
            Re-ranked results with boost applied
        """
        for item in results:
            code = item.get(code_field)
            if not code:
                continue
            
            base_score = item.get('score', 0.5)
            selection_count = selection_counts.get(code, 0)
            
            # Calculate boost
            boost = self.calculate_boost(selection_count)
            
            # Apply boost
            item['final_score'] = base_score + boost
            item['boost_applied'] = round(boost, 3)
            item['selection_count'] = selection_count
        
        # Sort by final_score descending
        results.sort(key=lambda x: x.get('final_score', x.get('score', 0)), reverse=True)
        
        return results
    
    def rerank_mapping_results(
        self,
        mapping_result: Dict,
        system: str,
        query: str = None
    ) -> Dict:
        """
        Re-rank all candidates in a mapping result
        
        Args:
            mapping_result: Result from mapper.map_to_icd()
            system: TM system (siddha, ayurveda, unani, ayurveda-sat)
            query: Optional query for context
        
        Returns:
            Mapping result with re-ranked candidates
        """
        # Get selection counts from database
        counts = self.get_selection_counts(system, query)
        
        # Normalize system key
        system_key = system.replace('-', '_')
        
        # Re-rank TM candidates
        tm_candidates_key = f"{system_key}_candidates"
        if tm_candidates_key in mapping_result:
            mapping_result[tm_candidates_key] = self.apply_boost_to_results(
                mapping_result[tm_candidates_key],
                counts['tm_codes'],
                code_field='code'
            )
        
        # Re-rank ICD-11 Standard candidates
        if 'icd11_standard_candidates' in mapping_result:
            mapping_result['icd11_standard_candidates'] = self.apply_boost_to_results(
                mapping_result['icd11_standard_candidates'],
                counts['icd11_standard'],
                code_field='code'
            )
        
        # Re-rank ICD-11 TM2 candidates
        if 'icd11_tm2_candidates' in mapping_result:
            mapping_result['icd11_tm2_candidates'] = self.apply_boost_to_results(
                mapping_result['icd11_tm2_candidates'],
                counts['icd11_tm2'],
                code_field='code'
            )
        
        return mapping_result
    
    def filter_low_confidence(
        self,
        results: List[Dict],
        threshold: float = MIN_SCORE_THRESHOLD
    ) -> List[Dict]:
        """
        Filter out results below confidence threshold
        
        Args:
            results: List of search results
            threshold: Minimum score threshold
        
        Returns:
            Filtered results
        """
        return [
            item for item in results
            if item.get('final_score', item.get('score', 0)) >= threshold
        ]
    
    def get_top_codes_by_system(self, system: str, limit: int = 10) -> Dict:
        """
        Get top selected codes for a system (for analytics/display)
        
        Args:
            system: TM system
            limit: Number of top codes to return
        
        Returns:
            Dictionary with top codes for each category
        """
        counts = self.get_selection_counts(system)
        
        # Sort and limit
        top_tm = sorted(
            counts['tm_codes'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        top_icd11_standard = sorted(
            counts['icd11_standard'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        top_icd11_tm2 = sorted(
            counts['icd11_tm2'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return {
            'tm_codes': top_tm,
            'icd11_standard': top_icd11_standard,
            'icd11_tm2': top_icd11_tm2
        }


# Convenience functions for easy integration
def rerank_results(mapping_result: Dict, system: str, query: str = None) -> Dict:
    """
    Convenience function to re-rank mapping results
    
    Args:
        mapping_result: Result from mapper.map_to_icd()
        system: TM system
        query: Optional query
    
    Returns:
        Re-ranked mapping result
    """
    engine = ReRankingEngine()
    return engine.rerank_mapping_results(mapping_result, system, query)


def get_selection_stats(system: str) -> Dict:
    """
    Get selection statistics for a system
    
    Args:
        system: TM system
    
    Returns:
        Statistics dictionary
    """
    engine = ReRankingEngine()
    return engine.get_top_codes_by_system(system)


# Example usage
if __name__ == "__main__":
    # Test the re-ranking engine
    engine = ReRankingEngine()
    
    # Get selection counts for Siddha
    print("Selection Counts for Siddha:")
    print("=" * 60)
    counts = engine.get_selection_counts('siddha')
    
    print("\nTM Codes:")
    for code, count in sorted(counts['tm_codes'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {code}: {count} selections")
    
    print("\nICD-11 Standard:")
    for code, count in sorted(counts['icd11_standard'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {code}: {count} selections")
    
    print("\nICD-11 TM2:")
    for code, count in sorted(counts['icd11_tm2'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {code}: {count} selections")
    
    # Test boost calculation
    print("\n" + "=" * 60)
    print("Boost Calculation Examples:")
    print("=" * 60)
    for count in [1, 5, 10, 20, 50, 100]:
        boost = engine.calculate_boost(count)
        print(f"  {count} selections → boost: {boost:.3f}")
