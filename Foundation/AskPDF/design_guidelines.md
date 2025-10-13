# Design Guidelines: AskMyPDF Interface

## Design Approach

**Selected Approach:** Design System - Minimal Productivity Pattern
**References:** ChatGPT, Linear, Claude, Vercel AI Chat SDK
**Principles:** Clean minimalism, functional clarity, distraction-free interaction, responsive parameter controls

## Core Design Elements

### A. Color Palette

**Dark Mode (Primary):**
- Background Base: 222 47% 11% (deep charcoal)
- Surface Elevated: 222 47% 15% (chat containers, panels)
- Border Subtle: 217 33% 25%
- Text Primary: 210 40% 98%
- Text Secondary: 215 20% 65%
- Accent Primary: 217 91% 60% (blue for actions, active states)
- Accent Hover: 217 91% 55%
- User Message: 217 91% 60% (blue bubble)
- Assistant Message: 222 47% 18% (subtle gray bubble)
- Error State: 0 84% 60%

**Light Mode:**
- Background: 0 0% 100%
- Surface: 210 40% 98%
- Borders: 214 32% 91%
- Text Primary: 222 47% 11%
- Text Secondary: 215 16% 47%

### B. Typography

**Font Stack:** System fonts for performance
```
Primary: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
Monospace: "SF Mono", Monaco, "Cascadia Code", monospace (for code blocks)
```

**Scale:**
- Page Title: text-2xl font-semibold (24px)
- Section Headers: text-sm font-semibold uppercase tracking-wider
- Chat Messages: text-base (16px) leading-relaxed
- Parameters Labels: text-sm font-medium
- Helper Text: text-xs text-secondary

### C. Layout System

**Spacing Units:** Tailwind primitives of 2, 4, 6, 8, 12, 16
- Component padding: p-4 or p-6
- Section gaps: gap-4 or gap-6
- Message spacing: space-y-4

**Grid Structure:**
- Desktop: Two-column layout (70/30 split)
  - Main: Chat interface (flex-1)
  - Sidebar: Parameter controls (w-80)
- Mobile: Single column, collapsible controls

**Container:**
- Max width: max-w-7xl mx-auto
- Chat messages: max-w-3xl for optimal readability

### D. Component Library

**1. Chat Interface:**
- Full-height scrollable container with gradient fade at top
- Message bubbles: rounded-2xl with tail-less design
- User messages: Aligned right, blue background (217 91% 60%)
- Assistant messages: Aligned left, dark gray background (222 47% 18%)
- Timestamp: text-xs opacity-60 below each message
- Avatar icons: 8x8 rounded-full (user gradient, AI icon)

**2. Parameter Controls Panel:**
- Card container with border-l-2 accent
- Grouped sections with dividers
- Model selector: Full-width dropdown, custom styled
- Temperature slider: 
  - Range 0-2 with tick marks at 0, 0.5, 1, 1.5, 2
  - Live value display above thumb
  - Gradient track from cool (blue) to warm (orange)
- Top K input: Number input with stepper controls
- Max tokens: Slider with dynamic label
- Each control includes help text explaining impact

**3. Input Area:**
- Fixed bottom position with backdrop blur
- Textarea with auto-expand (max 5 lines)
- Send button: Accent color, icon (arrow-up), rounded-full
- Character counter when approaching limits
- "Thinking..." indicator with animated dots

**4. Navigation & Actions:**
- Top bar: Minimal with logo, model indicator badge, clear chat button
- Clear chat: Outlined button with trash icon, confirmation modal
- Export chat: Secondary action, download icon

**5. Empty State:**
- Centered content with OpenAI logo (placeholder)
- Suggested prompts as clickable cards (4-6 examples)
- Cards: hover lift effect, cursor-pointer

**6. Loading & Error States:**
- Streaming response: Typewriter effect with blinking cursor
- Loading: Pulsing skeleton for message bubble
- Error: Red border on input, inline error message with retry button

### E. Interactions & Micro-animations

**Minimal Animation Budget:**
- Message appearance: Fade up (200ms ease-out)
- Parameter changes: Smooth value transitions (150ms)
- Button hovers: Scale 1.02, slight shadow increase
- Slider thumb: Scale on drag
- NO background animations, NO complex scroll effects

**Focus States:**
- 2px blue ring with offset for keyboard navigation
- Visible throughout entire interface

## Layout Specifications

**Desktop View (≥1024px):**
```
┌─────────────────────────────────────┬──────────────┐
│ Header (Model, Actions)             │              │
├─────────────────────────────────────┤  Parameters  │
│                                     │   Sidebar    │
│   Chat Messages Area                │   (sticky)   │
│   (scrollable, max-w-3xl centered)  │              │
│                                     │              │
├─────────────────────────────────────┤              │
│ Input Area (fixed bottom)           │              │
└─────────────────────────────────────┴──────────────┘
```

**Mobile View (<1024px):**
- Parameters: Collapsible drawer from bottom (sheet component)
- Toggle button in header to show/hide controls
- Chat takes full width
- Input area remains fixed at bottom

## Accessibility

- All controls keyboard navigable
- ARIA labels on all interactive elements
- Color contrast ratio ≥4.5:1 for all text
- Focus indicators never hidden
- Screen reader announcements for new messages
- Reduced motion support: Disable all animations when preferred

## Key Differentiators

- **Split-screen productivity layout** - Chat + controls visible simultaneously
- **Real-time parameter feedback** - Visual indicators show how settings affect output
- **Code-friendly** - Monospace font support, syntax highlighting for code blocks (use highlight.js)
- **Conversation context** - Message count and token usage visible
- **Professional restraint** - No playful illustrations, no distracting animations, pure focus on utility