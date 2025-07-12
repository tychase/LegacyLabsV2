import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { 
  X, 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  Info
} from 'lucide-react'
import axios from 'axios'

interface GedcomUploadProps {
  onClose: () => void
}

export default function GedcomUpload({ onClose }: GedcomUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [projectTitle, setProjectTitle] = useState('')
  const queryClient = useQueryClient()

  const createProject = useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await axios.post('/projects', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
            setUploadProgress(progress)
          }
        },
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      onClose()
    },
  })

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const gedcomFile = acceptedFiles[0]
      setFile(gedcomFile)
      
      // Extract title from filename
      const name = gedcomFile.name.replace(/\.(ged|gedcom)$/i, '')
      setProjectTitle(name)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/gedcom': ['.ged', '.gedcom'],
    },
    maxFiles: 1,
  })

  const handleSubmit = () => {
    if (!file || !projectTitle) return

    const formData = new FormData()
    formData.append('gedcom_file', file)
    formData.append('title', projectTitle)
    
    createProject.mutate(formData)
  }

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-background rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold">Create New Documentary</h2>
          <button 
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Info Box */}
          <div className="bg-primary/5 border border-primary/20 rounded-lg p-4 flex gap-3">
            <Info className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
            <div className="text-sm">
              <p className="font-semibold mb-1">What is a GEDCOM file?</p>
              <p className="text-muted-foreground">
                GEDCOM files contain your family tree data. You can export them from 
                Ancestry.com, MyHeritage, FamilySearch, or any genealogy software.
              </p>
            </div>
          </div>

          {/* Upload Area */}
          {!file ? (
            <div
              {...getRootProps()}
              className={`
                border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
                transition-colors
                ${isDragActive 
                  ? 'border-primary bg-primary/5' 
                  : 'border-muted-foreground/25 hover:border-primary'
                }
              `}
            >
              <input {...getInputProps()} />
              <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-lg font-medium mb-2">
                {isDragActive 
                  ? 'Drop your GEDCOM file here' 
                  : 'Drag & drop your GEDCOM file here'
                }
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                or click to browse your files
              </p>
              <p className="text-xs text-muted-foreground">
                Supports .ged and .gedcom files up to 50MB
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* File Preview */}
              <div className="bg-muted/50 rounded-lg p-4 flex items-center gap-3">
                <FileText className="h-8 w-8 text-primary" />
                <div className="flex-1">
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <button
                  onClick={() => setFile(null)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {/* Project Title */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Documentary Title
                </label>
                <input
                  type="text"
                  value={projectTitle}
                  onChange={(e) => setProjectTitle(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="My Family Story"
                />
              </div>

              {/* Upload Progress */}
              {createProject.isPending && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Uploading...</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-primary h-2 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Error Message */}
              {createProject.isError && (
                <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 flex gap-3">
                  <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0" />
                  <div>
                    <p className="font-medium">Upload failed</p>
                    <p className="text-sm text-muted-foreground mt-1">
                      There was an error uploading your file. Please try again.
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* What Happens Next */}
          <div className="bg-muted/50 rounded-lg p-4 space-y-3">
            <h3 className="font-semibold">What happens next?</h3>
            <div className="space-y-2 text-sm text-muted-foreground">
              <div className="flex gap-2">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                <span>We'll analyze your family tree data</span>
              </div>
              <div className="flex gap-2">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                <span>AI creates a personalized narrative</span>
              </div>
              <div className="flex gap-2">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                <span>Professional narration is generated</span>
              </div>
              <div className="flex gap-2">
                <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0 mt-0.5" />
                <span>Your documentary is ready in 5-10 minutes</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex gap-3 p-6 border-t">
          <Button 
            variant="outline" 
            onClick={onClose}
            disabled={createProject.isPending}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit}
            disabled={!file || !projectTitle || createProject.isPending}
            className="flex-1"
          >
            {createProject.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Creating Documentary...
              </>
            ) : (
              'Create Documentary'
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}
