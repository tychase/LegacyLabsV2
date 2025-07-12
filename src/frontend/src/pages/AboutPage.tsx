import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { 
  Heart, 
  Users, 
  Globe, 
  Sparkles,
  Award,
  Shield
} from 'lucide-react'

export default function AboutPage() {
  const values = [
    {
      icon: Heart,
      title: 'Family First',
      description: 'We believe every family story deserves to be preserved with care and dignity.'
    },
    {
      icon: Shield,
      title: 'Privacy Focused',
      description: 'Your family data is sacred. We use bank-level encryption and never share your information.'
    },
    {
      icon: Sparkles,
      title: 'Innovation with Purpose',
      description: 'We harness AI not to replace human connection, but to enhance and preserve it.'
    },
    {
      icon: Globe,
      title: 'Accessible to All',
      description: 'Professional documentaries should be available to every family, regardless of technical skill.'
    }
  ]

  const team = [
    {
      name: 'Sarah Chen',
      role: 'CEO & Co-Founder',
      bio: 'Former Ancestry.com product lead with a passion for family storytelling.',
      image: '/api/placeholder/200/200'
    },
    {
      name: 'Michael Rodriguez',
      role: 'CTO & Co-Founder',
      bio: 'AI researcher focused on making technology more human and accessible.',
      image: '/api/placeholder/200/200'
    },
    {
      name: 'Emily Thompson',
      role: 'Head of Storytelling',
      bio: 'Documentary filmmaker bringing professional narrative techniques to family histories.',
      image: '/api/placeholder/200/200'
    }
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="py-20 text-center">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">
            Preserving Family Legacies, One Story at a Time
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            LegacyLabs was born from a simple belief: every family's history is a treasure 
            that deserves to be preserved and shared with future generations.
          </p>
        </div>
      </section>

      {/* Our Story */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold mb-8 text-center">Our Story</h2>
            
            <div className="prose prose-lg mx-auto">
              <p className="text-muted-foreground">
                It started with a shoebox full of old photos and a GEDCOM file that no one in the family could understand. 
                Our founder, Sarah, had spent years researching her family history on Ancestry.com, accumulating names, 
                dates, and places. But when she tried to share this treasure trove with her family at a reunion, 
                she watched their eyes glaze over at the sight of endless family tree charts.
              </p>
              
              <p className="text-muted-foreground mt-4">
                That's when the idea struck: what if we could transform these databases into something people actually 
                want to watch? What if we could use AI not to replace the human element of storytelling, but to 
                enhance it—to find the narrative threads that connect generations and weave them into compelling documentaries?
              </p>
              
              <p className="text-muted-foreground mt-4">
                Today, LegacyLabs helps thousands of families transform their genealogical data into beautiful, 
                professionally narrated documentaries. We've seen these videos played at family reunions, memorial services, 
                and birthday celebrations. We've received letters from grandchildren finally understanding their heritage, 
                and from parents grateful to preserve their family's story for future generations.
              </p>
              
              <p className="text-muted-foreground mt-4 font-semibold">
                Every family has a story worth telling. We're here to help you tell yours.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Our Values */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-12 text-center">Our Values</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-5xl mx-auto">
            {values.map((value) => {
              const Icon = value.icon
              return (
                <div key={value.title} className="text-center">
                  <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Icon className="h-8 w-8 text-primary" />
                  </div>
                  <h3 className="font-semibold mb-2">{value.title}</h3>
                  <p className="text-sm text-muted-foreground">{value.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-12 text-center">Meet the Team</h2>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {team.map((member) => (
              <div key={member.name} className="text-center">
                <img
                  src={member.image}
                  alt={member.name}
                  className="w-32 h-32 rounded-full mx-auto mb-4 object-cover"
                />
                <h3 className="font-semibold text-lg">{member.name}</h3>
                <p className="text-primary mb-2">{member.role}</p>
                <p className="text-sm text-muted-foreground">{member.bio}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8 max-w-4xl mx-auto text-center">
            <div>
              <div className="text-4xl font-bold text-primary mb-2">10,000+</div>
              <p className="text-muted-foreground">Families Served</p>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">50,000+</div>
              <p className="text-muted-foreground">Stories Preserved</p>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">4.9/5</div>
              <p className="text-muted-foreground">Customer Rating</p>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary mb-2">24/7</div>
              <p className="text-muted-foreground">Support Available</p>
            </div>
          </div>
        </div>
      </section>

      {/* Awards Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-12">Recognition</h2>
          
          <div className="flex flex-wrap justify-center items-center gap-8">
            <div className="flex items-center gap-2">
              <Award className="h-8 w-8 text-primary" />
              <div className="text-left">
                <p className="font-semibold">Best New Startup 2024</p>
                <p className="text-sm text-muted-foreground">TechCrunch Awards</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Award className="h-8 w-8 text-primary" />
              <div className="text-left">
                <p className="font-semibold">Innovation in AI</p>
                <p className="text-sm text-muted-foreground">AI Excellence Awards</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Award className="h-8 w-8 text-primary" />
              <div className="text-left">
                <p className="font-semibold">Family Choice Award</p>
                <p className="text-sm text-muted-foreground">Family Tech Magazine</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Preserve Your Family's Legacy?
          </h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join thousands of families who have discovered the power of their story.
          </p>
          <div className="flex gap-4 justify-center">
            <Link to="/signup">
              <Button size="lg">
                Start Your Story
              </Button>
            </Link>
            <Link to="/pricing">
              <Button size="lg" variant="outline">
                View Pricing
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
