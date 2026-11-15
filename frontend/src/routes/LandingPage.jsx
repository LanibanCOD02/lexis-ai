import React from 'react';
import { Scale, Search, ArrowRight, Link2, BookOpen, Layers, CheckCircle2, ChevronRight, FileText, ArrowDown } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useScrollReveal, useParallax, useCinematicParallax } from '../hooks/useScrollReveal';

// Reusable Reveal Wrapper Component
const RevealSection = ({ children, delay = 0, className = "" }) => {
  const [ref, isVisible] = useScrollReveal({ threshold: 0.1, rootMargin: '0px' });
  return (
    <div 
      ref={ref} 
      className={`reveal-hidden ${isVisible ? 'reveal-visible' : ''} ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
};

const TextRevealLine = ({ text, delay = 0, emphasisWord = null, emphasisDelay = 0 }) => {
  const [ref, isVisible] = useScrollReveal({ threshold: 0.5, rootMargin: '0px' });
  
  // Split the text into words for staggered deposition-style typing effect
  const words = text.split(' ');

  return (
    <div ref={ref} className="flex flex-wrap items-center justify-center gap-x-3 md:gap-x-4 lg:gap-x-5 w-full mb-2 lg:mb-4">
      {words.map((word, i) => {
        // Precise match against the emphasis word (handling trailing punctuation in the prop if necessary)
        const isEmphasis = word === emphasisWord;
        
        // Stagger the fade-in of each word by 150ms to simulate typing
        const wordDelay = delay + (i * 150);
        
        return (
          <span
            key={i}
            className={`
              transition-all duration-[800ms] ease-out inline-block
              ${isVisible ? 'opacity-100 translate-y-0 filter-none' : 'opacity-0 translate-y-3 blur-[3px]'}
              ${isEmphasis 
                ? 'font-serif italic font-medium text-[#fdfdfc] text-4xl sm:text-5xl md:text-6xl lg:text-[80px] leading-[1.2] shimmer-text px-1' 
                : 'font-sans font-medium text-4xl sm:text-5xl md:text-6xl lg:text-[76px] leading-[1.2] tracking-tight text-white/95'
              }
            `}
            style={{ 
              transitionDelay: `${wordDelay}ms`,
              animationDelay: isEmphasis ? `${(wordDelay / 1000) + 0.8}s` : undefined
            }}
            data-text={isEmphasis ? word : undefined}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};

// 6-Step Hero Live Research Object
const HeroResearchObject = ({ isVisible }) => {
  return (
    <div style={{ transform: 'translateY(calc(var(--scroll-y, 0) * 0.1px + var(--mouse-y, 0) * 2px))' }} className="w-full max-w-[420px] mx-auto md:mx-0 md:ml-auto relative">
      
      {/* DOCUMENT COMPOSITION */}
      <div className={`w-full aspect-[3/4] bg-surface border border-border/60 rounded shadow-[0_12px_40px_rgb(0,0,0,0.06),0_1px_3px_rgb(0,0,0,0.02)] p-8 md:p-10 relative flex flex-col ${isVisible ? 'hero-reveal-visible' : ''} living-document overflow-hidden`}>
      
        {/* Subtle Document Materiality */}
        <div className="absolute inset-0 bg-paper-texture opacity-50 mix-blend-multiply pointer-events-none z-0"></div>
        <div className="absolute left-6 md:left-8 top-0 bottom-0 w-px bg-red-900/5 z-0"></div>
        <div className="absolute left-10 md:left-12 top-0 bottom-0 w-px bg-border/20 z-0"></div>
        <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-bl from-border/20 to-transparent pointer-events-none z-0"></div>

        {/* The Optical Search Beam (Ambient Motion) */}
        <div className="absolute left-0 right-0 h-[80px] bg-gradient-to-b from-transparent via-primary/5 to-transparent pointer-events-none z-30 optical-search-beam"></div>

        {/* [ RETRIEVED ] Tag */}
        <div className="absolute left-6 md:left-8 top-[115px] z-20 flex items-center living-retrieved hidden md:flex">
          <div className="text-[9px] font-mono text-muted/70 tracking-widest uppercase whitespace-nowrap bg-surface px-1">
            [ RETRIEVED ]
          </div>
          <svg width="40" height="1" className="text-border/60 ml-2" style={{ strokeWidth: 0.5, stroke: 'currentColor', fill: 'none' }}>
             <path d="M 0,0.5 L 40,0.5" />
          </svg>
        </div>

        {/* Internal CITATION 07 (Desktop only, inside document lower right) */}
        <div className="absolute right-8 bottom-12 z-20 hidden md:flex flex-col items-center living-citation" style={{ transform: 'translateY(calc(var(--scroll-y, 0) * 0.16px + var(--mouse-y, 0) * 3px))' }}>
          <svg width="1" height="60" className="text-border/60 mb-2" style={{ strokeWidth: 0.5, stroke: 'currentColor', fill: 'none' }}>
             <path d="M 0.5,0 L 0.5,60" />
          </svg>
          <div className="text-[9px] font-mono text-primary/80 tracking-widest uppercase whitespace-nowrap bg-surface px-1">
            [ CITATION 07 ]
          </div>
          <svg width="1" height="20" className="text-primary/40 mt-2 mb-2" style={{ strokeWidth: 0.5, stroke: 'currentColor', fill: 'none' }}>
             <path d="M 0.5,0 L 0.5,20" />
          </svg>
          <div className="text-[8px] font-mono text-muted/60 tracking-widest uppercase whitespace-nowrap">
            SOURCE VERIFIED
          </div>
        </div>

        {/* Step 1: Document Structure */}
        <div className="relative z-10 living-text-layer">
          <div className="absolute right-0 top-0 text-[8px] font-mono text-muted/40 tracking-widest text-right leading-relaxed">
            CASE NO. 2024-88A<br/>
            PAGE 48 / 112
          </div>
          <div className="w-full h-px bg-border/30 mt-12 mb-8"></div>
        </div>
        
        {/* Step 2: Legal Text Resolves */}
        <div className="relative z-10 flex flex-col gap-4 living-text-layer">
          <div className="flex flex-col gap-2">
            <div className="w-full h-1 bg-muted/10 rounded-sm"></div>
            <div className="w-[95%] h-1 bg-muted/10 rounded-sm"></div>
            <div className="w-[85%] h-1 bg-muted/10 rounded-sm"></div>
            <div className="w-[90%] h-1 bg-muted/10 rounded-sm"></div>
            <div className="w-[60%] h-1 bg-muted/10 rounded-sm"></div>
          </div>
          
          <div className="flex items-center gap-2 my-2">
            <span className="text-[7px] text-muted/40 font-mono">§ 11.2</span>
            <div className="flex-1 h-px bg-border/20"></div>
          </div>

          <div className="flex flex-col gap-2">
            <div className="w-[90%] h-1 bg-muted/10 rounded-sm"></div>
            <div className="w-full h-1 bg-muted/10 rounded-sm"></div>
          </div>
        </div>
        
        <div className="relative z-10 mt-6 living-highlight-layer">
          {/* Step 3: Highlight Sweep over text */}
          <div className="relative pl-4 py-2">
            <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-[#D4AF37]/40 rounded-sm living-highlight-bar"></div>
            <div className="font-serif italic text-xs md:text-[13px] text-foreground/85 leading-relaxed living-highlight-text">
              "The referral court under Section 11 must limit its inquiry to a prima facie examination of the arbitration agreement's existence, leaving contested matters to the tribunal..."
            </div>
          </div>

          {/* Layout Row for Post-passage and Annotations */}
          <div className="flex flex-row justify-between items-start gap-4 mt-8">
            
            {/* Paragraph 3 (Post-passage) left side */}
            <div className="flex-1 flex flex-col gap-3 mt-2 living-text-layer opacity-60">
              <div className="w-[100%] h-1 bg-muted/20 rounded-sm"></div>
              <div className="w-[95%] h-1 bg-muted/20 rounded-sm"></div>
              <div className="w-[85%] h-1 bg-muted/20 rounded-sm"></div>
              <div className="w-[90%] h-1 bg-muted/20 rounded-sm"></div>
              <div className="w-[60%] h-1 bg-muted/20 rounded-sm"></div>
            </div>

            {/* Internal Annotations Column (Desktop) */}
            <div className="hidden md:flex flex-col gap-5 w-[140px] shrink-0 relative opacity-0 animate-[fade-in_0.5s_ease-out_1.2s_forwards] pt-2">
               
               {/* Precise Legal Markup Leader Lines */}
               <svg className="absolute bottom-full right-[120px] w-[60px] h-[32px] text-border/60 overflow-visible pointer-events-none">
                  {/* Draws from bottom of highlight down, then right, then down to annotation label */}
                  <path d="M -20,-24 L -20,-10 L 10,-10 L 10,8" fill="none" stroke="currentColor" strokeWidth="0.5" />
               </svg>
               <svg className="absolute bottom-full right-[120px] w-[60px] h-[32px] text-primary/40 overflow-visible pointer-events-none" style={{ animationDelay: '1.6s' }}>
                  <path d="M -40,-24 L -40,-16 L -10,-16 L -10,50" fill="none" stroke="currentColor" strokeWidth="0.5" className="opacity-0 animate-[fade-in_0.5s_ease-out_1.6s_forwards]" />
               </svg>

               <div className="flex flex-col relative pl-3">
                 <div className="absolute left-0 top-0 bottom-0 w-[0.5px] bg-border/40"></div>
                 <div className="text-[8px] font-mono text-muted/60 tracking-widest uppercase mb-1">Legal Principle</div>
                 <div className="text-[10px] font-serif italic text-foreground/90 leading-relaxed">Prima facie examination of the arbitration agreement.</div>
               </div>
               
               <div className="flex flex-col relative pl-3 opacity-0 animate-[fade-in_0.5s_ease-out_1.6s_forwards]">
                 <div className="absolute left-0 top-0 bottom-0 w-[0.5px] bg-primary/30"></div>
                 <div className="text-[8px] font-mono text-primary/70 tracking-widest uppercase mb-1">Reasoning</div>
                 <div className="text-[10px] font-serif italic text-foreground/80 leading-relaxed">Complex factual disputes remain for the tribunal.</div>
               </div>
            </div>
          </div>
          
          {/* Mobile Stacked Annotations (Visible only on < 768px) */}
          <div className="md:hidden w-full flex flex-col gap-5 living-text-layer opacity-0 animate-[fade-in_0.5s_ease-out_1.2s_forwards] mt-6 pl-4 border-l border-primary/20">
             <div className="flex flex-col">
               <div className="text-[9px] font-mono text-primary/70 tracking-widest uppercase mb-1">Legal Principle</div>
               <div className="text-[11px] font-serif italic text-foreground/90 leading-relaxed">Prima facie examination of the arbitration agreement.</div>
             </div>
             <div className="flex flex-col">
               <div className="text-[9px] font-mono text-primary/70 tracking-widest uppercase mb-1">Reasoning</div>
               <div className="text-[11px] font-serif italic text-foreground/80 leading-relaxed">Complex factual disputes remain for the tribunal.</div>
             </div>
             <div className="flex items-center gap-3 pt-2">
               <div className="text-[9px] font-mono text-primary/80 tracking-widest uppercase border border-primary/20 bg-primary/5 px-2 py-1 rounded-sm">
                 [ CITATION 07 ]
               </div>
               <div className="w-4 h-px bg-border/40"></div>
               <div className="text-[9px] font-mono font-medium text-foreground/80 tracking-widest uppercase">
                 Source Verified
               </div>
             </div>
          </div>

        </div>
      </div>

    </div>
  );
};

// D. Sophisticated Citation Network Animation
const AnimatedNetwork = () => {
  const [ref, isVisible] = useScrollReveal({ threshold: 0.1, rootMargin: '0px' });
  
  return (
    <div ref={ref} className={`relative w-full aspect-[4/3] md:aspect-[16/9] bg-surface border border-border rounded overflow-hidden flex items-center justify-center ${isVisible ? 'reveal-visible' : ''}`}>
      {/* Subtle Texture */}
      <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, #0f172a 1px, transparent 0)', backgroundSize: '24px 24px' }}></div>
      
      {/* SVG Connecting Lines - Drawn with stroke-dashoffset */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 5 }}>
        {/* Central Vertical */}
        <line x1="50%" y1="20%" x2="50%" y2="40%" stroke="#e2e8f0" strokeWidth="1.5" className="network-line" style={{ transitionDelay: '0.2s' }} />
        {/* Horizontal Split */}
        <line x1="20%" y1="40%" x2="80%" y2="40%" stroke="#e2e8f0" strokeWidth="1.5" className="network-line" style={{ transitionDelay: '0.4s' }} />
        {/* Down to Nodes */}
        <line x1="20%" y1="40%" x2="20%" y2="60%" stroke="#e2e8f0" strokeWidth="1.5" className="network-line" style={{ transitionDelay: '0.6s' }} />
        <line x1="50%" y1="40%" x2="50%" y2="60%" stroke="#e2e8f0" strokeWidth="1.5" className="network-line" style={{ transitionDelay: '0.7s' }} />
        <line x1="80%" y1="40%" x2="80%" y2="60%" stroke="#e2e8f0" strokeWidth="1.5" className="network-line" style={{ transitionDelay: '0.8s' }} />
        {/* Reconnect Horizontal */}
        <line x1="20%" y1="70%" x2="80%" y2="70%" stroke="#e2e8f0" strokeWidth="1.5" className="network-line" style={{ transitionDelay: '1.2s' }} />
        {/* Down to Source */}
        <line x1="50%" y1="70%" x2="50%" y2="85%" stroke="#e2e8f0" strokeWidth="1.5" className="network-line" style={{ transitionDelay: '1.4s' }} />
      </svg>

      {/* Nodes - Staggered appearance */}
      <div className="absolute top-[15%] left-1/2 -translate-x-1/2 -translate-y-1/2 z-10 flex flex-col items-center network-node" style={{ transitionDelay: '0s' }}>
        <div className="w-16 h-16 rounded-full border border-primary/20 bg-primary/5 flex items-center justify-center relative shadow-sm">
          <div className="absolute inset-0 rounded-full border border-primary/30 animate-[ping_4s_ease-out_infinite] opacity-20"></div>
          <Scale size={20} className="text-primary" />
        </div>
        <span className="absolute top-full mt-2 text-[10px] font-semibold text-primary uppercase tracking-widest bg-surface px-1">CASE</span>
      </div>

      <div className="absolute top-[60%] left-[20%] -translate-x-1/2 -translate-y-1/2 z-10 flex flex-col items-center network-node" style={{ transitionDelay: '0.9s' }}>
        <div className="w-10 h-10 rounded-full border border-border bg-background flex items-center justify-center text-[10px] text-muted shadow-sm">
          <BookOpen size={14} />
        </div>
        <span className="absolute top-full mt-2 text-[10px] font-semibold text-muted uppercase tracking-widest bg-surface px-1">PRINCIPLE</span>
      </div>

      <div className="absolute top-[60%] left-[50%] -translate-x-1/2 -translate-y-1/2 z-10 flex flex-col items-center network-node" style={{ transitionDelay: '1.0s' }}>
        <div className="w-12 h-12 rounded-full border border-[#D4AF37]/30 bg-[#D4AF37]/5 flex items-center justify-center text-[#b4975a] shadow-sm">
          <Scale size={16} />
        </div>
        <span className="absolute top-full mt-2 text-[10px] font-semibold text-[#b4975a] uppercase tracking-widest bg-surface px-1">PRECEDENT</span>
      </div>

      <div className="absolute top-[60%] left-[80%] -translate-x-1/2 -translate-y-1/2 z-10 flex flex-col items-center network-node" style={{ transitionDelay: '1.1s' }}>
        <div className="w-10 h-10 rounded-full border border-border bg-background flex items-center justify-center text-[10px] text-muted shadow-sm">
          <Layers size={14} />
        </div>
        <span className="absolute top-full mt-2 text-[10px] font-semibold text-muted uppercase tracking-widest bg-surface px-1">ISSUE</span>
      </div>

      <div className="absolute top-[85%] left-[50%] -translate-x-1/2 -translate-y-1/2 z-10 flex flex-col items-center network-node" style={{ transitionDelay: '1.8s' }}>
        <div className="w-10 h-10 bg-foreground text-white rounded border border-border flex items-center justify-center shadow-sm">
          <FileText size={14} />
        </div>
        <span className="absolute top-full mt-2 text-[10px] font-semibold text-foreground uppercase tracking-widest bg-surface px-1">SOURCE</span>
      </div>
    </div>
  );
}

// 1. Premium Global Navigation
const Navbar = () => {
  const [scrolled, setScrolled] = React.useState(false);

  React.useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 40);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className={`fixed top-0 left-0 w-full z-50 transition-all duration-300 ease-out bg-[#F7F5F0] border-b border-border/30 shadow-[0_4px_24px_rgb(0,0,0,0.03)] py-3 md:py-4 bg-legal-texture mix-blend-normal`}>
      <nav className="w-full max-w-[1280px] mx-auto px-6 md:px-12 lg:px-16 flex items-center justify-between relative z-10">
        <div className="flex items-center gap-3 group cursor-pointer w-auto pr-10">
          <Scale size={28} className="text-primary transition-all duration-300 group-hover:scale-[1.02] group-hover:-translate-y-[1px] group-hover:brightness-110" />
          <span className="font-serif font-medium text-2xl text-foreground tracking-tight transition-transform duration-300 group-hover:-translate-y-[1px]">Lexis AI</span>
        </div>
        <div className="hidden md:flex gap-12 items-center justify-center flex-1">
          <a href="#" className="nav-link-premium text-sm font-medium text-muted hover:text-primary transition-colors duration-300 pb-1">Platform</a>
          <a href="#" className="nav-link-premium text-sm font-medium text-muted hover:text-primary transition-colors duration-300 pb-1">How it works</a>
          <a href="#" className="nav-link-premium text-sm font-medium text-muted hover:text-primary transition-colors duration-300 pb-1">Security</a>
        </div>
        <div className="flex items-center justify-end gap-4 lg:gap-6 min-w-fit">
          <Link to="/login" className="nav-link-premium text-sm font-medium text-muted hover:text-foreground transition-colors duration-300 pb-1 whitespace-nowrap">
            Sign In
          </Link>
          <Link to="/login" className="btn-premium hidden sm:flex items-center justify-center gap-2 px-5 py-2.5 bg-foreground text-white text-sm font-medium rounded hover:bg-primary transition-all duration-300 shadow-sm hover:shadow-md group hover:-translate-y-[2px] whitespace-nowrap flex-shrink-0 h-[44px]">
            Enter Workspace
            <ArrowRight size={14} className="transition-transform duration-300 group-hover:translate-x-1" />
          </Link>
        </div>
      </nav>
    </div>
  );
};





// -----------------------------------------------------------------------------
// Precision Folio Stack + Editorial Rows
// -----------------------------------------------------------------------------





// -----------------------------------------------------------------------------
// Precision Alternating Cascade Sequence
// -----------------------------------------------------------------------------
const PrecisionScrollSequence = () => {
  const containerRef = React.useRef(null);
  const [revealedCount, setRevealedCount] = React.useState(0);
  const [hasTriggered, setHasTriggered] = React.useState(false);

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting && !hasTriggered) {
          setHasTriggered(true);
        }
      },
      { threshold: 0.4 }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, [hasTriggered]);

  React.useEffect(() => {
    if (hasTriggered && revealedCount < 5) {
      // 800ms stagger for a majestic, deliberate reveal
      const timer = setTimeout(() => {
        setRevealedCount(prev => prev + 1);
      }, 800);
      return () => clearTimeout(timer);
    }
  }, [hasTriggered, revealedCount]);

  const steps = [
    { title: "01 AI SEARCH", meta: "CORPUS 1.8M+  //  LATENCY 14ms" },
    { title: "02 RELEVANT CHUNK", meta: "RANKING 0.97  //  EMBEDDING MATCH" },
    { title: "03 LEGAL REASONING", meta: "LOGIC EXTRACTION  //  PRECEDENT" },
    { title: "04 CITATION", meta: "CROSS-REFERENCE  //  BLUEBOOK" },
    { title: "05 VERIFIED SOURCE", meta: "SOURCE PRIMARY  //  IMMUTABLE" },
  ];

  return (
    <section 
      ref={containerRef} 
      className="w-full min-h-screen bg-[#FAF9F6] relative overflow-hidden flex flex-col items-center py-40"
    >
      {/* Section Headline */}
      <div className={`mb-32 transition-all duration-[1500ms] ease-out text-center ${hasTriggered ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'}`}>
        <h2 className="font-serif italic text-xl md:text-2xl text-[#0A192F]/60">
          The intelligence is in the evidence.
        </h2>
      </div>

      <div className="w-full max-w-7xl mx-auto px-6 relative z-10">
        
        {/* The Central Calibration Axis */}
        <div className="absolute left-1/2 top-0 bottom-0 w-[1px] bg-[#0A192F]/20 z-0 pointer-events-none -translate-x-1/2"></div>

        {/* The Alternating Cascade */}
        <div className="flex flex-col gap-16 md:gap-20 relative w-full">
          {steps.map((step, idx) => {
            const isRevealed = idx < revealedCount;
            const isRightSide = idx % 2 === 0;

            // Optical Focus State
            const opacity = isRevealed ? 'opacity-100' : 'opacity-0';
            const blur = isRevealed ? 'blur-0' : 'blur-[12px]';
            
            // Transform direction depends on which side it's on
            let transform = 'scale-100 translate-x-0';
            if (!isRevealed) {
               transform = isRightSide ? 'scale-[0.96] translate-x-16' : 'scale-[0.96] -translate-x-16';
            }

            const metaOpacity = isRevealed ? 'opacity-100' : 'opacity-0';
            const metaTransform = isRevealed ? 'translate-x-0' : (isRightSide ? '-translate-x-6' : 'translate-x-6');

            return (
              <div key={idx} className="w-full relative flex">
                
                {isRightSide ? (
                  // ---------------- RIGHT SIDE LAYOUT ----------------
                  <div className="w-1/2 ml-auto pl-6 md:pl-12 flex flex-col md:flex-row md:items-baseline justify-start relative">
                    {/* The connector dot on the axis */}
                    <div className={`absolute left-0 top-1/2 -translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-[#0A192F] transition-all duration-1000 delay-300 ${isRevealed ? 'opacity-100 scale-100' : 'opacity-0 scale-0'}`}></div>
                    
                    <h3 className={`font-serif text-3xl md:text-5xl lg:text-6xl tracking-tight whitespace-nowrap transition-all duration-[1200ms] ease-[cubic-bezier(0.2,0.8,0.2,1)] text-[#0A192F] origin-left ${opacity} ${blur} ${transform}`}>
                      {step.title}
                    </h3>
                    
                    <div className={`mt-2 md:mt-0 ml-0 md:ml-10 flex items-center gap-4 transition-all duration-[1000ms] delay-[600ms] ease-out ${metaOpacity} ${metaTransform}`}>
                      <div className="hidden md:block w-6 h-[1px] bg-[#0047AB]/30"></div>
                      <span className="font-mono text-[8px] tracking-[0.25em] text-[#0A192F]/60 font-semibold uppercase">
                        {step.meta}
                      </span>
                    </div>
                  </div>
                ) : (
                  // ---------------- LEFT SIDE LAYOUT ----------------
                  <div className="w-1/2 mr-auto pr-6 md:pr-12 flex flex-col md:flex-row md:items-baseline justify-end relative text-right">
                    {/* The connector dot on the axis */}
                    <div className={`absolute right-0 top-1/2 translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-[#0A192F] transition-all duration-1000 delay-300 ${isRevealed ? 'opacity-100 scale-100' : 'opacity-0 scale-0'}`}></div>

                    <div className={`hidden md:flex mt-2 md:mt-0 mr-10 items-center flex-row-reverse gap-4 transition-all duration-[1000ms] delay-[600ms] ease-out ${metaOpacity} ${metaTransform}`}>
                      <div className="w-6 h-[1px] bg-[#0047AB]/30"></div>
                      <span className="font-mono text-[8px] tracking-[0.25em] text-[#0A192F]/60 font-semibold uppercase">
                        {step.meta}
                      </span>
                    </div>

                    <h3 className={`font-serif text-3xl md:text-5xl lg:text-6xl tracking-tight whitespace-nowrap transition-all duration-[1200ms] ease-[cubic-bezier(0.2,0.8,0.2,1)] text-[#0A192F] origin-right ${opacity} ${blur} ${transform}`}>
                      {step.title}
                    </h3>
                    
                    {/* Mobile metadata (shown below text on small screens) */}
                    <div className={`md:hidden mt-2 flex items-center justify-end gap-4 transition-all duration-[1000ms] delay-[600ms] ease-out ${metaOpacity} ${metaTransform}`}>
                      <span className="font-mono text-[8px] tracking-[0.25em] text-[#0A192F]/60 font-semibold uppercase">
                        {step.meta}
                      </span>
                    </div>
                  </div>
                )}
                
              </div>
            );
          })}
        </div>
        
      </div>
    </section>
  );
};
// -----------------------------------------------------------------------------





