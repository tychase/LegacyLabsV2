# LegacyLabs Technical Specification

## System Architecture

### 1. GEDCOM Processing Pipeline

#### Data Ingestion
```python
class GEDCOMProcessor:
    """
    Handles parsing and validation of GEDCOM files
    Compatible with Ancestry.com export format
    """
    
    def parse_file(self, file_path):
        # Extract individuals, families, events
        # Validate data integrity
        # Build relationship graph
        pass
    
    def extract_story_elements(self):
        # Identify key life events
        # Calculate family dynamics
        # Determine geographic movements
        # Flag historical contexts
        pass
```

#### Story Element Categories
1. **Life Events**
   - Birth (date, location, circumstances)
   - Baptism/religious ceremonies
   - Education milestones
   - Marriage(s)
   - Career/occupation changes
   - Military service
   - Death and burial

2. **Geographic Data**
   - Immigration patterns
   - City/state/country movements
   - Distance from family members
   - Historical context of locations

3. **Family Dynamics**
   - Number of siblings
   - Birth order
   - Age gaps
   - Multi-generational patterns
   - Family size trends

### 2. Narrative Generation Engine

#### Story Logic Trees
```yaml
story_templates:
  immigration:
    triggers:
      - country_change: true
      - ocean_crossing: true
    narrative_blocks:
      - departure_context
      - journey_description
      - arrival_experience
      - settlement_story
    
  large_family:
    triggers:
      - sibling_count: ">= 8"
    narrative_blocks:
      - family_size_context
      - sibling_relationships
      - household_dynamics
      - economic_implications
  
  early_death:
    triggers:
      - death_age: "< 50"
      - has_young_children: true
    narrative_blocks:
      - life_cut_short
      - family_impact
      - legacy_continuation
```

#### Narrative Voice Profiles
1. **Professional Documentary**
   - Formal, measured pace
   - Historical context emphasis
   - Third-person perspective

2. **Family Storyteller**
   - Warm, conversational
   - Personal anecdotes style
   - Mix of first/third person

3. **Memorial Service**
   - Respectful, commemorative
   - Celebration of life focus
   - Comfort-oriented

### 3. Visual Generation System

#### Stock Footage Library Structure
```
/media_library/
  /by_era/
    /1800-1850/
    /1851-1900/
    /1901-1950/
    /1951-2000/
    /2001-present/
  /by_region/
    /north_america/
    /europe/
    /asia/
    /africa/
    /south_america/
    /oceania/
  /by_theme/
    /immigration/
    /military/
    /farming/
    /urban_life/
    /family_gatherings/
```

#### AI Prompt Templates
```python
visual_prompts = {
    "german_village_1850": {
        "base": "Peaceful village scene in Bavaria, Germany, 1850s",
        "style": "historical painting style, sepia toned",
        "elements": ["church spire", "cobblestone streets", "traditional houses"],
        "avoid": ["modern elements", "cars", "power lines"]
    },
    
    "ellis_island_arrival": {
        "base": "Immigrants arriving at Ellis Island, early 1900s",
        "style": "vintage photograph aesthetic",
        "elements": ["ship in background", "crowds", "luggage"],
        "mood": "hopeful, nervous energy"
    }
}
```

### 4. Video Assembly Pipeline

#### Timeline Generation
```python
class VideoTimeline:
    def __init__(self, story_data):
        self.duration = self.calculate_duration(story_data)
        self.segments = []
    
    def add_segment(self, segment_type, content, duration):
        """
        segment_types: intro, life_event, transition, conclusion
        """
        pass
    
    def apply_transitions(self):
        # Smooth transitions between segments
        # Match transition style to narrative tone
        pass
    
    def add_lower_thirds(self):
        # Names, dates, locations
        # Family relationship indicators
        pass
```

#### Audio Processing
- Background music selection algorithm
- Voice-over timing and pacing
- Pronunciation database integration
- Audio ducking for emphasis

### 5. User Portal Architecture

#### Frontend Stack
- **Framework**: React with TypeScript
- **State Management**: Redux Toolkit
- **UI Library**: Tailwind CSS + Shadcn/ui
- **Video Player**: Custom player with timeline markers
- **File Upload**: Resumable uploads for large files

