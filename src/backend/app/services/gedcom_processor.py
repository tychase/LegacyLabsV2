"""
GEDCOM processing service
Integrates with the GEDCOM parser to process family history files
"""

import sys
import os
from typing import Dict, Any

# Add the project root to the path to import the GEDCOM parser
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from gedcom_parser import GEDCOMParser, StoryGenerator


async def process_gedcom_file(gedcom_content: str) -> Dict[str, Any]:
    """
    Process GEDCOM file content and extract story data
    
    Args:
        gedcom_content: The raw GEDCOM file content as a string
        
    Returns:
        Dictionary containing parsed data and narrative elements
    """
    try:
        # Save content to temporary file for parser
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ged', delete=False) as temp_file:
            temp_file.write(gedcom_content)
            temp_file_path = temp_file.name
        
        # Parse the GEDCOM file
        parser = GEDCOMParser()
        story_data = parser.parse_file(temp_file_path)
        
        # Generate opening narrative
        generator = StoryGenerator(story_data)
        opening_narrative = generator.generate_opening_narrative()
        
        # Add the opening narrative to the story data
        story_data['opening_narrative'] = opening_narrative
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Enhance the data with additional insights
        story_data['insights'] = generate_insights(story_data)
        
        return story_data
        
    except Exception as e:
        raise Exception(f"Failed to process GEDCOM file: {str(e)}")


def generate_insights(story_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate additional insights from the parsed data
    """
    insights = {}
    
    # Migration insights
    if story_data.get('geographic_journey'):
        journey = story_data['geographic_journey']
        if len(journey) > 1:
            insights['migration_distance'] = calculate_migration_span(journey)
            insights['settlement_pattern'] = analyze_settlement_pattern(journey)
    
    # Family insights
    stats = story_data.get('statistics', {})
    if stats.get('average_children_per_family'):
        avg_children = stats['average_children_per_family']
        if avg_children > 6:
            insights['family_size_note'] = "Large families were common in your ancestry"
        elif avg_children < 2:
            insights['family_size_note'] = "Your ancestors tended to have smaller families"
    
    # Longevity insights
    if stats.get('average_lifespan'):
        avg_lifespan = stats['average_lifespan']
        if avg_lifespan > 70:
            insights['longevity_note'] = "Your family has a history of longevity"
        elif avg_lifespan < 50:
            insights['longevity_note'] = "Life was harder for earlier generations"
    
    # Time span insights
    date_range = stats.get('date_range', {})
    if date_range.get('earliest') and date_range.get('latest'):
        span = date_range['latest'] - date_range['earliest']
        insights['time_span'] = f"Your family history spans {span} years"
        
        # Historical context
        insights['historical_events'] = get_historical_context(
            date_range['earliest'], 
            date_range['latest']
        )
    
    return insights


def calculate_migration_span(journey: list) -> str:
    """
    Calculate the geographic span of migration
    """
    locations = [j['location'] for j in journey]
    if len(set(locations)) > 3:
        return "extensive - across multiple regions"
    elif len(set(locations)) > 1:
        return "moderate - within a general region"
    else:
        return "minimal - largely settled in one area"


def analyze_settlement_pattern(journey: list) -> str:
    """
    Analyze the pattern of settlement
    """
    # Simple analysis based on timing
    if len(journey) > 0:
        years = [j['year'] for j in journey if j.get('year')]
        if years:
            span = max(years) - min(years)
            if span > 100:
                return "gradual migration over generations"
            elif span > 50:
                return "steady movement over decades"
            else:
                return "rapid relocation"
    return "stable settlement"


def get_historical_context(earliest_year: int, latest_year: int) -> list:
    """
    Get relevant historical events for the time period
    """
    events = []
    
    # Major historical events by period
    historical_events = [
        (1776, 1783, "American Revolution"),
        (1861, 1865, "American Civil War"),
        (1914, 1918, "World War I"),
        (1929, 1939, "Great Depression"),
        (1939, 1945, "World War II"),
        (1845, 1852, "Irish Potato Famine"),
        (1849, 1855, "California Gold Rush"),
        (1892, 1954, "Ellis Island Immigration"),
    ]
    
    for start, end, event in historical_events:
        if start <= latest_year and end >= earliest_year:
            events.append(event)
    
    return events
