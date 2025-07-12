"""
LegacyLabs GEDCOM Parser
========================
A Python module for parsing GEDCOM genealogy files and extracting
story-worthy elements for documentary generation.
"""

import re
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
import json


class EventType(Enum):
    """Types of life events we track for storytelling"""
    BIRTH = "BIRT"
    DEATH = "DEAT"
    MARRIAGE = "MARR"
    DIVORCE = "DIV"
    IMMIGRATION = "IMMI"
    EMIGRATION = "EMIG"
    CENSUS = "CENS"
    OCCUPATION = "OCCU"
    EDUCATION = "EDUC"
    MILITARY = "MILI"
    BAPTISM = "BAPM"
    BURIAL = "BURI"
    RESIDENCE = "RESI"


class StoryTheme(Enum):
    """Narrative themes that can be detected from the data"""
    IMMIGRATION = "immigration"
    LARGE_FAMILY = "large_family"
    MILITARY_SERVICE = "military_service"
    EARLY_DEATH = "early_death"
    LONG_LIFE = "long_life"
    MULTIPLE_MARRIAGES = "multiple_marriages"
    PIONEER = "pioneer"
    TRAGEDY = "tragedy"
    SUCCESS = "success"
    FAMILY_BUSINESS = "family_business"


@dataclass
class Location:
    """Represents a geographic location with parsing for storytelling"""
    full_text: str
    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    
    def __post_init__(self):
        """Parse location string into components"""
        parts = [p.strip() for p in self.full_text.split(',')]
        
        if len(parts) >= 4:
            self.city = parts[0]
            self.county = parts[1]
            self.state = parts[2]
            self.country = parts[3]
        elif len(parts) == 3:
            self.city = parts[0]
            self.state = parts[1]
            self.country = parts[2]
        elif len(parts) == 2:
            self.city = parts[0]
            self.country = parts[1]
        elif len(parts) == 1:
            self.country = parts[0]
    
    def get_display_name(self) -> str:
        """Get a narrative-friendly location name"""
        if self.city and self.state:
            return f"{self.city}, {self.state}"
        elif self.city and self.country:
            return f"{self.city}, {self.country}"
        return self.full_text


@dataclass
class Event:
    """Represents a life event with narrative context"""
    event_type: EventType
    date: Optional[str] = None
    location: Optional[Location] = None
    description: Optional[str] = None
    age_at_event: Optional[int] = None
    
    def get_year(self) -> Optional[int]:
        """Extract year from date string"""
        if self.date:
            year_match = re.search(r'\b(1[0-9]{3}|2[0-9]{3})\b', self.date)
            if year_match:
                return int(year_match.group(1))
        return None
    
    def get_narrative_date(self) -> str:
        """Convert date to narrative-friendly format"""
        if not self.date:
            return "on an unknown date"
        
        # Handle different date formats
        if re.match(r'^\d{4}$', self.date):
            return f"in {self.date}"
        elif re.match(r'^\d{1,2} \w+ \d{4}$', self.date):
            return f"on {self.date}"
        elif "ABT" in self.date:
            return self.date.replace("ABT", "around")
        elif "BEF" in self.date:
            return self.date.replace("BEF", "before")
        elif "AFT" in self.date:
            return self.date.replace("AFT", "after")
        
        return f"on {self.date}"


