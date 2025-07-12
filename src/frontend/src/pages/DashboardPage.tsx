import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { 
  Plus, 
  Film, 
  Clock, 
  CheckCircle,
  AlertCircle,
  Loader2,
  Play,
  Edit,
  Trash2
} from 'lucide-react'
import { format } from 'date-fns'
import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'
import GedcomUpload from '@/components/GedcomUpload'

interface Project {
  id: number
  title: string
  description?: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  updated_at: string
  video_url?: string
  thumbnail_url?: string
  video_duration?: number
}

export default function DashboardPage() {
  const [showUpload, setShowUpload] = useState(false)
  const { user } = useAuthStore()
  const queryClient = useQueryClient()

  // Fetch user's projects
  const { data: projects, isLoading } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await axios.get('/projects')
      return response.data
    }
  })

  // Delete project mutation
  const deleteProject = useMutation({
    mutationFn: async (projectId: number) => {
      await axios.delete(`/projects/${projectId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    }
  })

  const getStatusIcon = (status: Project['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'processing':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />
      default:
        return <Clock className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusText = (status: Project['status']) => {
    switch (status) {
      case 'completed':
        return 'Ready to view'
      case 'processing':
        return 'Creating your documentary...'
      case 'failed':
        return 'Failed to process'
      default:
        return 'Waiting to process'
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">My Family Documentaries</h1>
          <p className="text-muted-foreground mt-2">
            Welcome back, {user?.full_name || user?.email}
          </p>
        </div>
        <Button onClick={() => setShowUpload(true)} className="gap-2">
          <Plus className="h-4 w-4" />
          New Documentary
        </Button>
      </div>

      {/* Projects Grid */}
      {projects && projects.length > 0 ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div key={project.id} className="bg-card rounded-lg shadow-sm overflow-hidden">
              {/* Thumbnail */}
              <div className="aspect-video bg-muted relative group">
                {project.thumbnail_url ? (
                  <img 
                    src={project.thumbnail_url} 
                    alt={project.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Film className="h-12 w-12 text-muted-foreground" />
                  </div>
                )}
                
                {project.status === 'completed' && (
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <Link to={`/project/${project.id}`}>
                      <Button size="sm" variant="secondary" className="gap-2">
                        <Play className="h-4 w-4" />
                        Watch
                      </Button>
                    </Link>
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-lg">{project.title}</h3>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(project.status)}
                  </div>
                </div>
                
                <p className="text-sm text-muted-foreground mb-3">
                  {getStatusText(project.status)}
                </p>
                
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>{format(new Date(project.created_at), 'MMM d, yyyy')}</span>
                  {project.video_duration && (
                    <span>{Math.floor(project.video_duration / 60)} min</span>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2 mt-4">
                  {project.status === 'completed' ? (
                    <>
                      <Link to={`/project/${project.id}`} className="flex-1">
                        <Button size="sm" variant="outline" className="w-full gap-2">
                          <Edit className="h-3 w-3" />
                          Edit
                        </Button>
                      </Link>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => {
                          if (confirm('Are you sure you want to delete this documentary?')) {
                            deleteProject.mutate(project.id)
                          }
                        }}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </>
                  ) : project.status === 'failed' ? (
                    <Button size="sm" variant="outline" className="w-full">
                      Retry
                    </Button>
                  ) : null}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <Film className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-2xl font-semibold mb-2">No documentaries yet</h2>
          <p className="text-muted-foreground mb-6 max-w-md mx-auto">
            Upload your family history data to create your first beautiful documentary
          </p>
          <Button onClick={() => setShowUpload(true)} className="gap-2">
            <Plus className="h-4 w-4" />
            Create Your First Documentary
          </Button>
        </div>
      )}

      {/* Upload Modal */}
      {showUpload && (
        <GedcomUpload onClose={() => setShowUpload(false)} />
      )}
    </div>
  )
}
