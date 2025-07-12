"""
Video assembly service
Combines audio narration, visual scenes, and effects into final documentary
"""

import asyncio
import os
import tempfile
import uuid
from typing import Dict, Any, List
import subprocess
import json

from app.core.config import settings
from app.utils.s3 import upload_file_to_s3, download_file_from_s3


async def assemble_final_video(
    voice_over_url: str,
    visual_scenes: List[Dict[str, Any]],
    project_title: str,
    duration: int
) -> Dict[str, Any]:
    """
    Assemble the final documentary video
    
    Returns:
        Dictionary containing video_url and duration
    """
    
    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Download voice-over audio
            audio_path = os.path.join(temp_dir, "narration.mp3")
            await download_file_from_s3(voice_over_url, audio_path)
            
            # Download visual assets
            visual_paths = await download_visual_assets(visual_scenes, temp_dir)
            
            # Create video timeline configuration
            timeline_config = create_timeline_config(
                visual_scenes=visual_scenes,
                visual_paths=visual_paths,
                audio_duration=duration
            )
            
            # Generate video using FFmpeg
            output_path = os.path.join(temp_dir, "documentary.mp4")
            await generate_video_ffmpeg(
                timeline_config=timeline_config,
                audio_path=audio_path,
                output_path=output_path,
                title=project_title
            )
            
            # Upload final video to S3
            video_filename = f"documentaries/{uuid.uuid4()}.mp4"
            video_url = await upload_file_to_s3(
                file_path=output_path,
                s3_key=video_filename,
                content_type="video/mp4"
            )
            
            # Get actual video duration
            actual_duration = get_video_duration(output_path)
            
            return {
                "video_url": video_url,
                "duration": actual_duration
            }
            
        except Exception as e:
            print(f"Error assembling video: {str(e)}")
            raise


async def download_visual_assets(scenes: List[Dict], temp_dir: str) -> Dict[str, str]:
    """Download all visual assets to temporary directory"""
    visual_paths = {}
    
    for i, scene in enumerate(scenes):
        if scene.get("url"):
            extension = get_file_extension(scene["url"])
            filename = f"scene_{i}.{extension}"
            local_path = os.path.join(temp_dir, filename)
            
            # Download file
            await download_file_from_s3(scene["url"], local_path)
            visual_paths[i] = local_path
    
    return visual_paths


def create_timeline_config(
    visual_scenes: List[Dict],
    visual_paths: Dict[int, str],
    audio_duration: int
) -> Dict[str, Any]:
    """Create timeline configuration for video assembly"""
    
    timeline = {
        "duration": audio_duration,
        "resolution": settings.VIDEO_RESOLUTION,
        "fps": settings.VIDEO_FPS,
        "scenes": []
    }
    
    current_time = 0
    
    for i, scene in enumerate(visual_scenes):
        scene_duration = scene.get("duration", 10)
        
        scene_config = {
            "index": i,
            "path": visual_paths.get(i),
            "start_time": current_time,
            "duration": scene_duration,
            "effects": scene.get("effects", []),
            "type": scene.get("type", "image")
        }
        
        timeline["scenes"].append(scene_config)
        current_time += scene_duration
    
    return timeline


async def generate_video_ffmpeg(
    timeline_config: Dict,
    audio_path: str,
    output_path: str,
    title: str
) -> None:
    """Generate video using FFmpeg"""
    
    # Create filter complex for all scenes
    filter_complex = build_filter_complex(timeline_config)
    
    # Build FFmpeg command
    cmd = [
        "ffmpeg",
        "-y",  # Overwrite output
    ]
    
    # Add input files
    for scene in timeline_config["scenes"]:
        if scene["path"]:
            cmd.extend(["-i", scene["path"]])
    
    # Add audio
    cmd.extend(["-i", audio_path])
    
    # Add filter complex
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", f"{len(timeline_config['scenes'])}:a",  # Audio input index
    ])
    
    # Output settings
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path
    ])
    
    # Run FFmpeg
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        raise Exception(f"FFmpeg failed: {stderr.decode()}")


