"""
Video generation service
Orchestrates the creation of documentary videos from parsed GEDCOM data
"""

import asyncio
import json
from typing import Dict, Any, List
import uuid
from datetime import datetime

from app.core.config import settings
from app.services.ai_narrator import generate_narration_script, generate_voice_over
from app.services.visual_generator import generate_visual_scenes
from app.services.video_assembler import assemble_final_video
from app.utils.s3 import upload_file_to_s3


async def generate_documentary(
    project_id: int,
    parsed_data: Dict[str, Any],
    title: str
) -> Dict[str, Any]:
    """
    Generate a complete documentary video from parsed GEDCOM data
    
    Returns:
        Dictionary containing video_url, thumbnail_url, transcript, and duration
    """
    try:
        # Step 1: Generate narration script
        print(f"Generating narration script for project {project_id}...")
        narration_script = await generate_narration_script(parsed_data, title)
        
        # Step 2: Generate voice-over audio
        print(f"Generating voice-over for project {project_id}...")
        voice_over_data = await generate_voice_over(
            script=narration_script['script'],
            voice_id=narration_script.get('voice_id', 'documentary_male')
        )
        
        # Step 3: Generate visual scenes
        print(f"Generating visual scenes for project {project_id}...")
        visual_scenes = await generate_visual_scenes(
            parsed_data=parsed_data,
            script_segments=narration_script['segments']
        )
        
        # Step 4: Assemble final video
        print(f"Assembling final video for project {project_id}...")
        video_data = await assemble_final_video(
            voice_over_url=voice_over_data['audio_url'],
            visual_scenes=visual_scenes,
            project_title=title,
            duration=voice_over_data['duration']
        )
        
        # Step 5: Generate thumbnail
        thumbnail_url = visual_scenes[0]['thumbnail_url'] if visual_scenes else None
        
        return {
            "video_url": video_data['video_url'],
            "thumbnail_url": thumbnail_url,
            "transcript": narration_script['full_text'],
            "duration": video_data['duration']
        }
        
    except Exception as e:
        print(f"Error generating documentary for project {project_id}: {str(e)}")
        raise


async def generate_narration_script(parsed_data: Dict[str, Any], title: str) -> Dict[str, Any]:
    """
    Generate the narration script using AI
    
    This is a simplified version - in production, this would call
    Claude or GPT-4 to generate a compelling narrative
    """
    # Extract key information
    stats = parsed_data.get('statistics', {})
    themes = parsed_data.get('narrative_themes', [])
    journey = parsed_data.get('geographic_journey', [])
    insights = parsed_data.get('insights', {})
    opening = parsed_data.get('opening_narrative', '')
    
    # Build script segments
    segments = []
    
    # Opening segment
    segments.append({
        "type": "opening",
        "text": opening or f"This is the story of {title}.",
        "duration": 8
    })
    
    # Family overview segment
    family_text = build_family_overview(stats, insights)
    if family_text:
        segments.append({
            "type": "family_overview",
            "text": family_text,
            "duration": 12
        })
    
    # Geographic journey segment
    if journey:
        journey_text = build_journey_narrative(journey)
        segments.append({
            "type": "geographic_journey",
            "text": journey_text,
            "duration": 15
        })
    
    # Key events timeline
    events = parsed_data.get('key_events', [])
    if events:
        events_text = build_events_narrative(events[:5])  # Top 5 events
        segments.append({
            "type": "timeline",
            "text": events_text,
            "duration": 20
        })
    
    # Themes and legacy
    if themes:
        themes_text = build_themes_narrative(themes, insights)
        segments.append({
            "type": "themes",
            "text": themes_text,
            "duration": 10
        })
    
    # Closing segment
    closing_text = build_closing_narrative(title, stats)
    segments.append({
        "type": "closing",
        "text": closing_text,
        "duration": 8
    })
    
    # Combine all segments
    full_text = "\n\n".join([seg['text'] for seg in segments])
    
    return {
        "script": full_text,
        "segments": segments,
        "full_text": full_text,
        "voice_id": "documentary_male",
        "total_duration": sum(seg['duration'] for seg in segments)
    }


def build_family_overview(stats: Dict, insights: Dict) -> str:
    """Build the family overview narrative"""
    parts = []
    
    if stats.get('total_individuals'):
        parts.append(f"This family tree encompasses {stats['total_individuals']} individuals")
    
    if stats.get('generations'):
        parts.append(f"spanning {stats['generations']} generations")
    
    if insights.get('time_span'):
        parts.append(insights['time_span'])
    
    if not parts:
        return ""
    
    text = ", ".join(parts) + "."
    
    if insights.get('family_size_note'):
        text += f" {insights['family_size_note']}."
    
    return text


def build_journey_narrative(journey: List[Dict]) -> str:
    """Build the geographic journey narrative"""
    if not journey:
        return ""
    
    if len(journey) == 1:
        return f"The family's roots are deeply planted in {journey[0]['location']}."
    
    origin = journey[0]
    destination = journey[-1]
    
    text = f"The family's journey began in {origin['location']}"
    
    if origin.get('year'):
        text += f" around {origin['year']}"
    
    text += f" and led them to {destination['location']}"
    
    if destination.get('year'):
        text += f" by {destination['year']}"
    
    text += "."
    
    if len(journey) > 2:
        text += f" Along the way, they passed through {len(journey) - 2} other locations, each adding to their story."
    
    return text


def build_events_narrative(events: List[Dict]) -> str:
    """Build narrative for key events"""
    if not events:
        return ""
    
    text = "Key moments shaped this family's history. "
    
    event_texts = []
    for event in events:
        event_texts.append(event.get('description', ''))
    
    text += " ".join(event_texts)
    
    return text


def build_themes_narrative(themes: List[str], insights: Dict) -> str:
    """Build narrative around family themes"""
    theme_narratives = {
        "immigration": "This is a story of courage and new beginnings, of leaving the familiar behind in search of opportunity.",
        "military_service": "Service and sacrifice run through this family's veins, with multiple generations answering the call to duty.",
        "large_family": "Family bonds were strong and numerous, creating a rich tapestry of relationships.",
        "long_life": "Blessed with longevity, many family members lived to see multiple generations flourish.",
        "early_death": "Life's fragility touched this family, making each moment more precious."
    }
    
    parts = []
    for theme in themes:
        if theme in theme_narratives:
            parts.append(theme_narratives[theme])
    
    return " ".join(parts) if parts else ""


def build_closing_narrative(title: str, stats: Dict) -> str:
    """Build the closing narrative"""
    return (
        f"The story of {title} continues to unfold. "
        f"From the {stats.get('total_individuals', 'many')} lives documented here, "
        f"we see not just names and dates, but a legacy of love, perseverance, and family. "
        f"This is your heritage. This is your story."
    )


# Placeholder for actual implementation
async def generate_voice_over(script: str, voice_id: str) -> Dict[str, Any]:
    """
    Generate voice-over using ElevenLabs or similar service
    In production, this would actually call the API
    """
    # Simulate processing time
    await asyncio.sleep(2)
    
    # For now, return mock data
    audio_filename = f"audio_{uuid.uuid4()}.mp3"
    audio_url = f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/audio/{audio_filename}"
    
    # Estimate duration based on script length (roughly 150 words per minute)
    word_count = len(script.split())
    duration = int((word_count / 150) * 60)
    
    return {
        "audio_url": audio_url,
        "duration": duration,
        "word_count": word_count
    }
