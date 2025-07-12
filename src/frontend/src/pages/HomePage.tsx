import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { 
  ArrowRight, 
  Film, 
  Clock, 
  Heart, 
  Sparkles,
  Upload,
  Play,
  Download,
  Users,
  Star
} from 'lucide-react'
import { useState } from 'react'

export default function HomePage() {
  const [isVideoPlaying, setIsVideoPlaying] = useState(false)

  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-primary/5 to-background">
        <div className="container mx-auto px-4 py-20 md:py-32">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-6 animate-fade-in">
              <h1 className="text-4xl md:text-6xl font-bold leading-tight">
                Transform Your Family Tree Into Their{' '}
                <span className="text-primary">Greatest Story</span>
              </h1>
              <p className="text-xl text-muted-foreground">
                Upload your genealogy data and watch as AI creates a beautiful, 
                professionally narrated documentary that brings your family history to life.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/signup">
                  <Button size="lg" className="gap-2">
                    Start Your Story Free
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
                <Button 
                  size="lg" 
                  variant="outline"
                  onClick={() => setIsVideoPlaying(true)}
                  className="gap-2"
                >
                  <Play className="h-4 w-4" />
                  Watch Demo
                </Button>
              </div>
              <div className="flex items-center gap-6 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Star className="h-4 w-4 fill-primary text-primary" />
                  <span>4.9/5 rating</span>
                </div>
                <div className="flex items-center gap-1">
                  <Users className="h-4 w-4" />
                  <span>10,000+ families</span>
                </div>
              </div>
            </div>
            
            <div className="relative">
              <div className="aspect-video rounded-lg overflow-hidden shadow-2xl vintage-photo">
                {/* Placeholder for demo video thumbnail */}
                <div className="w-full h-full bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                  <Play className="h-16 w-16 text-white/80" />
                </div>
              </div>
              {/* Floating testimonial */}
              <div className="absolute -bottom-6 -left-6 bg-card p-4 rounded-lg shadow-lg max-w-xs animate-fade-in animation-delay-200">
                <p className="text-sm italic">"This made my mother cry happy tears. Worth every penny!"</p>
                <p className="text-xs text-muted-foreground mt-2">- Sarah J.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              From Family Tree to Family Film in Minutes
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Our AI-powered platform transforms your genealogy data into a compelling documentary
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center space-y-4">
              <div className="w-20 h-20 mx-auto bg-primary/10 rounded-full flex items-center justify-center">
                <Upload className="h-10 w-10 text-primary" />
              </div>
              <h3 className="text-xl font-semibold">1. Upload Your Data</h3>
              <p className="text-muted-foreground">
                Simply upload your GEDCOM file from Ancestry.com or any genealogy platform
              </p>
            </div>
            
            <div className="text-center space-y-4">
              <div className="w-20 h-20 mx-auto bg-secondary/10 rounded-full flex items-center justify-center">
                <Sparkles className="h-10 w-10 text-secondary" />
              </div>
              <h3 className="text-xl font-semibold">2. AI Creates Your Story</h3>
              <p className="text-muted-foreground">
                Our AI analyzes your family history and creates a personalized narrative
              </p>
            </div>
            
            <div className="text-center space-y-4">
              <div className="w-20 h-20 mx-auto bg-accent/10 rounded-full flex items-center justify-center">
                <Download className="h-10 w-10 text-accent" />
              </div>
              <h3 className="text-xl font-semibold">3. Download & Share</h3>
              <p className="text-muted-foreground">
                Get your professional documentary ready to share with family
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div>
                <h2 className="text-3xl md:text-4xl font-bold mb-4">
                  Every Family Deserves a Beautiful Story
                </h2>
                <p className="text-xl text-muted-foreground">
                  We combine cutting-edge AI with emotional intelligence to create documentaries that capture the heart of your family's journey.
                </p>
              </div>
              
              <div className="space-y-6">
                <div className="flex gap-4">
                  <Film className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-semibold mb-1">Professional Quality</h3>
                    <p className="text-muted-foreground">
                      Documentary-style narration with period-accurate visuals
                    </p>
                  </div>
                </div>
                
                <div className="flex gap-4">
                  <Clock className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-semibold mb-1">Quick Turnaround</h3>
                    <p className="text-muted-foreground">
                      Get your video in minutes, not months
                    </p>
                  </div>
                </div>
                
                <div className="flex gap-4">
                  <Heart className="h-6 w-6 text-primary flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-semibold mb-1">Emotionally Compelling</h3>
                    <p className="text-muted-foreground">
                      Stories that celebrate life and preserve memories
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <img 
                src="/api/placeholder/300/400" 
                alt="Historical photo 1" 
                className="rounded-lg vintage-photo"
              />
              <img 
                src="/api/placeholder/300/400" 
                alt="Historical photo 2" 
                className="rounded-lg vintage-photo mt-8"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            Families Love Their Stories
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="bg-card p-6 rounded-lg shadow-sm">
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-4 w-4 fill-primary text-primary" />
                ))}
              </div>
              <p className="italic mb-4">
                "We played this at my grandmother's 90th birthday. There wasn't a dry eye in the room. 
                It captured our family's journey perfectly."
              </p>
              <p className="text-sm font-semibold">Michael Thompson</p>
            </div>
            
            <div className="bg-card p-6 rounded-lg shadow-sm">
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-4 w-4 fill-primary text-primary" />
                ))}
              </div>
              <p className="italic mb-4">
                "As a funeral director, this has transformed how we help families celebrate lives. 
                It's become our most requested service."
              </p>
              <p className="text-sm font-semibold">David Martinez, Funeral Director</p>
            </div>
            
            <div className="bg-card p-6 rounded-lg shadow-sm">
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-4 w-4 fill-primary text-primary" />
                ))}
              </div>
              <p className="italic mb-4">
                "I've spent years researching my family tree. This brought it to life in ways 
                I never imagined possible."
              </p>
              <p className="text-sm font-semibold">Jennifer Chen</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary text-primary-foreground">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Preserve Your Family's Legacy?
          </h2>
          <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
            Join thousands of families who have transformed their genealogy data into treasured documentaries.
          </p>
          <Link to="/signup">
            <Button size="lg" variant="secondary" className="gap-2">
              Start Your Free Documentary
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <p className="mt-4 text-sm opacity-75">
            No credit card required • 5-minute video included free
          </p>
        </div>
      </section>

      {/* Video Modal */}
      {isVideoPlaying && (
        <div 
          className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
          onClick={() => setIsVideoPlaying(false)}
        >
          <div className="max-w-4xl w-full aspect-video bg-black rounded-lg">
            {/* Video player would go here */}
            <div className="w-full h-full flex items-center justify-center text-white">
              Demo video player
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
