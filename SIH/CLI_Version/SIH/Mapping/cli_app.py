#!/usr/bin/env python3
"""
CLI Application for Traditional Medicine → ICD-11 Mapping
Menu-driven interface with FHIR JSON export
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from search import search_siddha
from search_ayurveda import search_ayurveda
from search_unani import search_unani
from search_ayurveda_sat import search_ayurveda_sat
from build_indexes.mapper import map_to_icd
from fhir_generator import generate_fhir_from_mapping
from database import log_mapping_session
from reranking import rerank_results


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TMICDMapper:
    """Traditional Medicine to ICD-11 Mapper CLI Application"""
    
    def __init__(self):
        self.current_system = None
        self.current_query = None
        self.tm_candidates = []
        self.selected_tm_candidate = None
        self.icd11_standard_candidates = []
        self.icd11_tm2_candidates = []
        self.selected_icd11_standard = None
        self.selected_icd11_tm2 = None
        self.mapping_result = None
    
    def format_system_name(self, system=None):
        """Format system name for display"""
        sys_name = system or self.current_system
        if not sys_name:
            return "Unknown"
        
        if sys_name == 'ayurveda-sat':
            return 'Ayurveda-SAT'
        else:
            return sys_name.upper()
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, text):
        """Print colored header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    def print_success(self, text):
        """Print success message"""
        print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")
    
    def print_error(self, text):
        """Print error message"""
        print(f"{Colors.RED}✗ {text}{Colors.ENDC}")
    
    def print_info(self, text):
        """Print info message"""
        print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")
    
    def print_warning(self, text):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")
    
    def wait_for_enter(self):
        """Wait for user to press Enter"""
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")
    
    def main_menu(self):
        """Display main menu"""
        while True:
            self.clear_screen()
            self.print_header("NAMASTE → ICD-11 Mapping System")
            
            print(f"{Colors.BOLD}Main Menu:{Colors.ENDC}\n")
            print(f"  {Colors.BLUE}1.{Colors.ENDC} Select Traditional Medicine System")
            print(f"  {Colors.BLUE}2.{Colors.ENDC} Search for Diagnosis")
            print(f"  {Colors.BLUE}3.{Colors.ENDC} View Current Selections")
            print(f"  {Colors.BLUE}4.{Colors.ENDC} Generate FHIR JSON")
            print(f"  {Colors.BLUE}5.{Colors.ENDC} Save FHIR to File")
            print(f"  {Colors.BLUE}6.{Colors.ENDC} View System Logs")
            print(f"  {Colors.BLUE}7.{Colors.ENDC} Reset Session")
            print(f"  {Colors.BLUE}0.{Colors.ENDC} Exit")
            
            # Show current status
            if self.current_system:
                print(f"\n{Colors.GREEN}Current System: {self.format_system_name()}{Colors.ENDC}")
            if self.selected_tm_candidate:
                print(f"{Colors.GREEN}Selected TM: {self.selected_tm_candidate['code']}{Colors.ENDC}")
            if self.selected_icd11_standard or self.selected_icd11_tm2:
                print(f"{Colors.GREEN}ICD Codes Selected: {bool(self.selected_icd11_standard)} Standard, {bool(self.selected_icd11_tm2)} TM2{Colors.ENDC}")
            
            choice = input(f"\n{Colors.BOLD}Enter your choice: {Colors.ENDC}").strip()
            
            if choice == '1':
                self.select_system()
            elif choice == '2':
                self.search_diagnosis()
            elif choice == '3':
                self.view_selections()
            elif choice == '4':
                self.generate_fhir()
            elif choice == '5':
                self.save_fhir_to_file()
            elif choice == '6':
                self.view_database_entries()
            elif choice == '7':
                self.reset_session()
            elif choice == '0':
                self.print_success("Thank you for using TM-ICD Mapper!")
                sys.exit(0)
            else:
                self.print_error("Invalid choice. Please try again.")
                self.wait_for_enter()
    
    def select_system(self):
        """Select Traditional Medicine system"""
        self.clear_screen()
        self.print_header("Select Traditional Medicine System")
        
        print(f"{Colors.BOLD}Available Systems:{Colors.ENDC}\n")
        print(f"  {Colors.BLUE}1.{Colors.ENDC} Siddha")
        print(f"  {Colors.BLUE}2.{Colors.ENDC} Ayurveda")
        print(f"  {Colors.BLUE}3.{Colors.ENDC} Unani")
        print(f"  {Colors.BLUE}4.{Colors.ENDC} Ayurveda-SAT")
        print(f"  {Colors.BLUE}0.{Colors.ENDC} Back to Main Menu")
        
        choice = input(f"\n{Colors.BOLD}Enter your choice: {Colors.ENDC}").strip()
        
        systems = {'1': 'siddha', '2': 'ayurveda', '3': 'unani', '4': 'ayurveda-sat'}
        
        if choice in systems:
            self.current_system = systems[choice]
            self.print_success(f"Selected system: {self.format_system_name()}")
            self.wait_for_enter()
        elif choice == '0':
            return
        else:
            self.print_error("Invalid choice.")
            self.wait_for_enter()
    
    def search_diagnosis(self):
        """Search for diagnosis"""
        if not self.current_system:
            self.print_error("Please select a Traditional Medicine system first!")
            self.wait_for_enter()
            return
        
        self.clear_screen()
        self.print_header(f"Search {self.format_system_name()} Diagnosis")
        
        query = input(f"{Colors.BOLD}Enter symptoms or condition: {Colors.ENDC}").strip()
        
        if not query:
            self.print_error("Query cannot be empty.")
            self.wait_for_enter()
            return
        
        self.current_query = query
        
        # Search based on system
        self.print_info(f"Searching {self.format_system_name()} database...")
        
        try:
            if self.current_system == 'siddha':
                result = search_siddha(query)
            elif self.current_system == 'ayurveda':
                result = search_ayurveda(query)
            elif self.current_system == 'unani':
                result = search_unani(query)
            elif self.current_system == 'ayurveda-sat':
                result = search_ayurveda_sat(query)
            
            self.tm_candidates = result.get('candidates', [])
            
            if not self.tm_candidates:
                self.print_error("No results found.")
                self.wait_for_enter()
                return
            
            self.print_success(f"Found {len(self.tm_candidates)} candidates")
            
            # Display and select TM candidate
            self.select_tm_candidate()
            
        except Exception as e:
            self.print_error(f"Search error: {str(e)}")
            self.wait_for_enter()
    
    def select_tm_candidate(self):
        """Select Traditional Medicine candidate"""
        self.clear_screen()
        self.print_header(f"{self.format_system_name()} Candidates")
        
        print(f"{Colors.BOLD}Top {len(self.tm_candidates)} Results:{Colors.ENDC}\n")
        
        for i, candidate in enumerate(self.tm_candidates, 1):
            print(f"{Colors.BLUE}{i}.{Colors.ENDC} {Colors.BOLD}{candidate['code']}{Colors.ENDC}")
            
            # Show both original and English terms if available
            if 'english' in candidate and candidate.get('term') != candidate.get('english'):
                print(f"   Original: {candidate.get('term', 'N/A')}")
                print(f"   English: {candidate.get('english', 'N/A')}")
            else:
                print(f"   Term: {candidate.get('term', candidate.get('english', 'N/A'))}")
            
            # Show definition (truncated)
            definition = candidate.get('definition', '')
            if definition and definition != 'No description available.':
                print(f"   {Colors.CYAN}{definition[:100]}...{Colors.ENDC}")
            
            print(f"   Score: {candidate.get('score', 0):.4f}\n")
        
        print(f"  {Colors.BLUE}0.{Colors.ENDC} Back")
        
        choice = input(f"\n{Colors.BOLD}Select a candidate (1-{len(self.tm_candidates)}): {Colors.ENDC}").strip()
        
        try:
            idx = int(choice)
            if idx == 0:
                return
            if 1 <= idx <= len(self.tm_candidates):
                self.selected_tm_candidate = self.tm_candidates[idx - 1]
                self.print_success(f"Selected: {self.selected_tm_candidate['code']}")
                
                # Now map to ICD
                self.map_to_icd_codes()
            else:
                self.print_error("Invalid selection.")
                self.wait_for_enter()
        except ValueError:
            self.print_error("Please enter a valid number.")
            self.wait_for_enter()
    
    def map_to_icd_codes(self):
        """Map selected TM candidate to ICD codes"""
        self.print_info("Mapping to ICD-11 codes...")
        
        try:
            # Build query from selected candidate
            query = self.current_query
            if self.selected_tm_candidate.get('english'):
                query += " " + self.selected_tm_candidate['english']
            
            self.mapping_result = map_to_icd(query, system=self.current_system)
            
            # Apply re-ranking based on database selection history
            self.mapping_result = rerank_results(self.mapping_result, self.current_system, query)
            
            self.icd11_standard_candidates = self.mapping_result.get('icd11_standard_candidates', [])
            self.icd11_tm2_candidates = self.mapping_result.get('icd11_tm2_candidates', [])
            
            self.print_success(f"Found {len(self.icd11_standard_candidates)} ICD-11 Standard codes")
            self.print_success(f"Found {len(self.icd11_tm2_candidates)} ICD-11 TM2 codes")
            
            self.wait_for_enter()
            
            # Select ICD codes
            self.select_icd_codes()
            
        except Exception as e:
            self.print_error(f"Mapping error: {str(e)}")
            self.wait_for_enter()
    
    def select_icd_codes(self):
        """Select ICD-11 codes"""
        while True:
            self.clear_screen()
            self.print_header("Select ICD-11 Codes")
            
            print(f"{Colors.BOLD}Options:{Colors.ENDC}\n")
            print(f"  {Colors.BLUE}1.{Colors.ENDC} Select ICD-11 Standard Code")
            print(f"  {Colors.BLUE}2.{Colors.ENDC} Select ICD-11 TM2 Code")
            print(f"  {Colors.BLUE}3.{Colors.ENDC} View Current Selections")
            print(f"  {Colors.BLUE}0.{Colors.ENDC} Done (Back to Main Menu)")
            
            # Show current selections
            if self.selected_icd11_standard:
                print(f"\n{Colors.GREEN}✓ ICD-11 Standard: {self.selected_icd11_standard['code']}{Colors.ENDC}")
            else:
                print(f"\n{Colors.YELLOW}○ ICD-11 Standard: Not selected{Colors.ENDC}")
            
            if self.selected_icd11_tm2:
                print(f"{Colors.GREEN}✓ ICD-11 TM2: {self.selected_icd11_tm2['code']}{Colors.ENDC}")
            else:
                print(f"{Colors.YELLOW}○ ICD-11 TM2: Not selected{Colors.ENDC}")
            
            choice = input(f"\n{Colors.BOLD}Enter your choice: {Colors.ENDC}").strip()
            
            if choice == '1':
                self.select_icd11_standard()
            elif choice == '2':
                self.select_icd11_tm2()
            elif choice == '3':
                self.view_selections()
            elif choice == '0':
                if not self.selected_icd11_standard and not self.selected_icd11_tm2:
                    self.print_warning("No ICD codes selected. You need at least one for FHIR export.")
                    self.wait_for_enter()
                return
            else:
                self.print_error("Invalid choice.")
                self.wait_for_enter()
    
    def select_icd11_standard(self):
        """Select ICD-11 Standard code"""
        if not self.icd11_standard_candidates:
            self.print_error("No ICD-11 Standard candidates available.")
            self.wait_for_enter()
            return
        
        self.clear_screen()
        self.print_header("ICD-11 Standard Candidates")
        
        for i, candidate in enumerate(self.icd11_standard_candidates, 1):
            print(f"{Colors.BLUE}{i}.{Colors.ENDC} {Colors.BOLD}{candidate['code']}{Colors.ENDC} - {candidate['title']}")
            
            definition = candidate.get('definition', '')
            if definition:
                print(f"   {Colors.CYAN}{definition[:100]}...{Colors.ENDC}")
            
            # Show score with boost information
            base_score = candidate.get('score', 0)
            final_score = candidate.get('final_score', base_score)
            boost = candidate.get('boost_applied', 0)
            selection_count = candidate.get('selection_count', 0)
            
            if boost > 0:
                print(f"   Score: {final_score:.4f} (base: {base_score:.4f} + boost: {boost:.3f}) | {Colors.GREEN}Selected {selection_count}x{Colors.ENDC}\n")
            else:
                print(f"   Score: {final_score:.4f}\n")
        
        print(f"  {Colors.BLUE}0.{Colors.ENDC} Back")
        
        choice = input(f"\n{Colors.BOLD}Select a code (1-{len(self.icd11_standard_candidates)}): {Colors.ENDC}").strip()
        
        try:
            idx = int(choice)
            if idx == 0:
                return
            if 1 <= idx <= len(self.icd11_standard_candidates):
                self.selected_icd11_standard = self.icd11_standard_candidates[idx - 1]
                self.print_success(f"Selected ICD-11 Standard: {self.selected_icd11_standard['code']}")
                self.wait_for_enter()
            else:
                self.print_error("Invalid selection.")
                self.wait_for_enter()
        except ValueError:
            self.print_error("Please enter a valid number.")
            self.wait_for_enter()
    
    def select_icd11_tm2(self):
        """Select ICD-11 TM2 code"""
        if not self.icd11_tm2_candidates:
            self.print_error("No ICD-11 TM2 candidates available.")
            self.wait_for_enter()
            return
        
        self.clear_screen()
        self.print_header("ICD-11 TM2 Candidates")
        
        for i, candidate in enumerate(self.icd11_tm2_candidates, 1):
            print(f"{Colors.BLUE}{i}.{Colors.ENDC} {Colors.BOLD}{candidate['code']}{Colors.ENDC} - {candidate['title']}")
            
            definition = candidate.get('definition', '')
            if definition:
                print(f"   {Colors.CYAN}{definition[:100]}...{Colors.ENDC}")
            
            # Show score with boost information
            base_score = candidate.get('score', 0)
            final_score = candidate.get('final_score', base_score)
            boost = candidate.get('boost_applied', 0)
            selection_count = candidate.get('selection_count', 0)
            
            if boost > 0:
                print(f"   Score: {final_score:.4f} (base: {base_score:.4f} + boost: {boost:.3f}) | {Colors.GREEN}Selected {selection_count}x{Colors.ENDC}\n")
            else:
                print(f"   Score: {final_score:.4f}\n")
        
        print(f"  {Colors.BLUE}0.{Colors.ENDC} Back")
        
        choice = input(f"\n{Colors.BOLD}Select a code (1-{len(self.icd11_tm2_candidates)}): {Colors.ENDC}").strip()
        
        try:
            idx = int(choice)
            if idx == 0:
                return
            if 1 <= idx <= len(self.icd11_tm2_candidates):
                self.selected_icd11_tm2 = self.icd11_tm2_candidates[idx - 1]
                self.print_success(f"Selected ICD-11 TM2: {self.selected_icd11_tm2['code']}")
                self.wait_for_enter()
            else:
                self.print_error("Invalid selection.")
                self.wait_for_enter()
        except ValueError:
            self.print_error("Please enter a valid number.")
            self.wait_for_enter()
    
    def view_selections(self):
        """View current selections"""
        self.clear_screen()
        self.print_header("Current Selections")
        
        if not self.selected_tm_candidate:
            self.print_warning("No selections made yet.")
            self.wait_for_enter()
            return
        
        print(f"{Colors.BOLD}Traditional Medicine:{Colors.ENDC}")
        print(f"  System: {Colors.GREEN}{self.format_system_name()}{Colors.ENDC}")
        print(f"  Code: {Colors.GREEN}{self.selected_tm_candidate['code']}{Colors.ENDC}")
        
        if 'english' in self.selected_tm_candidate:
            print(f"  English: {self.selected_tm_candidate['english']}")
        if 'term' in self.selected_tm_candidate and self.selected_tm_candidate.get('term') != self.selected_tm_candidate.get('english'):
            print(f"  Original: {self.selected_tm_candidate['term']}")
        
        definition = self.selected_tm_candidate.get('definition', '')
        if definition and definition != 'No description available.':
            print(f"  Definition: {definition[:150]}...")
        
        print(f"\n{Colors.BOLD}ICD-11 Standard:{Colors.ENDC}")
        if self.selected_icd11_standard:
            print(f"  Code: {Colors.GREEN}{self.selected_icd11_standard['code']}{Colors.ENDC}")
            print(f"  Title: {self.selected_icd11_standard['title']}")
            print(f"  Score: {self.selected_icd11_standard.get('score', 0):.4f}")
        else:
            print(f"  {Colors.YELLOW}Not selected{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}ICD-11 TM2:{Colors.ENDC}")
        if self.selected_icd11_tm2:
            print(f"  Code: {Colors.GREEN}{self.selected_icd11_tm2['code']}{Colors.ENDC}")
            print(f"  Title: {self.selected_icd11_tm2['title']}")
            print(f"  Score: {self.selected_icd11_tm2.get('score', 0):.4f}")
        else:
            print(f"  {Colors.YELLOW}Not selected{Colors.ENDC}")
        
        self.wait_for_enter()
    
    def generate_fhir(self):
        """Generate FHIR JSON"""
        if not self.selected_tm_candidate:
            self.print_error("Please select a Traditional Medicine diagnosis first!")
            self.wait_for_enter()
            return
        
        if not self.selected_icd11_standard and not self.selected_icd11_tm2:
            self.print_error("Please select at least one ICD-11 code!")
            self.wait_for_enter()
            return
        
        self.clear_screen()
        self.print_header("Generate FHIR JSON")
        
        # Get patient details
        print(f"{Colors.BOLD}Enter Patient Details (or press Enter for defaults):{Colors.ENDC}\n")
        
        patient_id = input(f"Patient ID [{Colors.CYAN}patient-{datetime.now().strftime('%Y%m%d%H%M%S')}{Colors.ENDC}]: ").strip()
        if not patient_id:
            patient_id = f"patient-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        encounter_id = input(f"Encounter ID [{Colors.CYAN}encounter-{datetime.now().strftime('%Y%m%d%H%M%S')}{Colors.ENDC}]: ").strip()
        if not encounter_id:
            encounter_id = f"encounter-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        practitioner_id = input(f"Practitioner ID [{Colors.CYAN}practitioner-001{Colors.ENDC}]: ").strip()
        if not practitioner_id:
            practitioner_id = "practitioner-001"
        
        self.print_info("Generating FHIR Condition resource...")
        
        try:
            # Build custom mapping result with only selected codes
            custom_mapping = {
                "system": self.current_system,
                "input": self.current_query or "",
                f"{self.current_system}_candidates": [self.selected_tm_candidate],
                "icd11_standard_candidates": [self.selected_icd11_standard] if self.selected_icd11_standard else [],
                "icd11_tm2_candidates": [self.selected_icd11_tm2] if self.selected_icd11_tm2 else []
            }
            
            fhir_condition = generate_fhir_from_mapping(
                mapping_result=custom_mapping,
                patient_id=patient_id,
                encounter_id=encounter_id,
                practitioner_id=practitioner_id
            )
            
            self.print_success("FHIR Condition resource generated successfully!")
            
            # Display FHIR JSON
            print(f"\n{Colors.BOLD}FHIR JSON:{Colors.ENDC}\n")
            print(json.dumps(fhir_condition, indent=2))
            
            # Store for saving
            self.fhir_condition = fhir_condition
            
            # Log to database
            try:
                self.print_info("Logging session to database...")
                
                record_id = log_mapping_session(
                    practitioner_id=practitioner_id,
                    encounter_id=encounter_id,
                    patient_id=patient_id,
                    selected_system=self.current_system,
                    query=self.current_query,
                    tm_candidates=self.tm_candidates[:10],  # Top 10
                    icd11_standard_candidates=self.icd11_standard_candidates[:10],  # Top 10
                    icd11_tm2_candidates=self.icd11_tm2_candidates[:10],  # Top 10
                    selected_tm_candidate=self.selected_tm_candidate,
                    selected_icd11_standard=self.selected_icd11_standard,
                    selected_icd11_tm2=self.selected_icd11_tm2,
                    fhir_json=fhir_condition
                )
                
                self.print_success(f"Session logged to database (Record ID: {record_id})")
                
                # Display rank information
                if self.selected_tm_candidate:
                    tm_rank = self._find_rank(self.selected_tm_candidate, self.tm_candidates)
                    if tm_rank:
                        self.print_info(f"Selected TM code was at position #{tm_rank} in results")
                
                if self.selected_icd11_standard:
                    std_rank = self._find_rank(self.selected_icd11_standard, self.icd11_standard_candidates)
                    if std_rank:
                        self.print_info(f"Selected ICD-11 Standard code was at position #{std_rank} in results")
                
                if self.selected_icd11_tm2:
                    tm2_rank = self._find_rank(self.selected_icd11_tm2, self.icd11_tm2_candidates)
                    if tm2_rank:
                        self.print_info(f"Selected ICD-11 TM2 code was at position #{tm2_rank} in results")
                
            except Exception as db_error:
                self.print_warning(f"Database logging failed: {str(db_error)}")
                self.print_info("FHIR generation succeeded, but session was not logged to database")
            
            self.wait_for_enter()
            
        except Exception as e:
            self.print_error(f"FHIR generation error: {str(e)}")
            import traceback
            traceback.print_exc()
            self.wait_for_enter()
    
    def save_fhir_to_file(self):
        """Save FHIR JSON to file"""
        if not hasattr(self, 'fhir_condition'):
            self.print_error("Please generate FHIR JSON first!")
            self.wait_for_enter()
            return
        
        self.clear_screen()
        self.print_header("Save FHIR JSON to File")
        
        default_filename = f"fhir-condition-{self.selected_tm_candidate['code']}-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        
        filename = input(f"Filename [{Colors.CYAN}{default_filename}{Colors.ENDC}]: ").strip()
        if not filename:
            filename = default_filename
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        try:
            output_dir = Path(__file__).parent / "fhir_output"
            output_dir.mkdir(exist_ok=True)
            
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.fhir_condition, f, indent=2, ensure_ascii=False)
            
            self.print_success(f"FHIR JSON saved to: {filepath}")
            self.wait_for_enter()
            
        except Exception as e:
            self.print_error(f"Error saving file: {str(e)}")
            self.wait_for_enter()
    
    def reset_session(self):
        """Reset current session"""
        self.clear_screen()
        self.print_header("Reset Session")
        
        confirm = input(f"{Colors.YELLOW}Are you sure you want to reset? (y/n): {Colors.ENDC}").strip().lower()
        
        if confirm == 'y':
            self.current_system = None
            self.current_query = None
            self.tm_candidates = []
            self.selected_tm_candidate = None
            self.icd11_standard_candidates = []
            self.icd11_tm2_candidates = []
            self.selected_icd11_standard = None
            self.selected_icd11_tm2 = None
            self.mapping_result = None
            
            if hasattr(self, 'fhir_condition'):
                delattr(self, 'fhir_condition')
            
            self.print_success("Session reset successfully!")
        else:
            self.print_info("Reset cancelled.")
        
        self.wait_for_enter()
    
    def view_database_entries(self):
        """View database entries in table format"""
        self.clear_screen()
        self.print_header("System Logs")
        
        try:
            from database import MappingDatabase
            
            with MappingDatabase() as db:
                # Get total count
                db.cursor.execute('SELECT COUNT(*) FROM mapping_records')
                total_count = db.cursor.fetchone()[0]
                
                if total_count == 0:
                    self.print_warning("No database entries found.")
                    self.wait_for_enter()
                    return
                
                print(f"{Colors.BOLD}Total Records: {Colors.GREEN}{total_count}{Colors.ENDC}\n")
                
                # Ask for limit
                limit_input = input(f"How many recent entries to display? [{Colors.CYAN}20{Colors.ENDC}]: ").strip()
                limit = int(limit_input) if limit_input.isdigit() else 20
                
                # Get recent records
                records = db.get_recent_records(limit=limit)
                
                if not records:
                    self.print_warning("No records found.")
                    self.wait_for_enter()
                    return
                
                # Display table header
                print(f"\n{Colors.BOLD}{'ID':<5} {'Timestamp':<20} {'Practitioner':<15} {'System':<10} {'Query':<25} {'TM Code':<12} {'Rank':<5} {'ICD-11 Std':<12} {'Rank':<5} {'ICD-11 TM2':<12} {'Rank':<5}{Colors.ENDC}")
                print(f"{Colors.BOLD}{'-'*150}{Colors.ENDC}")
                
                # Display records
                for record in records:
                    record_id = str(record.get('id', ''))[:5]
                    timestamp = record.get('timestamp', '')[:19].replace('T', ' ')
                    practitioner = record.get('practitioner_id', '')[:15]
                    system = record.get('selected_system', '')[:10]
                    query = record.get('query', '')[:25]
                    
                    tm_code = record.get('selected_tm_code', '')[:12]
                    tm_rank = str(record.get('selected_tm_rank', ''))[:5] if record.get('selected_tm_rank') else '-'
                    
                    icd_std_code = record.get('selected_icd11_standard_code', '')[:12] if record.get('selected_icd11_standard_code') else '-'
                    icd_std_rank = str(record.get('selected_icd11_standard_rank', ''))[:5] if record.get('selected_icd11_standard_rank') else '-'
                    
                    icd_tm2_code = record.get('selected_icd11_tm2_code', '')[:12] if record.get('selected_icd11_tm2_code') else '-'
                    icd_tm2_rank = str(record.get('selected_icd11_tm2_rank', ''))[:5] if record.get('selected_icd11_tm2_rank') else '-'
                    
                    print(f"{Colors.CYAN}{record_id:<5}{Colors.ENDC} {timestamp:<20} {practitioner:<15} {Colors.GREEN}{system:<10}{Colors.ENDC} {query:<25} {Colors.YELLOW}{tm_code:<12}{Colors.ENDC} {tm_rank:<5} {icd_std_code:<12} {icd_std_rank:<5} {icd_tm2_code:<12} {icd_tm2_rank:<5}")
                
                print(f"\n{Colors.BOLD}Legend:{Colors.ENDC}")
                print(f"  Rank: Position in top 10 results where practitioner selected the code")
                print(f"  '-': Code not selected")
                
        except Exception as e:
            self.print_error(f"Error retrieving database entries: {str(e)}")
            import traceback
            traceback.print_exc()
        
        self.wait_for_enter()
    
    def _find_rank(self, selected_item, candidates):
        """Find the rank (position) of selected item in candidates list"""
        if not selected_item or not candidates:
            return None
        
        selected_code = selected_item.get('code')
        for i, candidate in enumerate(candidates[:10], 1):  # Top 10 only
            if candidate.get('code') == selected_code:
                return i
        
        return None  # Not in top 10


def main():
    """Main entry point"""
    try:
        app = TMICDMapper()
        app.main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Program interrupted by user.{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
