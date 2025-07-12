import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { 
  ArrowLeft, 
  Download, 
  Share2, 
  Edit, 
  Play,
  Pause,
  Volume2,
  Maximize,
  SkipBack,
  SkipForward
} from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

export default function ProjectPage() {
  const { id } = useParams()
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const videoRef = useRef<HTMLVideoElement>(null)

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', id],
    queryFn: async () => {
      const response = await axios.get(`/projects/${id}`)
      return response.data
    }
  })

  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime)
    }
  }

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration)
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Project not found</h2>
          <Link to="/dashboard">
            <Button>Back to Dashboard</Button>
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link to="/dashboard">
                <Button variant="ghost" size="sm" className="gap-2">
                  <ArrowLeft className="h-4 w-4" />
                  Back
                </Button>
              </Link>
              <h1 className="text-2xl font-bold">{project.title}</h1>
            </div>
            
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" className="gap-2">
                <Share2 className="h-4 w-4" />
                Share
              </Button>
              <Button variant="outline" size="sm" className="gap-2">
                <Download className="h-4 w-4" />
                Download
              </Button>
              <Button size="sm" className="gap-2">
                <Edit className="h-4 w-4" />
                Edit
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Video Player */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-5xl mx-auto">
          {project.status === 'completed' && project.video_url ? (
            <div className="space-y-4">
              {/* Video Container */}
              <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
                <video
                  ref={videoRef}
                  src={project.video_url}
                  className="w-full h-full"
                  onTimeUpdate={handleTimeUpdate}
                  onLoadedMetadata={handleLoadedMetadata}
                />
                
                {/* Custom Controls Overlay */}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="bg-white/20 rounded-full h-1 cursor-pointer">
                      <div 
                        className="bg-primary h-full rounded-full"
                        style={{ width: `${(currentTime / duration) * 100}%` }}
                      />
                    </div>
                  </div>
                  
                  {/* Controls */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <button onClick={togglePlayPause} className="text-white hover:text-primary">
                        {isPlaying ? (
                          <Pause className="h-6 w-6" />
                        ) : (
                          <Play className="h-6 w-6" />
                        )}
                      </button>
                      
                      <button className="text-white hover:text-primary">
                        <SkipBack className="h-5 w-5" />
                      </button>
                      
                      <button className="text-white hover:text-primary">
                        <SkipForward className="h-5 w-5" />
                      </button>
                      
                      <button className="text-white hover:text-primary">
                        <Volume2 className="h-5 w-5" />
                      </button>
                      
                      <span className="text-white text-sm">
                        {formatTime(currentTime)} / {formatTime(duration)}
                      </span>
                    </div>
                    
                    <button className="text-white hover:text-primary">
                      <Maximize className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Transcript */}
              <div className="bg-card rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4">Transcript</h2>
                <div className="prose prose-sm max-w-none">
                  <p className="text-muted-foreground whitespace-pre-wrap">
                    {project.transcript || 'No transcript available'}
                  </p>
                </div>
              </div>

              {/* Project Details */}
              <div className="grid md:grid-cols-3 gap-6">
                <div className="bg-card rounded-lg p-6">
                  <h3 className="font-semibold mb-2">Created</h3>
                  <p className="text-muted-foreground">
                    {new Date(project.created_at).toLocaleDateString()}
                  </p>
                </div>
                
                <div className="bg-card rounded-lg p-6">
                  <h3 className="font-semibold mb-2">Duration</h3>
                  <p className="text-muted-foreground">
                    {Math.floor(project.video_duration / 60)} minutes
                  </p>
                </div>
                
                <div className="bg-card rounded-lg p-6">
                  <h3 className="font-semibold mb-2">Themes</h3>
                  <p className="text-muted-foreground">
                    {project.story_themes?.join(', ') || 'General family history'}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <h2 className="text-2xl font-bold mb-2">Processing your documentary...</h2>
              <p className="text-muted-foreground">
                This usually takes 5-10 minutes. We'll email you when it's ready.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
