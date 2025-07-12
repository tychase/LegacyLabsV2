import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Check, X } from 'lucide-react'
import { useState } from 'react'

interface PricingTier {
  name: string
  price: number
  description: string
  features: string[]
  notIncluded?: string[]
  recommended?: boolean
  cta: string
}

export default function PricingPage() {
  const [isAnnual, setIsAnnual] = useState(false)

  const tiers: PricingTier[] = [
    {
      name: 'Starter',
      price: isAnnual ? 39 : 49,
      description: 'Perfect for trying out LegacyLabs',
      features: [
        '1 documentary per month',
        '5-minute video length',
        'Standard narrator voice',
        'Stock visuals only',
        'Email delivery',
        'Basic support'
      ],
      notIncluded: [
        'Custom visuals',
        'Editing portal',
        'Multiple exports'
      ],
      cta: 'Start Free Trial'
    },
    {
      name: 'Family',
      price: isAnnual ? 79 : 99,
      description: 'Most popular for families',
      features: [
        '3 documentaries per month',
        '10-minute video length',
        '3 narrator voice options',
        'AI-generated custom visuals',
        'Editing portal access',
        'HD downloads',
        'Priority support',
        'Family sharing (5 members)'
      ],
      recommended: true,
      cta: 'Start Free Trial'
    },
    {
      name: 'Legacy',
      price: isAnnual ? 159 : 199,
      description: 'For family historians and professionals',
      features: [
        'Unlimited documentaries',
        '20-minute video length',
        'Premium narrator selection',
        'Advanced AI visuals',
        'Full editing suite',
        '4K downloads',
        'White-label option',
        'API access',
        'Dedicated support',
        'Custom branding'
      ],
      cta: 'Start Free Trial'
    }
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <section className="py-20 text-center">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Simple, Transparent Pricing
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
            Choose the perfect plan for preserving your family's legacy. 
            All plans include our AI-powered storytelling engine.
          </p>
          
          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-4 mb-12">
            <span className={!isAnnual ? 'font-semibold' : 'text-muted-foreground'}>
              Monthly
            </span>
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className="relative inline-flex h-6 w-11 items-center rounded-full bg-primary/20"
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-primary transition ${
                  isAnnual ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span className={isAnnual ? 'font-semibold' : 'text-muted-foreground'}>
              Annual
              <span className="text-primary ml-1">(Save 20%)</span>
            </span>
          </div>
        </div>
      </section>

      {/* Pricing Tiers */}
      <section className="pb-20">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {tiers.map((tier) => (
              <div
                key={tier.name}
                className={`relative bg-card rounded-lg p-8 ${
                  tier.recommended
                    ? 'ring-2 ring-primary shadow-lg scale-105'
                    : 'border'
                }`}
              >
                {tier.recommended && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-primary text-primary-foreground px-3 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold mb-2">{tier.name}</h3>
                  <p className="text-muted-foreground mb-4">{tier.description}</p>
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="text-4xl font-bold">${tier.price}</span>
                    <span className="text-muted-foreground">
                      /{isAnnual ? 'year' : 'month'}
                    </span>
                  </div>
                </div>
                
                <ul className="space-y-3 mb-8">
                  {tier.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2">
                      <Check className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                      <span className="text-sm">{feature}</span>
                    </li>
                  ))}
                  
                  {tier.notIncluded?.map((feature) => (
                    <li key={feature} className="flex items-start gap-2 opacity-50">
                      <X className="h-5 w-5 text-muted-foreground flex-shrink-0 mt-0.5" />
                      <span className="text-sm line-through">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Link to="/signup">
                  <Button
                    className="w-full"
                    variant={tier.recommended ? 'default' : 'outline'}
                  >
                    {tier.cta}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">
            Frequently Asked Questions
          </h2>
          
          <div className="max-w-3xl mx-auto space-y-8">
            <div>
              <h3 className="text-xl font-semibold mb-2">
                Can I change plans later?
              </h3>
              <p className="text-muted-foreground">
                Yes! You can upgrade or downgrade your plan at any time. Changes take effect at the next billing cycle.
              </p>
            </div>
            
            <div>
              <h3 className="text-xl font-semibold mb-2">
                What file formats do you support?
              </h3>
              <p className="text-muted-foreground">
                We support GEDCOM files (.ged, .gedcom) from all major genealogy platforms including Ancestry.com, MyHeritage, and FamilySearch.
              </p>
            </div>
            
            <div>
              <h3 className="text-xl font-semibold mb-2">
                Is my family data secure?
              </h3>
              <p className="text-muted-foreground">
                Absolutely. We use bank-level encryption and never share your data. You can delete your projects and data at any time.
              </p>
            </div>
            
            <div>
              <h3 className="text-xl font-semibold mb-2">
                Do you offer refunds?
              </h3>
              <p className="text-muted-foreground">
                Yes, we offer a 30-day money-back guarantee. If you're not satisfied, contact us for a full refund.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Preserve Your Family's Story?
          </h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Start with our free trial. No credit card required.
          </p>
          <Link to="/signup">
            <Button size="lg">
              Start Your Free Documentary
            </Button>
          </Link>
        </div>
      </section>
    </div>
  )
}
