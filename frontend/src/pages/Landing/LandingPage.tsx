import Navbar from '../../components/landing/Navbar';
import HeroSection from '../../components/landing/HeroSection';
import FeaturesSection from '../../components/landing/FeaturesSection';
import HowItWorksSection from '../../components/landing/HowItWorksSection';
import PricingSection from '../../components/landing/PricingSection';
import FAQSection from '../../components/landing/FAQSection';
import CTASection from '../../components/landing/CTASection';
import FooterSection from '../../components/landing/FooterSection';
import ParticlesCanvas from '../../animations/ParticlesCanvas';

export default function LandingPage() {
  return (
    <div style={{ position: 'relative', minHeight: '100vh', background: 'var(--bg)' }}>
      <ParticlesCanvas count={30} />
      <Navbar />
      <HeroSection />
      <FeaturesSection />
      <HowItWorksSection />
      <PricingSection />
      <FAQSection />
      <CTASection />
      <FooterSection />
    </div>
  );
}