@dataclass
class Individual:
    """Represents a person with all their life events and relationships"""
    id: str
    given_names: Optional[str] = None
    surname: Optional[str] = None
    sex: Optional[str] = None
    events: List[Event] = field(default_factory=list)
    family_child: List[str] = field(default_factory=list)  # Families where child
    family_spouse: List[str] = field(default_factory=list)  # Families where spouse
    notes: List[str] = field(default_factory=list)
    
    def get_full_name(self) -> str:
        """Get narrative-friendly full name"""
        if self.given_names and self.surname:
            return f"{self.given_names} {self.surname}"
        return self.given_names or self.surname or "Unknown"
    
    def get_birth_year(self) -> Optional[int]:
        """Get birth year for age calculations"""
        for event in self.events:
            if event.event_type == EventType.BIRTH:
                return event.get_year()
        return None
    
    def get_death_year(self) -> Optional[int]:
        """Get death year for lifespan calculations"""
        for event in self.events:
            if event.event_type == EventType.DEATH:
                return event.get_year()
        return None
    
    def get_lifespan(self) -> Optional[int]:
        """Calculate lifespan in years"""
        birth = self.get_birth_year()
        death = self.get_death_year()
        if birth and death:
            return death - birth
        return None
    
    def get_story_themes(self) -> Set[StoryTheme]:
        """Identify narrative themes from life events"""
        themes = set()
        
        # Check lifespan
        lifespan = self.get_lifespan()
        if lifespan:
            if lifespan < 50:
                themes.add(StoryTheme.EARLY_DEATH)
            elif lifespan > 85:
                themes.add(StoryTheme.LONG_LIFE)
        
        # Check for immigration
        for event in self.events:
            if event.event_type in [EventType.IMMIGRATION, EventType.EMIGRATION]:
                themes.add(StoryTheme.IMMIGRATION)
            elif event.event_type == EventType.MILITARY:
                themes.add(StoryTheme.MILITARY_SERVICE)
        
        # Check marriages
        marriage_count = sum(1 for e in self.events if e.event_type == EventType.MARRIAGE)
        if marriage_count > 1:
            themes.add(StoryTheme.MULTIPLE_MARRIAGES)
        
        # Check family size (as parent)
        if len(self.family_spouse) > 0:
            # This would need family data to determine number of children
            pass
        
        return themes


@dataclass
class Family:
    """Represents a family unit with parents and children"""
    id: str
    husband_id: Optional[str] = None
    wife_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    marriage_event: Optional[Event] = None
    divorce_event: Optional[Event] = None
    
    def get_child_count(self) -> int:
        """Get number of children for narrative purposes"""
        return len(self.children_ids)
    
    def is_large_family(self) -> bool:
        """Determine if this qualifies as a large family for storytelling"""
        return self.get_child_count() >= 8


