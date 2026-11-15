# Lexis AI Design System: Master Rules

## 1. Brand Identity & Direction
- **Identity**: Premium legal research platform. Authoritative, intelligent, precise, evidence-driven, editorial, trustworthy, and sophisticated.
- **Goal**: Reassure professionals immediately. Focus deeply on evidence and logical extraction (Case → Evidence → Analysis → AI Answer → Source).
- **Anti-patterns**: 
  - NO generic SaaS layouts or floating cards
  - NO AI neon aesthetics, 3D animated robots, pink/purple AI gradients
  - NO crypto-like styling or heavily glassmorphic elements
  - NO rainbow buttons or excessive shadows

## 2. Color System
- **Background**: Warm Ivory (`#fdfdfc`) to emulate archival document paper.
- **Surfaces**: Soft White (`#ffffff`) for elevated read areas.
- **Primary Text**: Deep Ink / Navy (`#0f172a`) for maximum editorial contrast and readability.
- **Secondary Text**: Muted Slate (`#475569`).
- **Signature Accent**: Deep Legal Blue/Navy (`#0a192f`). Used exclusively for the Brand Manifesto section.
- **Interactive Primary**: Restrained Blue (`#3366cc`).
- **Subtle Accent**: Muted Gold (`#D4AF37` or `#b4975a`), used sparingly for verification / citations.

## 3. Typography Hierarchy
- **Structural UI (Sans-Serif)**: `Manrope`. Used for navigation, labels, data points, buttons, and supporting structural information. (Weights: 400, 500, 600, 700).
- **Editorial Emphasis (Serif)**: `Lora`. Used exclusively for critical legal concepts, case titles, major headings, and the manifesto focus words. (Weights: 500, italic).

## 4. Spacing & Composition
- Emphasize generous whitespace to communicate confidence and clarity.
- Prefer tight grouping of related elements (Gestalt principles) and vast spacing between disparate sections.
- Borders: Restrained (`1px solid var(--color-border)`).
- Radii: Minimal. Use `md` (4-6px) for interactive elements to retain a structured, technical feel. Avoid pill shapes or massive rounding.
- Shadows: Avoid drop shadows for decoration. Use subtle elevations only for interactive states (e.g., hover).

## 5. Interaction & Motion Principles
- Motion must communicate state changes or reveal information sequentially; never use motion solely for decoration.
- Prefer CSS transitions (150ms-300ms) for micro-interactions (hover, focus, active).
- Scroll-based reveals should use smooth translation on the Y-axis + opacity fade. Avoid overshoot, bounce, or scale.
- **Accessibility Mandate**: Respect `prefers-reduced-motion`. All parallax, shimmers, and complex reveals must gracefully degrade to static visible states if reduced motion is enabled.

## 6. Architecture Component Rules
- 21st.dev components may be referenced structurally but MUST be overridden with Lexis AI typography, colors, and timing. 
- Do not blindly install external component libraries. Prefer internal CSS, `IntersectionObserver`, and React ref manipulations for performance.
