#!/usr/bin/env python3
"""
Test script for fuzzy matching / typo correction
Demonstrates the Levenshtein distance algorithm
"""

import sys
sys.path.insert(0, 'api')

from autocomplete import levenshtein_distance, fuzzy_match_terms

def test_levenshtein():
    """Test Levenshtein distance calculation"""
    print("=" * 60)
    print("Levenshtein Distance Tests")
    print("=" * 60)
    print()
    
    test_cases = [
        ("febr", "fever", 1),
        ("pian", "pain", 1),
        ("sweling", "swelling", 1),
        ("diabetis", "diabetes", 1),
        ("cough", "cold", 4),
        ("fever", "fever", 0),
        ("back pian", "back pain", 1),
    ]
    
    for s1, s2, expected in test_cases:
        distance = levenshtein_distance(s1, s2)
        status = "✅" if distance == expected else "❌"
        print(f"{status} '{s1}' → '{s2}': distance = {distance} (expected {expected})")
    
    print()

def test_fuzzy_matching():
    """Test fuzzy matching with sample dataset"""
    print("=" * 60)
    print("Fuzzy Matching Tests")
    print("=" * 60)
    print()
    
    # Sample dataset
    sample_data = [
        {"code": "SP42", "term": "Fever disorder", "definition": "High body temperature"},
        {"code": "SP43", "term": "Fever with chills", "definition": "Fever accompanied by chills"},
        {"code": "SP44", "term": "Pain disorder", "definition": "Chronic pain condition"},
        {"code": "SP45", "term": "Back pain", "definition": "Pain in the back region"},
        {"code": "SP46", "term": "Joint pain", "definition": "Pain in joints"},
        {"code": "SP47", "term": "Swelling", "definition": "Abnormal enlargement"},
        {"code": "SP48", "term": "Diabetes", "definition": "Metabolic disorder"},
    ]
    
    test_queries = [
        ("febr", "Should match 'Fever disorder'"),
        ("pian", "Should match 'Pain disorder'"),
        ("sweling", "Should match 'Swelling'"),
        ("diabetis", "Should match 'Diabetes'"),
        ("back pian", "Should match 'Back pain'"),
        ("xyz", "Should find no matches"),
    ]
    
    for query, description in test_queries:
        print(f"Query: '{query}' - {description}")
        matches = fuzzy_match_terms(query, sample_data, max_distance=2)
        
        if matches:
            print(f"  Found {len(matches)} match(es):")
            for item, distance in matches[:3]:
                print(f"    - {item['code']}: {item['term']} (distance: {distance})")
        else:
            print(f"  No matches found")
        print()

def interactive_test():
    """Interactive testing mode"""
    print("=" * 60)
    print("Interactive Fuzzy Matching Test")
    print("=" * 60)
    print()
    print("Enter two words to calculate Levenshtein distance")
    print("Type 'quit' to exit")
    print()
    
    while True:
        try:
            word1 = input("Word 1: ").strip()
            if word1.lower() == 'quit':
                break
            
            word2 = input("Word 2: ").strip()
            if word2.lower() == 'quit':
                break
            
            distance = levenshtein_distance(word1.lower(), word2.lower())
            print(f"  Distance: {distance}")
            
            if distance == 0:
                print(f"  ✅ Exact match!")
            elif distance <= 2:
                print(f"  💡 Close match - would suggest '{word2}'")
            else:
                print(f"  ❌ Too different - would not suggest")
            
            print()
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_test()
    else:
        test_levenshtein()
        test_fuzzy_matching()
        print()
        print("Run with 'interactive' argument for interactive mode:")
        print("  python test_fuzzy_matching.py interactive")
