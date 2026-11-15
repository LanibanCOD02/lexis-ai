# Lexis AI Landing Page Design System

## 1. Context & Purpose
The Landing Page serves as the expressive brand introduction. It stands in contrast to the Research Workspace (Dashboard).
- **Landing Page**: Expressive, cinematic, editorial, bold, memorable, story-driven.
- **Research Workspace (Dashboard)**: Calm, restrained, utilitarian, evidence-first, unopinionated UI.

## 2. Layout Structure
The landing page follows a distinct, deliberate visual narrative:
1. **Navigation**: Minimal. Sign In / Start Researching CTA. Underline expansion micro-interaction on hover.
2. **Editorial Hero**: Restrained but powerful. Strong typographic hierarchy. Not a massive SaaS gradient. Introduces the core concept: precision intelligence.
3. **The Brand Manifesto**: The visual centerpiece. Deep blue (`#0a192f`) background. Parallax depth. 
   - `RESEARCH THE LAW.`
   - `UNDERSTAND THE REASONING.`
   - `TRACE THE EVIDENCE.`
4. **Product Intelligence Story**: Sequential scroll-driven explanation.
5. **Evidence Visualization**: Abstract visualization of `AI -> Evidence -> Source`. Use 21st.dev-inspired network components, strictly styled in legal tones.
6. **Capabilities / Trust**: Grid emphasizing Semantic Engine, Verbatim Citations, and Security.
7. **Final CTA**: High-contrast, elegant exit point to the workspace.

## 3. Cinematic Motion & Texture
### Textures
- **Archival Paper**: Utilize `.bg-legal-texture` (an SVG fractal noise filter) rendered at ~10% opacity over dark sections.
- **Document Artifacts**: Faint grid marks, citation brackets, structural rules. 

### Parallax & Motion (21st.dev Adapted)
- **Layered Parallax**: Background slow, texture offset, typography minimal, foreground decorative elements opposing.
- **Reflective Shimmer**: A 21st.dev patterned `background-clip: text` gradient that slowly sweeps across the `Lora` keywords (`LAW`, `REASONING`, `EVIDENCE`). This creates the illusion of light passing over premium printed paper.
- **Staggered Reveal**: Sections fade in and slightly translate up via `IntersectionObserver`.

## 4. Strict Constraints
- **NO bleed over into the Dashboard**.
- **NO scroll-jacking**.
- **NO overwhelming animations**; the user should feel depth, not motion.
- **MUST respect `prefers-reduced-motion`** instantly overriding all parallax, shimmer, and translate animations.
