"""
Visual scene generator service
Generates or selects appropriate visuals for each segment of the documentary
"""

import asyncio
import json
from typing import Dict, Any, List
import random
from datetime import datetime

from app.core.config import settings
from app.services.stock_footage import get_stock_footage
from app.services.ai_image_generator import generate_ai_images
from app.utils.s3 import upload_file_to_s3


async def generate_visual_scenes(
    parsed_data: Dict[str, Any],
    script_segments: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate visual scenes for each script segment
    
    Returns:
        List of visual scene dictionaries with urls and metadata
    """
    visual_scenes = []
    
    # Extract context from parsed data
    context = extract_visual_context(parsed_data)
    
    for segment in script_segments:
        scene = await generate_scene_for_segment(segment, context)
        visual_scenes.append(scene)
    
    return visual_scenes


def extract_visual_context(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract visual context from parsed GEDCOM data"""
    context = {
        "time_period": determine_primary_time_period(parsed_data),
        "locations": extract_primary_locations(parsed_data),
        "themes": parsed_data.get("narrative_themes", []),
        "ethnic_background": infer_ethnic_background(parsed_data),
        "key_events": parsed_data.get("key_events", [])
    }
    return context


def determine_primary_time_period(parsed_data: Dict[str, Any]) -> str:
    """Determine the primary time period for visual selection"""
    stats = parsed_data.get("statistics", {})
    date_range = stats.get("date_range", {})
    
    if not date_range.get("earliest"):
        return "modern"
    
    earliest = date_range["earliest"]
    
    if earliest < 1800:
        return "colonial"
    elif earliest < 1850:
        return "early_1800s"
    elif earliest < 1900:
        return "late_1800s"
    elif earliest < 1950:
        return "early_1900s"
    elif earliest < 2000:
        return "mid_1900s"
    else:
        return "modern"


def extract_primary_locations(parsed_data: Dict[str, Any]) -> List[str]:
    """Extract primary locations for visual context"""
    journey = parsed_data.get("geographic_journey", [])
    locations = []
    
    for stop in journey[:5]:  # Top 5 locations
        if stop.get("location"):
            locations.append(stop["location"])
    
    # Also get most common locations
    stats = parsed_data.get("statistics", {})
    common_locs = stats.get("most_common_locations", [])
    for loc, count in common_locs[:3]:
        if loc not in locations:
            locations.append(loc)
    
    return locations


def infer_ethnic_background(parsed_data: Dict[str, Any]) -> List[str]:
    """Infer ethnic background from locations and names"""
    backgrounds = []
    
    # Analyze locations
    locations = extract_primary_locations(parsed_data)
    for loc in locations:
        loc_lower = loc.lower()
        if any(country in loc_lower for country in ["ireland", "irish"]):
            backgrounds.append("irish")
        elif any(country in loc_lower for country in ["germany", "german", "bavaria"]):
            backgrounds.append("german")
        elif any(country in loc_lower for country in ["italy", "italian"]):
            backgrounds.append("italian")
        elif any(country in loc_lower for country in ["england", "english", "britain"]):
            backgrounds.append("british")
        elif any(country in loc_lower for country in ["scotland", "scottish"]):
            backgrounds.append("scottish")
        elif any(country in loc_lower for country in ["poland", "polish"]):
            backgrounds.append("polish")
        elif any(country in loc_lower for country in ["mexico", "mexican"]):
            backgrounds.append("mexican")
        elif any(country in loc_lower for country in ["china", "chinese"]):
            backgrounds.append("chinese")
        elif any(country in loc_lower for country in ["africa", "african"]):
            backgrounds.append("african")
    
    return list(set(backgrounds))


async def generate_scene_for_segment(
    segment: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate appropriate visual scene for a script segment"""
    
    segment_type = segment.get("type", "general")
    duration = segment.get("duration", 10)
    
    # Determine visual strategy based on segment type
    if segment_type == "opening":
        scene = await generate_opening_scene(context)
    elif segment_type == "family_overview":
        scene = await generate_family_tree_scene(context)
    elif segment_type == "geographic_journey":
        scene = await generate_map_scene(context)
    elif segment_type == "timeline":
        scene = await generate_timeline_scene(context)
    elif segment_type == "themes":
        scene = await generate_thematic_scene(segment, context)
    else:
        scene = await generate_generic_scene(context)
    
    scene["duration"] = duration
    scene["segment_type"] = segment_type
    
    return scene


async def generate_opening_scene(context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate an compelling opening visual"""
    
    # Try to get period-appropriate establishing shot
    time_period = context.get("time_period", "modern")
    locations = context.get("locations", [])
    
    # Build search criteria for stock footage
    search_tags = [time_period, "establishing shot", "vintage", "family"]
    if locations:
        search_tags.append(locations[0].split(",")[0])  # Primary location
    
    # Get stock footage
    stock_options = await get_stock_footage(
        tags=search_tags,
        era=time_period,
        limit=5
    )
    
    if stock_options:
        selected = stock_options[0]
        return {
            "type": "stock_footage",
            "url": selected["file_url"],
            "thumbnail_url": selected["thumbnail_url"],
            "description": "Opening establishing shot",
            "effects": ["slow_zoom_in", "vintage_filter", "soft_vignette"]
        }
    
    # Fallback to AI generation
    prompt = build_ai_prompt_for_opening(context)
    ai_image = await generate_ai_images([prompt])
    
    return {
        "type": "ai_generated",
        "url": ai_image[0]["url"],
        "thumbnail_url": ai_image[0]["url"],
        "description": "AI-generated opening scene",
        "effects": ["ken_burns", "vintage_filter"]
    }


async def generate_family_tree_scene(context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a family tree visualization"""
    
    # This would integrate with a family tree visualization service
    # For now, return a template
    return {
        "type": "animated_graphic",
        "template": "family_tree_bloom",
        "data_source": "parsed_gedcom",
        "url": "https://legacylabs-assets.s3.amazonaws.com/templates/family_tree_animated.mp4",
        "thumbnail_url": "https://legacylabs-assets.s3.amazonaws.com/templates/family_tree_thumb.jpg",
        "description": "Animated family tree visualization",
        "effects": ["fade_in", "gentle_motion"]
    }


async def generate_map_scene(context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a map showing geographic journey"""
    
    locations = context.get("locations", [])
    
    if len(locations) > 1:
        # Generate animated journey map
        return {
            "type": "animated_map",
            "template": "journey_map",
            "locations": locations,
            "url": "https://legacylabs-assets.s3.amazonaws.com/templates/journey_map.mp4",
            "thumbnail_url": "https://legacylabs-assets.s3.amazonaws.com/templates/journey_map_thumb.jpg",
            "description": "Animated journey map",
            "effects": ["path_animation", "location_markers"]
        }
    else:
        # Single location map
        return {
            "type": "static_map",
            "template": "location_map",
            "location": locations[0] if locations else "Unknown",
            "url": "https://legacylabs-assets.s3.amazonaws.com/templates/location_map.jpg",
            "thumbnail_url": "https://legacylabs-assets.s3.amazonaws.com/templates/location_map_thumb.jpg",
            "description": "Location map",
            "effects": ["slow_zoom", "highlight_pulse"]
        }


async def generate_timeline_scene(context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a timeline visualization"""
    
    events = context.get("key_events", [])[:5]  # Top 5 events
    
    return {
        "type": "animated_timeline",
        "template": "historical_timeline",
        "events": events,
        "url": "https://legacylabs-assets.s3.amazonaws.com/templates/timeline.mp4",
        "thumbnail_url": "https://legacylabs-assets.s3.amazonaws.com/templates/timeline_thumb.jpg",
        "description": "Historical timeline",
        "effects": ["sequential_reveal", "date_highlights"]
    }


async def generate_thematic_scene(segment: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate scene based on narrative themes"""
    
    themes = context.get("themes", [])
    time_period = context.get("time_period", "modern")
    
    # Map themes to visual concepts
    theme_visuals = {
        "immigration": ["ship", "ellis island", "voyage", "new land"],
        "military_service": ["uniform", "flag", "medals", "service"],
        "large_family": ["gathering", "reunion", "children", "generations"],
        "farming": ["farmland", "harvest", "rural", "agriculture"],
        "urban": ["city", "industry", "streets", "buildings"]
    }
    
    search_tags = [time_period]
    for theme in themes:
        if theme in theme_visuals:
            search_tags.extend(theme_visuals[theme])
    
    # Get appropriate stock footage
    stock_options = await get_stock_footage(
        tags=search_tags,
        era=time_period,
        theme=themes[0] if themes else "family",
        limit=3
    )
    
    if stock_options:
        selected = stock_options[0]
        return {
            "type": "stock_footage",
            "url": selected["file_url"],
            "thumbnail_url": selected["thumbnail_url"],
            "description": f"Thematic scene: {', '.join(themes)}",
            "effects": ["cross_dissolve", "emotional_color_grade"]
        }
    
    # Fallback to generic
    return await generate_generic_scene(context)


async def generate_generic_scene(context: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a generic period-appropriate scene"""
    
    time_period = context.get("time_period", "modern")
    
    # Generic family/heritage visuals
    search_tags = [time_period, "family", "heritage", "vintage", "memories"]
    
    stock_options = await get_stock_footage(
        tags=search_tags,
        era=time_period,
        limit=5
    )
    
    if stock_options:
        selected = random.choice(stock_options)
        return {
            "type": "stock_footage",
            "url": selected["file_url"],
            "thumbnail_url": selected["thumbnail_url"],
            "description": "Period-appropriate scene",
            "effects": ["subtle_motion", "film_grain", "nostalgic_tone"]
        }
    
    # Ultimate fallback
    return {
        "type": "placeholder",
        "url": "https://legacylabs-assets.s3.amazonaws.com/placeholders/vintage_family.jpg",
        "thumbnail_url": "https://legacylabs-assets.s3.amazonaws.com/placeholders/vintage_family_thumb.jpg",
        "description": "Vintage family photograph",
        "effects": ["ken_burns", "sepia_tone"]
    }


def build_ai_prompt_for_opening(context: Dict[str, Any]) -> str:
    """Build AI image generation prompt for opening scene"""
    
    time_period = context.get("time_period", "modern")
    locations = context.get("locations", [])
    backgrounds = context.get("ethnic_background", [])
    
    # Map time periods to visual styles
    period_styles = {
        "colonial": "colonial era painting style, 1700s aesthetic",
        "early_1800s": "19th century daguerreotype style, sepia toned",
        "late_1800s": "Victorian era photography, vintage portrait",
        "early_1900s": "early 20th century photograph, slightly faded",
        "mid_1900s": "mid-century photograph, color but nostalgic",
        "modern": "contemporary but timeless photographic style"
    }
    
    style = period_styles.get(time_period, "vintage photographic style")
    
    prompt = f"A beautiful, emotional establishing shot in {style}. "
    
    if locations:
        location = locations[0].split(",")[0]
        prompt += f"Scene depicts {location} during the {time_period.replace('_', ' ')}. "
    
    prompt += "Cinematic composition, documentary quality, historical accuracy, emotional resonance. "
    prompt += "No people in frame, focus on location and atmosphere."
    
    return prompt


# Mock service functions (would be replaced with actual implementations)
async def get_stock_footage(tags: List[str], era: str = None, theme: str = None, limit: int = 5) -> List[Dict]:
    """Mock function to get stock footage - would query actual database"""
    await asyncio.sleep(0.1)  # Simulate API call
    
    # Return mock data
    return [
        {
            "id": f"stock_{i}",
            "file_url": f"https://legacylabs-assets.s3.amazonaws.com/stock/video_{i}.mp4",
            "thumbnail_url": f"https://legacylabs-assets.s3.amazonaws.com/stock/thumb_{i}.jpg",
            "tags": tags,
            "era": era,
            "duration": 15
        }
        for i in range(min(3, limit))
    ]


async def generate_ai_images(prompts: List[str]) -> List[Dict]:
    """Mock function for AI image generation - would call DALL-E or similar"""
    await asyncio.sleep(0.5)  # Simulate API call
    
    return [
        {
            "url": f"https://legacylabs-assets.s3.amazonaws.com/ai/generated_{i}.jpg",
            "prompt": prompt
        }
        for i, prompt in enumerate(prompts)
    ]