const LandingPage = () => {
  // Parallax hooks
  const [blueSectionRef, blueBgOffset] = useParallax(0.12);
  const [, textureOffset] = useParallax(0.20);
  const [, decoOffset] = useParallax(-0.05);
  
  // Hero Cinematic Parallax (tracks scroll & mouse)
  const heroContainerRef = useCinematicParallax();

  const [workflowRef, workflowIsVisible] = useScrollReveal({ threshold: 0.3 });
  const [flowchartRef, flowchartIsVisible] = useScrollReveal({ threshold: 0.4 });
  const [heroVisibleRef, heroIsVisible] = useScrollReveal({ threshold: 0.1 });

  return (
      <div className="min-h-screen bg-background text-foreground font-sans selection:bg-primary selection:text-white bg-paper-texture relative overflow-x-hidden w-full max-w-[100vw]">
      
      <Navbar />

      <main className="w-full flex flex-col">
        
        {/* 2. Editorial Hero (Cinematic Parallax Controlled) */}
        <section ref={heroContainerRef} className="relative w-full max-w-[1280px] mx-auto px-6 md:px-12 lg:px-16 pt-32 lg:pt-40 pb-32 flex flex-col md:flex-row items-start justify-between gap-10 md:gap-16 min-h-[90vh] md:min-h-screen overflow-x-clip">
          
          {/* Subtle Vertical Rules (Parallax Layer 2) */}
          <div className="absolute inset-x-0 bottom-0 top-24 pointer-events-none overflow-hidden flex justify-between px-6 md:px-12 lg:px-16 z-0" style={{ transform: 'translateY(calc(var(--scroll-y, 0) * -0.04px))' }}>
            <div className="w-px h-[200%] bg-gradient-to-b from-transparent via-border/30 to-transparent transform -translate-y-1/4"></div>
            <div className="w-px h-[200%] bg-gradient-to-b from-transparent via-border/30 to-transparent transform -translate-y-1/4"></div>
            {/* Registration marks */}
            <div className="absolute top-[15%] left-0 w-full flex justify-between px-6 md:px-12 lg:px-16 text-muted/30 text-[8px] font-mono">
              <span>+</span><span>+</span>
            </div>
            <div className="absolute bottom-[20%] left-0 w-full flex justify-between px-6 md:px-12 lg:px-16 text-muted/30 text-[8px] font-mono">
              <span>+</span><span>+</span>
            </div>
          </div>
          
          {/* Environmental Metadata (Parallax Layer 1) */}
          <div className="absolute inset-0 pointer-events-none overflow-hidden z-0 hidden md:block" style={{ transform: 'translateY(calc(var(--scroll-y, 0) * -0.02px + var(--mouse-y, 0) * -1px))' }}>
            
            {/* Top architectural marker */}
            <div className="absolute top-24 md:top-32 left-6 md:left-12 lg:left-16 flex items-center gap-4 text-[9px] font-mono text-muted/60 tracking-widest uppercase cinematic-enter-description">
              <span className="font-semibold text-foreground/70">01 / COMMERCIAL LITIGATION INTELLIGENCE</span>
              <div className="w-12 h-px bg-border/40"></div>
            </div>

            {/* Lower Information Rail */}
            <div className="absolute bottom-12 left-0 right-0 px-6 md:px-12 lg:px-16 flex items-end justify-between cinematic-enter-description border-t border-border/40 pt-4">
              
              <div className="flex gap-8 lg:gap-16">
                <div className="flex flex-col gap-1">
                  <span className="text-[8px] font-mono text-muted/50 tracking-widest uppercase">01 RESEARCH ENGINE</span>
                  <span className="text-[9px] font-mono text-foreground/70 tracking-widest uppercase">SEMANTIC RETRIEVAL</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-[8px] font-mono text-muted/50 tracking-widest uppercase">02 EVIDENCE</span>
                  <span className="text-[9px] font-mono text-foreground/70 tracking-widest uppercase">VERBATIM CITATIONS</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-[8px] font-mono text-muted/50 tracking-widest uppercase">03 SOURCE</span>
                  <span className="text-[9px] font-mono text-foreground/70 tracking-widest uppercase">PAGE-LEVEL VERIFICATION</span>
                </div>
              </div>
              
              {/* Scroll Indicator integrated into rail */}
              <div className="flex flex-col items-end gap-2">
                <span className="text-[8px] font-mono text-muted tracking-widest uppercase">SCROLL TO EXPLORE</span>
                <div className="h-4 w-px bg-gradient-to-b from-muted to-transparent animate-[living-float-small_2s_ease-in-out_infinite]"></div>
              </div>

            </div>
          </div>
          
          {/* Subtle SVG Evidence Beam from Headline to Research Object */}
          <div className="hidden lg:block absolute left-[45%] top-[55%] w-[15%] h-[50px] pointer-events-none z-10" style={{ transform: 'translateX(-50%)' }}>
            <svg className="w-full h-full overflow-visible" viewBox="0 0 100 50" preserveAspectRatio="none">
              <path 
                d="M 0,25 C 40,25 60,0 100,0" 
                fill="none" 
                stroke="currentColor" 
                className={`text-border/60 hero-cross-beam ${heroIsVisible ? 'hero-reveal-visible' : ''}`} 
                strokeWidth="1" 
                strokeDasharray="100" 
                pathLength="100"
                style={{ transitionDelay: '2s' }} 
              />
            </svg>
          </div>

          <div ref={heroVisibleRef} className={`flex-1 flex flex-col items-start text-left z-10 ${heroIsVisible ? 'hero-reveal-visible' : ''}`} style={{ transform: 'translateY(calc(var(--scroll-y, 0) * 0.02px))' }}>
            
            <h1 className="font-serif font-medium text-5xl md:text-6xl lg:text-7xl text-foreground leading-[1.1] tracking-tight max-w-2xl cinematic-enter-headline mt-12">
              Precision AI for <br/>
              <span className="text-primary italic relative inline-block living-shimmer-text" data-text="evidence-driven">
                evidence-driven
              </span> <br/>
              legal research.
            </h1>
            
            <p className="mt-8 text-lg md:text-xl text-muted leading-relaxed max-w-xl font-medium cinematic-enter-description">
              The deterministic RAG engine designed exclusively for commercial courts. Grounded entirely in verbatim citations, preventing hallucinations instantly.
            </p>
            
            <div className="mt-12 flex flex-col sm:flex-row items-center gap-5 cinematic-enter-description">
              <Link to="/login" className="btn-premium group flex items-center justify-center gap-3 px-8 py-4 bg-foreground text-white text-base font-medium rounded hover:bg-primary transition-all duration-300 shadow-sm hover:shadow-md hover:-translate-y-[2px]">
                Start Researching
                <ArrowRight size={16} className="transition-transform duration-300 group-hover:translate-x-[4px]" />
              </Link>
            </div>

          </div>
          
          {/* Research Object (Parallax Layer 3) */}
          <div className="flex-1 w-full hidden md:flex flex-col items-end z-10 relative md:mr-8 lg:mr-12">
            {/* System Status */}
            <div className="flex flex-col items-end gap-1 cinematic-enter-description text-right mb-4 w-full max-w-md">
               <div className="flex items-center gap-2 text-[9px] font-mono text-primary/80 tracking-widest uppercase">
                  <span className="w-1.5 h-1.5 bg-primary/80 rounded-full animate-pulse"></span>
                  STATUS · ONLINE
               </div>
               <div className="text-[8px] font-mono text-muted/50 tracking-widest uppercase">
                  LATENCY 42MS
               </div>
            </div>
            <HeroResearchObject isVisible={heroIsVisible} />
          </div>

        </section>

        {/* 3. Brand Manifesto (The Visual Centerpiece) */}
        <section 
          ref={blueSectionRef}
          className="relative w-full bg-[#0a192f] text-white py-48 md:py-64 px-6 overflow-hidden flex flex-col items-center justify-center border-t border-border/40"
        >
          {/* Architectural/legal graphic layer (Parallax Deco) */}
          <div 
            className="absolute inset-0 pointer-events-none flex justify-between items-center opacity-[0.06] px-10 md:px-32 mix-blend-overlay"
            style={{ transform: `translateY(${decoOffset}px)` }}
          >
            <div className="h-[200%] w-px bg-white transform -rotate-12"></div>
            <div className="h-[200%] w-px bg-white transform rotate-12"></div>
          </div>
          
          <div 
            className="absolute inset-0 bg-[#061124] opacity-80 w-full h-[150%] -top-[25%] pointer-events-none"
            style={{ transform: `translateY(${blueBgOffset}px)` }}
          ></div>

          <div 
            className="absolute inset-0 bg-legal-texture w-full h-[150%] -top-[25%] pointer-events-none mix-blend-soft-light"
            style={{ transform: `translateY(${textureOffset}px)` }}
          ></div>

          <div className="relative z-10 w-full max-w-[1280px] mx-auto px-6 md:px-12 lg:px-16 flex flex-col items-center text-center gap-6 md:gap-8 overflow-hidden">
            <TextRevealLine text="RESEARCH THE LAW." emphasisWord="LAW." delay={100} emphasisDelay={1.5} />
            <TextRevealLine text="UNDERSTAND THE REASONING." emphasisWord="REASONING." delay={400} emphasisDelay={3.5} />
            <TextRevealLine text="TRACE THE EVIDENCE." emphasisWord="EVIDENCE." delay={700} emphasisDelay={5.5} />
          </div>
        </section>

        {/* 4. Product Intelligence Explanation (Cinematic Ledger) */}
        <PrecisionScrollSequence />
        
        {/* 5. Product Story (Visual Workflow Beam) */}
        <section className="w-full max-w-7xl mx-auto py-40 px-6">
          <div ref={workflowRef} className={`grid md:grid-cols-4 gap-12 relative ${workflowIsVisible ? 'reveal-visible' : ''}`}>
             
             {/* Animated SVG connecting beam */}
             <div className="hidden md:block absolute top-[40px] left-[12%] right-[12%] h-1 z-0">
               <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 2">
                 <line x1="0" y1="1" x2="100" y2="1" stroke="#e2e8f0" strokeWidth="2" />
                 <line x1="0" y1="1" x2="100" y2="1" stroke="#3366cc" strokeWidth="2" className="workflow-beam" pathLength="1000" />
               </svg>
             </div>
             
             {[
               { icon: <FileText size={20}/>, title: "Upload Judgment", num: "01" },
               { icon: <Search size={20}/>, title: "Semantic Search", num: "02" },
               { icon: <Layers size={20}/>, title: "Analyze Reasoning", num: "03" },
               { icon: <Link2 size={20}/>, title: "Verify Citations", num: "04" }
             ].map((step, idx) => (
               <div key={idx} className="flex flex-col items-center text-center relative z-10 flow-item" style={{ transitionDelay: `${idx * 0.5}s` }}>
                 <div className="w-20 h-20 bg-background border border-border rounded-full flex flex-col items-center justify-center text-primary mb-6 shadow-sm hover:border-primary/50 transition-colors duration-300">
                   <div className="text-[9px] text-muted font-mono mb-1">{step.num}</div>
                   {step.icon}
                 </div>
                 <h3 className="font-sans font-semibold text-base text-foreground">{step.title}</h3>
               </div>
             ))}
          </div>
        </section>

        {/* 6. Evidence Visualization */}
        <section className="w-full bg-[#f8fafc] border-y border-border py-40 px-6 overflow-hidden bg-paper-texture">
          <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-24 items-center relative z-10">
            <div className="flex flex-col gap-8 order-2 lg:order-1">
              <RevealSection>
                <div className="w-1 h-12 bg-primary mb-6"></div>
                <h2 className="font-serif font-medium text-4xl md:text-5xl text-foreground leading-tight">
                  Deterministic Graph Resolution
                </h2>
                <p className="text-lg text-muted leading-relaxed mt-6">
                  Lexis AI maps incoming references against a verified FAISS index, drawing deterministic relationships between source materials and cited precedent. Every node is mathematically traceable.
                </p>
                <ul className="flex flex-col gap-5 mt-10">
                  {[
                    "Identify pivotal cases instantly.",
                    "Verify original context with single-click SourceViewer.",
                    "Extract structured legal principles automatically."
                  ].map((item, i) => (
                    <li key={i} className="flex items-start gap-4">
                      <div className="mt-1 text-[#D4AF37]"><CheckCircle2 size={18} /></div>
                      <span className="text-foreground font-medium text-base">{item}</span>
                    </li>
                  ))}
                </ul>
              </RevealSection>
            </div>
            <div className="order-1 lg:order-2">
              <AnimatedNetwork />
            </div>
          </div>
        </section>

        {/* 7. Professional Standards (Editorial Columns) */}
        <section className="w-full max-w-7xl mx-auto py-40 px-6">
          <RevealSection>
             <div className="mb-20">
               <h2 className="font-serif font-medium text-3xl md:text-4xl text-foreground">Built for Professional Standards</h2>
             </div>
          </RevealSection>
          
          <div className="grid md:grid-cols-3 gap-12 md:gap-0">
             <RevealSection delay={100} className="md:border-r border-border md:pr-12 group cursor-default">
                <div className="text-xs font-mono text-muted mb-6 tracking-widest group-hover:text-primary transition-colors">01 / SECURITY</div>
                <h3 className="font-sans font-semibold text-xl text-foreground mb-4">Bank-grade Encrypted Isolation</h3>
                <p className="text-muted leading-relaxed text-sm">OAuth2 and JWT token-based authentication ensures client confidentiality. Your files never leave the isolated, encrypted VPC.</p>
             </RevealSection>
             <RevealSection delay={300} className="md:border-r border-border md:px-12 group cursor-default">
                <div className="text-xs font-mono text-muted mb-6 tracking-widest group-hover:text-primary transition-colors">02 / RETRIEVAL</div>
                <h3 className="font-sans font-semibold text-xl text-foreground mb-4">SQL-bridged FAISS Index</h3>
                <p className="text-muted leading-relaxed text-sm">High-dimensional vector search combined with deterministic relational databases guarantees absolute retrieval precision without hallucination.</p>
             </RevealSection>
             <RevealSection delay={500} className="md:pl-12 group cursor-default">
                <div className="text-xs font-mono text-muted mb-6 tracking-widest group-hover:text-primary transition-colors">03 / SPECIALIZATION</div>
                <h3 className="font-sans font-semibold text-xl text-foreground mb-4">Commercial Specialty Corpus</h3>
                <p className="text-muted leading-relaxed text-sm">A specialized dataset focusing entirely on commercial litigation, arbitration, and corporate tribunals for maximum domain accuracy.</p>
             </RevealSection>
          </div>
        </section>

        {/* 8. Final CTA */}
        <section className="w-full bg-[#0a192f] text-white py-32 px-6 relative overflow-hidden">
          <div className="absolute inset-0 pointer-events-none bg-legal-texture opacity-[0.03]"></div>
          <div className="max-w-4xl mx-auto flex flex-col items-center text-center relative z-10">
            <RevealSection>
              <Scale size={32} className="text-[#D4AF37] mb-8 mx-auto" />
              <h2 className="font-serif font-medium text-4xl md:text-5xl text-white leading-tight mb-12">
                Ready to elevate your legal research?
              </h2>
              <Link to="/login" className="btn-premium group inline-flex items-center justify-center gap-3 px-10 py-5 bg-white text-foreground text-lg font-medium rounded hover:bg-surface transition-all duration-300 shadow-md hover:shadow-lg hover:-translate-y-1">
                Enter Research Workspace 
                <ChevronRight size={20} className="transition-transform group-hover:translate-x-1" />
              </Link>
            </RevealSection>
          </div>
        </section>
        
      </main>

      {/* 9. Minimal footer */}
      <footer className="w-full border-t border-border py-12 px-6 bg-background">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2 text-muted">
            <Scale size={18} />
            <span className="text-sm font-medium tracking-wide">© 2026 LEXIS AI</span>
          </div>
          <div className="flex gap-8 text-sm font-medium text-muted">
            <a href="#" className="hover:text-foreground transition-colors nav-link-premium pb-1">Platform</a>
            <a href="#" className="hover:text-foreground transition-colors nav-link-premium pb-1">Privacy</a>
            <a href="#" className="hover:text-foreground transition-colors nav-link-premium pb-1">Terms of Service</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
