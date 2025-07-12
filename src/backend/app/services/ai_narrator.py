"""
AI Narrator Service
Generates compelling narratives using Claude or GPT-4
"""

import os
from typing import Dict, Any, List
import anthropic
import openai
from elevenlabs import generate, set_api_key, voices, save
import asyncio
import tempfile
import uuid

from app.core.config import settings
from app.utils.s3 import upload_file_to_s3


# Initialize AI clients
anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
openai.api_key = settings.OPENAI_API_KEY
set_api_key(settings.ELEVENLABS_API_KEY)


async def generate_narration_script(parsed_data: Dict[str, Any], title: str) -> Dict[str, Any]:
    """
    Generate a professional documentary narration script using AI
    """
    
    # Build comprehensive prompt
    prompt = build_narration_prompt(parsed_data, title)
    
    # Try Claude first, fallback to GPT-4
    try:
        script_data = await generate_with_claude(prompt)
    except Exception as e:
        print(f"Claude generation failed: {e}, falling back to GPT-4")
        script_data = await generate_with_gpt4(prompt)
    
    # Parse and structure the script
    structured_script = parse_script_response(script_data)
    
    # Select appropriate voice
    voice_id = select_narrator_voice(parsed_data, structured_script)
    
    return {
        "script": structured_script["full_text"],
        "segments": structured_script["segments"],
        "full_text": structured_script["full_text"],
        "voice_id": voice_id,
        "total_duration": structured_script["estimated_duration"]
    }


def build_narration_prompt(parsed_data: Dict[str, Any], title: str) -> str:
    """Build comprehensive prompt for AI narrator"""
    
    # Extract key information
    stats = parsed_data.get('statistics', {})
    themes = parsed_data.get('narrative_themes', [])
    journey = parsed_data.get('geographic_journey', [])
    events = parsed_data.get('key_events', [])[:10]  # Top 10 events
    insights = parsed_data.get('insights', {})
    individuals = list(parsed_data.get('individuals', {}).values())[:5]  # Key individuals
    
    prompt = f"""You are a professional documentary narrator creating a script for a family history documentary titled "{title}".

FAMILY DATA:
- Total individuals: {stats.get('total_individuals', 'Unknown')}
- Generations: {stats.get('generations', 'Unknown')}
- Time span: {stats.get('date_range', {}).get('earliest', 'Unknown')} to {stats.get('date_range', {}).get('latest', 'Unknown')}
- Average lifespan: {stats.get('average_lifespan', 'Unknown')}
- Average children per family: {stats.get('average_children_per_family', 'Unknown')}

NARRATIVE THEMES:
{', '.join(themes) if themes else 'General family history'}

GEOGRAPHIC JOURNEY:
{format_journey_for_prompt(journey)}

KEY EVENTS:
{format_events_for_prompt(events)}

KEY INDIVIDUALS:
{format_individuals_for_prompt(individuals)}

INSIGHTS:
{format_insights_for_prompt(insights)}

INSTRUCTIONS:
1. Create a compelling 5-7 minute documentary narration (750-1000 words)
2. Structure the narration with clear segments:
   - Opening: Hook the viewer with an emotional or intriguing statement
   - Family Overview: Introduce the scope and scale of the family
   - Geographic Journey: Tell the story of migration and settlement
   - Key Moments: Highlight 3-5 pivotal events or people
   - Themes: Weave in the narrative themes naturally
   - Legacy: Conclude with the family's lasting impact
3. Use a warm, professional documentary tone (think Ken Burns style)
4. Include specific dates, places, and names where provided
5. Create emotional resonance without being overly sentimental
6. Use vivid language that paints pictures
7. Maintain historical accuracy while telling a compelling story

Format your response as:
[SEGMENT: Opening]
[Duration: X seconds]
[Text of opening segment]

[SEGMENT: Family Overview]
[Duration: X seconds]
[Text of family overview segment]

[Continue for all segments...]

Remember: This is a treasured family keepsake. Make every word count."""
    
    return prompt


def format_journey_for_prompt(journey: List[Dict]) -> str:
    """Format geographic journey for prompt"""
    if not journey:
        return "No significant geographic movements recorded"
    
    lines = []
    for stop in journey[:5]:  # Top 5 locations
        line = f"- {stop['location']} ({stop['year']}): {stop['significance']}"
        lines.append(line)
    
    return "\n".join(lines)


def format_events_for_prompt(events: List[Dict]) -> str:
    """Format key events for prompt"""
    if not events:
        return "No specific events recorded"
    
    lines = []
    for event in events:
        line = f"- {event['year']}: {event['description']}"
        lines.append(line)
    
    return "\n".join(lines)


def format_individuals_for_prompt(individuals: List[Dict]) -> str:
    """Format key individuals for prompt"""
    if not individuals:
        return "No detailed individual records"
    
    lines = []
    for person in individuals:
        line = f"- {person['name']}"
        if person.get('lifespan'):
            line += f" (lived {person['lifespan']} years)"
        if person.get('birth_year') and person.get('death_year'):
            line += f" [{person['birth_year']}-{person['death_year']}]"
        lines.append(line)
    
    return "\n".join(lines)


def format_insights_for_prompt(insights: Dict) -> str:
    """Format insights for prompt"""
    if not insights:
        return "No additional insights"
    
    lines = []
    for key, value in insights.items():
        if isinstance(value, list):
            lines.append(f"- {key}: {', '.join(value)}")
        else:
            lines.append(f"- {key}: {value}")
    
    return "\n".join(lines)


async def generate_with_claude(prompt: str) -> str:
    """Generate script using Claude"""
    
    response = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
    )
    
    return response.content[0].text