def build_filter_complex(timeline_config: Dict) -> str:
    """Build FFmpeg filter complex string"""
    
    filters = []
    concat_inputs = []
    
    resolution = timeline_config["resolution"]
    width, height = resolution.split("x")
    
    for i, scene in enumerate(timeline_config["scenes"]):
        input_label = f"[{i}:v]"
        output_label = f"[v{i}]"
        
        scene_filters = []
        
        # Scale to output resolution
        scene_filters.append(f"scale={width}:{height}:force_original_aspect_ratio=decrease")
        scene_filters.append(f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2")
        
        # Apply effects
        for effect in scene.get("effects", []):
            effect_filter = get_effect_filter(effect, scene["duration"])
            if effect_filter:
                scene_filters.append(effect_filter)
        
        # Set duration
        scene_filters.append(f"setpts=PTS-STARTPTS")
        scene_filters.append(f"trim=duration={scene['duration']}")
        
        # Build filter chain for this scene
        filter_chain = f"{input_label}{','.join(scene_filters)}{output_label}"
        filters.append(filter_chain)
        concat_inputs.append(output_label)
    
    # Concatenate all scenes
    concat_filter = f"{''.join(concat_inputs)}concat=n={len(concat_inputs)}:v=1:a=0[outv]"
    filters.append(concat_filter)
    
    return ";".join(filters)


def get_effect_filter(effect: str, duration: float) -> str:
    """Get FFmpeg filter for effect"""
    
    effect_filters = {
        "fade_in": "fade=t=in:d=1",
        "fade_out": f"fade=t=out:st={duration-1}:d=1",
        "ken_burns": f"zoompan=z='min(zoom+0.0015,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={duration*30}:s={settings.VIDEO_RESOLUTION}",
        "slow_zoom_in": f"zoompan=z='min(zoom+0.001,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={duration*30}:s={settings.VIDEO_RESOLUTION}",
        "vintage_filter": "curves=vintage,colorbalance=rs=.1:gs=-.05:bs=-.1",
        "sepia_tone": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131",
        "film_grain": "noise=alls=3:allf=t",
        "soft_vignette": "vignette",
        "cross_dissolve": "fade=t=in:d=0.5,fade=t=out:d=0.5:st=" + str(duration - 0.5)
    }
    
    return effect_filters.get(effect, "")


def get_video_duration(video_path: str) -> int:
    """Get actual duration of video file"""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return int(float(result.stdout.strip()))
    
    return 0


def get_file_extension(url: str) -> str:
    """Extract file extension from URL"""
    path = url.split("?")[0]  # Remove query parameters
    extension = os.path.splitext(path)[1].lstrip(".")
    return extension or "mp4"


# Add intro and outro
async def add_intro_outro(
    main_video_path: str,
    output_path: str,
    title: str
) -> None:
    """Add intro and outro to the main video"""
    
    # Generate intro card
    intro_path = await generate_title_card(title, "intro")
    outro_path = await generate_title_card("Thank you for watching", "outro")
    
    # Concatenate intro + main + outro
    cmd = [
        "ffmpeg",
        "-y",
        "-i", intro_path,
        "-i", main_video_path,
        "-i", outro_path,
        "-filter_complex",
        "[0:v][1:v][2:v]concat=n=3:v=1:a=0[outv];"
        "[1:a]apad[outa]",
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-c:a", "aac",
        output_path
    ]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    await process.communicate()


async def generate_title_card(text: str, card_type: str) -> str:
    """Generate a title card image"""
    
    # This would use ImageMagick or Pillow to create title cards
    # For now, return a placeholder
    
    if card_type == "intro":
        return "https://legacylabs-assets.s3.amazonaws.com/templates/intro_card.mp4"
    else:
        return "https://legacylabs-assets.s3.amazonaws.com/templates/outro_card.mp4"