#### Backend Services
- **API**: FastAPI (Python)
- **Database**: PostgreSQL with PostGIS
- **File Storage**: S3-compatible object storage
- **Queue System**: Redis + Celery for video processing
- **CDN**: CloudFront for video delivery

#### Authentication & Security
- **Auth**: Auth0 or Clerk
- **Encryption**: AES-256 for stored data
- **Access Control**: Row-level security
- **Audit Logging**: All data access tracked

### 6. AI/ML Infrastructure

#### Model Selection
```python
AI_MODELS = {
    "visual_generation": {
        "primary": "veo3",
        "fallback": "gemini-pro-vision",
        "config": {
            "resolution": "1920x1080",
            "fps": 30,
            "style": "documentary"
        }
    },
    
    "narration": {
        "service": "elevenlabs",
        "voices": ["documentary_male", "documentary_female", "memorial_warm"],
        "config": {
            "stability": 0.8,
            "clarity": 0.9
        }
    },
    
    "story_generation": {
        "model": "claude-opus-4",
        "temperature": 0.7,
        "max_tokens": 2000
    }
}
```

#### Processing Pipeline
1. **Queue Management**
   - Priority queue for paid users
   - Batch processing for efficiency
   - Progress tracking and notifications

2. **Quality Assurance**
   - Automated content review
   - Inappropriate content filtering
   - Historical accuracy checks
   - Output quality validation

### 7. Integration APIs

#### White-Label Configuration
```yaml
white_label_config:
  branding:
    - logo_upload
    - color_scheme
    - font_selection
    - email_templates
  
  features:
    - feature_toggles
    - custom_narratives
    - output_formats
    - delivery_methods
  
  pricing:
    - volume_discounts
    - revenue_sharing
    - usage_tracking
```

#### Webhook System
```python
WEBHOOK_EVENTS = [
    "video.processing.started",
    "video.processing.completed",
    "video.processing.failed",
    "user.edit.saved",
    "user.media.uploaded",
    "subscription.created",
    "subscription.cancelled"
]
```

### 8. Performance Optimization

#### Caching Strategy
- **CDN**: Static assets and completed videos
- **Redis**: User sessions and processing status
- **Database**: Query result caching
- **Local**: Frequently accessed media assets

#### Scaling Considerations
- **Horizontal Scaling**: Kubernetes deployment
- **GPU Clusters**: For AI video generation
- **Geographic Distribution**: Multi-region deployment
- **Load Balancing**: Intelligent routing

### 9. Monitoring & Analytics

#### System Monitoring
- **APM**: DataDog or New Relic
- **Logging**: ELK stack
- **Alerts**: PagerDuty integration
- **Metrics**: Prometheus + Grafana

#### Business Analytics
```sql
-- Key metrics queries
SELECT 
    DATE_TRUNC('day', created_at) as date,
    COUNT(*) as videos_created,
    AVG(processing_time) as avg_processing_time,
    SUM(CASE WHEN edited = true THEN 1 ELSE 0 END) as edited_count
FROM videos
GROUP BY DATE_TRUNC('day', created_at);
```

### 10. Development Workflow

#### Git Structure
```
/legacylabs/
  /frontend/          # React application
  /backend/           # FastAPI services
  /ml-models/         # AI/ML pipeline code
  /infrastructure/    # Terraform/K8s configs
  /docs/             # Technical documentation
  /tests/            # Test suites
```

#### CI/CD Pipeline
1. **Code Quality**: ESLint, Black, mypy
2. **Testing**: Jest, pytest, integration tests
3. **Security**: SAST scanning, dependency checks
4. **Deployment**: Blue-green deployments
5. **Rollback**: Automated rollback on failures

---

## Implementation Roadmap

### Phase 1: MVP (Months 1-3)
- Basic GEDCOM parsing
- Simple narrative generation
- Stock footage only
- Basic web interface

### Phase 2: Enhanced Features (Months 4-6)
- AI visual generation
- Multiple voice options
- Editing portal
- B2B portal

### Phase 3: Scale & Optimize (Months 7-12)
- Performance optimization
- White-label platform
- Advanced analytics
- Mobile apps