async def generate_with_gpt4(prompt: str) -> str:
    """Generate script using GPT-4"""
    
    response = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional documentary narrator specializing in family history documentaries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
    )
    
    return response.choices[0].message.content


def parse_script_response(script_text: str) -> Dict[str, Any]:
    """Parse the AI-generated script into structured segments"""
    
    segments = []
    current_segment = None
    full_text_parts = []
    
    lines = script_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('[SEGMENT:'):
            # Save previous segment if exists
            if current_segment and current_segment.get('text'):
                segments.append(current_segment)
                full_text_parts.append(current_segment['text'])
            
            # Start new segment
            segment_type = line.replace('[SEGMENT:', '').replace(']', '').strip()
            current_segment = {
                'type': segment_type.lower().replace(' ', '_'),
                'title': segment_type,
                'text': '',
                'duration': 10  # Default duration
            }
        
        elif line.startswith('[Duration:'):
            if current_segment:
                duration_str = line.replace('[Duration:', '').replace(']', '').strip()
                try:
                    current_segment['duration'] = int(duration_str.replace(' seconds', ''))
                except:
                    pass
        
        elif line and current_segment:
            # Add to current segment text
            if current_segment['text']:
                current_segment['text'] += ' '
            current_segment['text'] += line
    
    # Add final segment
    if current_segment and current_segment.get('text'):
        segments.append(current_segment)
        full_text_parts.append(current_segment['text'])
    
    # If no segments found, treat entire text as one segment
    if not segments:
        segments = [{
            'type': 'full_narration',
            'title': 'Full Narration',
            'text': script_text,
            'duration': len(script_text.split()) // 2  # Rough estimate
        }]
        full_text_parts = [script_text]
    
    return {
        'segments': segments,
        'full_text': '\n\n'.join(full_text_parts),
        'estimated_duration': sum(seg['duration'] for seg in segments)
    }


def select_narrator_voice(parsed_data: Dict[str, Any], script_data: Dict[str, Any]) -> str:
    """Select appropriate narrator voice based on content"""
    
    # Available ElevenLabs voices (you would configure these)
    voices = {
        "documentary_male": "21m00Tcm4TlvDq8ikWAM",  # Rachel (placeholder)
        "documentary_female": "EXAVITQu4vr4xnSDxMaL",  # Bella
        "warm_grandfather": "VR6AewLTigWG4xSOukaG",  # Arnold
        "gentle_grandmother": "pNInz6obpgDQGcFmaJgB",  # Dorothy
    }
    
    # Simple selection logic (could be more sophisticated)
    themes = parsed_data.get('narrative_themes', [])
    
    if 'military_service' in themes:
        return voices["documentary_male"]
    elif 'immigration' in themes:
        return voices["warm_grandfather"]
    elif any(theme in themes for theme in ['large_family', 'family_business']):
        return voices["gentle_grandmother"]
    else:
        # Default to standard documentary voice
        return voices["documentary_female"]


async def generate_voice_over(script: str, voice_id: str) -> Dict[str, Any]:
    """
    Generate voice-over audio using ElevenLabs
    """
    
    try:
        # Generate audio
        audio = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: generate(
                text=script,
                voice=voice_id,
                model="eleven_monolingual_v1"
            )
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            save(audio, temp_file.name)
            temp_path = temp_file.name
        
        # Upload to S3
        audio_filename = f"narration/{uuid.uuid4()}.mp3"
        audio_url = await upload_file_to_s3(
            file_path=temp_path,
            s3_key=audio_filename,
            content_type="audio/mpeg"
        )
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Calculate duration (approximate based on word count)
        word_count = len(script.split())
        duration = int((word_count / 150) * 60)  # 150 words per minute average
        
        return {
            "audio_url": audio_url,
            "duration": duration,
            "word_count": word_count,
            "voice_id": voice_id
        }
        
    except Exception as e:
        print(f"Error generating voice-over: {str(e)}")
        # Fallback to mock data for development
        return await generate_mock_voice_over(script, voice_id)


async def generate_mock_voice_over(script: str, voice_id: str) -> Dict[str, Any]:
    """Generate mock voice-over data for development"""
    
    word_count = len(script.split())
    duration = int((word_count / 150) * 60)
    
    return {
        "audio_url": f"https://{settings.S3_BUCKET_NAME}.s3.amazonaws.com/mock/narration.mp3",
        "duration": duration,
        "word_count": word_count,
        "voice_id": voice_id
    }


# Additional helper functions for enhancing narratives
async def enhance_with_historical_context(script: str, time_period: str) -> str:
    """Add historical context to the narrative"""
    
    historical_events = {
        "1800-1850": ["Industrial Revolution", "Westward expansion", "Gold Rush"],
        "1850-1900": ["Civil War", "Reconstruction", "Immigration wave"],
        "1900-1950": ["World Wars", "Great Depression", "Technological revolution"],
        "1950-2000": ["Civil Rights", "Space Age", "Digital revolution"]
    }
    
    # This would be enhanced with AI to weave in relevant historical context
    return script


async def add_emotional_depth(script: str, themes: List[str]) -> str:
    """Add emotional depth to the narrative based on themes"""
    
    emotional_elements = {
        "immigration": "hope, courage, sacrifice, new beginnings",
        "military_service": "duty, honor, sacrifice, patriotism",
        "large_family": "love, chaos, support, togetherness",
        "tragedy": "resilience, strength, healing, memory",
        "success": "determination, hard work, achievement, legacy"
    }
    
    # This would use AI to enhance emotional resonance
    return script