class GEDCOMParser:
    """Main parser for GEDCOM files with story extraction focus"""
    
    def __init__(self):
        self.individuals: Dict[str, Individual] = {}
        self.families: Dict[str, Family] = {}
        self.current_entity = None
        self.current_entity_type = None
        self.current_event = None
        
    def parse_file(self, filepath: str) -> Dict:
        """Parse GEDCOM file and extract story elements"""
        with open(filepath, 'r', encoding='utf-8-sig') as file:
            lines = file.readlines()
        
        for line in lines:
            self._parse_line(line.strip())
        
        # Post-process to identify story themes
        story_data = self._extract_story_data()
        
        return story_data
    
    def _parse_line(self, line: str):
        """Parse a single GEDCOM line"""
        if not line:
            return
        
        # GEDCOM line format: LEVEL [XREF] TAG [VALUE]
        match = re.match(r'^(\d+)\s+(@\w+@\s+)?(\w+)(\s+(.*))?$', line)
        if not match:
            return
        
        level = int(match.group(1))
        xref = match.group(2).strip() if match.group(2) else None
        tag = match.group(3)
        value = match.group(5) if match.group(5) else None
        
        # Handle level 0 (new entity)
        if level == 0:
            self._save_current_entity()
            
            if xref and tag == "INDI":
                self.current_entity = Individual(id=xref)
                self.current_entity_type = "INDI"
            elif xref and tag == "FAM":
                self.current_entity = Family(id=xref)
                self.current_entity_type = "FAM"
            else:
                self.current_entity = None
                self.current_entity_type = None
        
        # Handle individual properties
        elif self.current_entity_type == "INDI" and level == 1:
            if tag == "NAME":
                self._parse_name(value)
            elif tag == "SEX":
                self.current_entity.sex = value
            elif tag in ["BIRT", "DEAT", "MARR", "IMMI", "EMIG", "OCCU", "EDUC", "MILI"]:
                self.current_event = Event(event_type=EventType(tag))
            elif tag == "FAMC":
                self.current_entity.family_child.append(value)
            elif tag == "FAMS":
                self.current_entity.family_spouse.append(value)
            elif tag == "NOTE":
                if value:
                    self.current_entity.notes.append(value)
        
        # Handle family properties
        elif self.current_entity_type == "FAM" and level == 1:
            if tag == "HUSB":
                self.current_entity.husband_id = value
            elif tag == "WIFE":
                self.current_entity.wife_id = value
            elif tag == "CHIL":
                self.current_entity.children_ids.append(value)
            elif tag == "MARR":
                self.current_event = Event(event_type=EventType.MARRIAGE)
            elif tag == "DIV":
                self.current_event = Event(event_type=EventType.DIVORCE)
        
        # Handle event properties
        elif self.current_event and level == 2:
            if tag == "DATE":
                self.current_event.date = value
            elif tag == "PLAC":
                self.current_event.location = Location(value)
            elif tag == "NOTE":
                self.current_event.description = value
        
        # Save completed events
        if level <= 1 and self.current_event:
            if self.current_entity_type == "INDI":
                self.current_entity.events.append(self.current_event)
            elif self.current_entity_type == "FAM":
                if self.current_event.event_type == EventType.MARRIAGE:
                    self.current_entity.marriage_event = self.current_event
                elif self.current_event.event_type == EventType.DIVORCE:
                    self.current_entity.divorce_event = self.current_event
            self.current_event = None
    
    def _parse_name(self, name_value: str):
        """Parse name into given names and surname"""
        if not name_value:
            return
        
        # GEDCOM format: Given Names /Surname/
        match = re.match(r'^([^/]*)\s*/([^/]*)/\s*(.*)$', name_value)
        if match:
            self.current_entity.given_names = match.group(1).strip()
            self.current_entity.surname = match.group(2).strip()
        else:
            # Handle names without slashes
            parts = name_value.split()
            if len(parts) > 1:
                self.current_entity.given_names = ' '.join(parts[:-1])
                self.current_entity.surname = parts[-1]
            else:
                self.current_entity.given_names = name_value
    
    def _save_current_entity(self):
        """Save the current entity to appropriate collection"""
        if self.current_entity:
            if self.current_entity_type == "INDI":
                self.individuals[self.current_entity.id] = self.current_entity
            elif self.current_entity_type == "FAM":
                self.families[self.current_entity.id] = self.current_entity
    
    def _extract_story_data(self) -> Dict:
        """Extract narrative elements from parsed data"""
        # Save any remaining entity
        self._save_current_entity()
        
        story_data = {
            "individuals": {},
            "families": {},
            "narrative_themes": [],
            "key_events": [],
            "geographic_journey": [],
            "statistics": {}
        }
        
        # Process individuals
        for ind_id, individual in self.individuals.items():
            ind_data = {
                "name": individual.get_full_name(),
                "lifespan": individual.get_lifespan(),
                "birth_year": individual.get_birth_year(),
                "death_year": individual.get_death_year(),
                "events": [],
                "themes": list(individual.get_story_themes())
            }
            
            # Add significant events
            for event in individual.events:
                event_data = {
                    "type": event.event_type.value,
                    "date": event.get_narrative_date(),
                    "year": event.get_year(),
                    "location": event.location.get_display_name() if event.location else None
                }
                ind_data["events"].append(event_data)
            
            story_data["individuals"][ind_id] = ind_data
        
        # Process families
        for fam_id, family in self.families.items():
            fam_data = {
                "size": family.get_child_count(),
                "is_large": family.is_large_family()
            }
            
            if family.marriage_event:
                fam_data["marriage"] = {
                    "date": family.marriage_event.get_narrative_date(),
                    "location": family.marriage_event.location.get_display_name() if family.marriage_event.location else None
                }
            
            story_data["families"][fam_id] = fam_data
        
        # Extract narrative themes
        all_themes = set()
        for individual in self.individuals.values():
            all_themes.update(individual.get_story_themes())
        story_data["narrative_themes"] = [theme.value for theme in all_themes]
        
        # Extract key events for timeline
        all_events = []
        for individual in self.individuals.values():
            for event in individual.events:
                if event.get_year():
                    all_events.append({
                        "person": individual.get_full_name(),
                        "type": event.event_type.value,
                        "year": event.get_year(),
                        "description": self._create_event_description(individual, event)
                    })
        
        # Sort events by year
        all_events.sort(key=lambda x: x["year"])
        story_data["key_events"] = all_events
        
        # Extract geographic journey
        locations = self._extract_migration_pattern()
        story_data["geographic_journey"] = locations
        
        # Calculate statistics
        story_data["statistics"] = self._calculate_statistics()
        
        return story_data
    
    def _create_event_description(self, individual: Individual, event: Event) -> str:
        """Create a narrative description for an event"""
        name = individual.get_full_name()
        
        descriptions = {
            EventType.BIRTH: f"{name} was born {event.get_narrative_date()}",
            EventType.DEATH: f"{name} passed away {event.get_narrative_date()}",
            EventType.MARRIAGE: f"{name} married {event.get_narrative_date()}",
            EventType.IMMIGRATION: f"{name} immigrated {event.get_narrative_date()}",
            EventType.EMIGRATION: f"{name} emigrated {event.get_narrative_date()}",
            EventType.MILITARY: f"{name} served in the military",
            EventType.OCCUPATION: f"{name} worked as {event.description if event.description else 'unknown'}"
        }
        
        desc = descriptions.get(event.event_type, f"{name} experienced {event.event_type.value}")
        
        if event.location:
            desc += f" in {event.location.get_display_name()}"
        
        return desc
    
    def _extract_migration_pattern(self) -> List[Dict]:
        """Extract geographic movement patterns for narrative"""
        locations = []
        location_timeline = []
        
        # Collect all locations with dates
        for individual in self.individuals.values():
            for event in individual.events:
                if event.location and event.get_year():
                    location_timeline.append({
                        "year": event.get_year(),
                        "location": event.location,
                        "person": individual.get_full_name(),
                        "event_type": event.event_type.value
                    })
        
        # Sort by year
        location_timeline.sort(key=lambda x: x["year"])
        
        # Identify unique locations and movements
        seen_locations = set()
        for item in location_timeline:
            loc_key = item["location"].get_display_name()
            if loc_key not in seen_locations:
                seen_locations.add(loc_key)
                locations.append({
                    "location": loc_key,
                    "year": item["year"],
                    "significance": self._determine_location_significance(item)
                })
        
        return locations
    
    def _determine_location_significance(self, location_event: Dict) -> str:
        """Determine why a location is significant to the story"""
        event_type = location_event["event_type"]
        
        significance_map = {
            "BIRT": "birthplace",
            "DEAT": "final resting place",
            "MARR": "marriage location",
            "IMMI": "immigration destination",
            "EMIG": "emigration origin",
            "RESI": "residence"
        }
        
        return significance_map.get(event_type, "significant location")
    
    def _calculate_statistics(self) -> Dict:
        """Calculate interesting statistics for narrative color"""
        stats = {
            "total_individuals": len(self.individuals),
            "total_families": len(self.families),
            "generations": self._estimate_generations(),
            "average_lifespan": self._calculate_average_lifespan(),
            "average_children_per_family": self._calculate_average_children(),
            "most_common_locations": self._find_common_locations(),
            "date_range": self._calculate_date_range()
        }
        
        return stats
    
    def _estimate_generations(self) -> int:
        """Estimate number of generations in the tree"""
        # Simple estimation based on date range
        date_range = self._calculate_date_range()
        if date_range["earliest"] and date_range["latest"]:
            years = date_range["latest"] - date_range["earliest"]
            return max(1, years // 25)  # Assume 25 years per generation
        return 1
    
    def _calculate_average_lifespan(self) -> Optional[float]:
        """Calculate average lifespan for narrative context"""
        lifespans = []
        for individual in self.individuals.values():
            lifespan = individual.get_lifespan()
            if lifespan and lifespan > 0:
                lifespans.append(lifespan)
        
        if lifespans:
            return sum(lifespans) / len(lifespans)
        return None
    
    def _calculate_average_children(self) -> float:
        """Calculate average number of children per family"""
        if not self.families:
            return 0
        
        total_children = sum(family.get_child_count() for family in self.families.values())
        return total_children / len(self.families)
    
    def _find_common_locations(self) -> List[Tuple[str, int]]:
        """Find most common locations for geographic narrative"""
        location_counts = {}
        
        for individual in self.individuals.values():
            for event in individual.events:
                if event.location:
                    loc_name = event.location.get_display_name()
                    location_counts[loc_name] = location_counts.get(loc_name, 0) + 1
        
        # Sort by frequency
        sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_locations[:5]  # Top 5 locations
    
    def _calculate_date_range(self) -> Dict[str, Optional[int]]:
        """Calculate earliest and latest dates in the tree"""
        all_years = []
        
        for individual in self.individuals.values():
            for event in individual.events:
                year = event.get_year()
                if year:
                    all_years.append(year)
        
        if all_years:
            return {
                "earliest": min(all_years),
                "latest": max(all_years)
            }
        
        return {"earliest": None, "latest": None}


class StoryGenerator:
    """Generate narrative elements from parsed GEDCOM data"""
    
    def __init__(self, story_data: Dict):
        self.story_data = story_data
    
    def generate_opening_narrative(self) -> str:
        """Generate an opening paragraph for the documentary"""
        stats = self.story_data["statistics"]
        themes = self.story_data["narrative_themes"]
        
        # Build opening based on key statistics and themes
        if "immigration" in themes:
            return self._generate_immigration_opening()
        elif "military_service" in themes:
            return self._generate_military_opening()
        elif "large_family" in themes:
            return self._generate_large_family_opening()
        else:
            return self._generate_default_opening()
    
    def _generate_immigration_opening(self) -> str:
        """Generate opening for immigration-themed stories"""
        date_range = self.story_data["statistics"]["date_range"]
        locations = self.story_data["geographic_journey"]
        
        if locations and len(locations) > 1:
            origin = locations[0]["location"]
            destination = locations[-1]["location"]
            return (
                f"This is the story of a family's journey across continents and generations. "
                f"From {origin} to {destination}, they carried with them hopes, dreams, "
                f"and the determination to build a better life. Their courage would shape "
                f"the destiny of generations to come."
            )
        
        return "This is a story of courage, journey, and new beginnings."
    
    def _generate_military_opening(self) -> str:
        """Generate opening for military service stories"""
        return (
            "Throughout history, this family has answered the call to serve. "
            "From generation to generation, they have stood in defense of their nation, "
            "their sacrifices woven into the fabric of history. This is their story of "
            "duty, honor, and the price of freedom."
        )
    
    def _generate_large_family_opening(self) -> str:
        """Generate opening for large family stories"""
        avg_children = self.story_data["statistics"]["average_children_per_family"]
        return (
            f"In an era when large families were both a blessing and a necessity, "
            f"this family tree spread wide and strong. With an average of {avg_children:.1f} "
            f"children per generation, theirs is a story of resilience, love, and the "
            f"bonds that tie us together across time."
        )
    
    def _generate_default_opening(self) -> str:
        """Generate a default opening paragraph"""
        generations = self.story_data["statistics"]["generations"]
        date_range = self.story_data["statistics"]["date_range"]
        
        if date_range["earliest"] and date_range["latest"]:
            years_span = date_range["latest"] - date_range["earliest"]
            return (
                f"Across {generations} generations and {years_span} years, this family's "
                f"story unfolds like a tapestry woven with love, loss, triumph, and tradition. "
                f"From {date_range['earliest']} to {date_range['latest']}, each thread tells "
                f"a tale of lives lived, challenges overcome, and legacies left behind."
            )
        
        return (
            "Every family has a story. This is yours. A story of ordinary people living "
            "extraordinary lives, of connections that span generations, and of the "
            "enduring power of family."
        )


# Example usage
if __name__ == "__main__":
    # Example of how to use the parser
    parser = GEDCOMParser()
    
    # Parse a GEDCOM file
    # story_data = parser.parse_file("sample_family.ged")
    
    # Generate story elements
    # generator = StoryGenerator(story_data)
    # opening = generator.generate_opening_narrative()
    
    # print("Opening Narrative:")
    # print(opening)
    # print("\nStory Data:")
    # print(json.dumps(story_data, indent=2, default=str))
