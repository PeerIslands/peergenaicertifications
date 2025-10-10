# PDF Chat Application - Design Guidelines

## Design Approach: Hybrid Design System
**Primary Reference:** ChatGPT/Claude for AI chat patterns + Linear for modern productivity aesthetics + Notion for document handling
**Rationale:** Utility-focused productivity tool requiring proven chat patterns with clean, professional design

## Core Design Elements

### A. Color Palette

**Dark Mode (Primary):**
- Background Primary: 222 15% 8% (deep charcoal)
- Background Secondary: 222 15% 12% (elevated surfaces, chat bubbles)
- Background Tertiary: 222 15% 16% (hover states, input fields)
- Text Primary: 210 20% 98% (high contrast white)
- Text Secondary: 215 15% 70% (subdued text, timestamps)
- Text Muted: 215 10% 50% (placeholders, disabled)
- Accent Primary: 217 91% 60% (vibrant blue for CTAs, user messages)
- Accent Hover: 217 91% 55%
- Success: 142 76% 45% (upload success, confirmations)
- Border: 215 15% 25% (dividers, input borders)

**Light Mode:**
- Background Primary: 0 0% 100%
- Background Secondary: 210 20% 98%
- Background Tertiary: 210 17% 95%
- Text Primary: 222 47% 11%
- Text Secondary: 215 16% 47%
- Accent Primary: 217 91% 50%

### B. Typography
- **Primary Font:** Inter (Google Fonts) - clean, highly legible for chat
- **Code/Monospace:** JetBrains Mono (for code snippets in responses)
- **Headings:** font-semibold to font-bold
- **Body Text:** font-normal, 15px (text-[15px]) for optimal chat readability
- **Small Text:** text-sm for timestamps, metadata
- **Message Text:** text-base leading-relaxed for comfortable reading

### C. Layout System
**Spacing Primitives:** Tailwind units of 2, 3, 4, 6, 8, 12
- Chat message padding: p-4
- Section spacing: space-y-4 to space-y-6
- Container padding: px-6 py-4
- Icon spacing: gap-3
- Consistent vertical rhythm: mb-6 for major sections

**Layout Structure:**
- Two-column split: Sidebar (320px, lg:w-80) + Main chat area (flex-1)
- Mobile: Stack sidebar above or as drawer overlay
- Max content width: Full width for chat, max-w-4xl for settings/docs

### D. Component Library

**Chat Interface:**
- **Message Bubbles:** 
  - User messages: Accent blue background, white text, rounded-2xl, ml-auto max-w-[80%]
  - AI responses: Secondary background, primary text, rounded-2xl, mr-auto max-w-[80%]
  - System messages: Border-l-4 border-accent, subtle background, italic text
- **Input Area:** 
  - Fixed bottom position with backdrop-blur-md
  - Multi-line textarea with auto-expand (max 5 lines)
  - Send button: Accent primary with icon
  - PDF upload button: Subtle secondary with paperclip icon

**PDF Upload Zone:**
- Drag-and-drop area with dashed border (border-dashed border-2)
- Animated border on drag-over (border-accent)
- File preview cards: Thumbnail + filename + size + remove button
- Upload progress bar: Linear gradient accent colors

**Sidebar Navigation:**
- Conversation history list with timestamps
- Active conversation: Accent background with higher opacity
- Search/filter input at top
- New chat button: Prominent accent CTA
- PDF library section: Collapsible list of uploaded documents

**Status Indicators:**
- Typing indicator: Three bouncing dots (animate-pulse)
- Processing PDF: Spinner with percentage text
- Success/Error toasts: Top-right corner, auto-dismiss
- Online status: Small green dot for active connection

**Message Components:**
- Markdown rendering support (bold, italic, lists, code blocks)
- Code blocks: Dark theme with syntax highlighting
- Copy button on hover for code/text blocks
- Timestamp: text-xs text-muted, right-aligned below message
- Avatar circles: 32px for user, 36px for AI (with gradient or icon)

### E. Interactions & Animations

**Minimal, Purposeful Animations:**
- Message send: Slide-in from right (user) or left (AI) with fade
- Typing indicator: Subtle pulse on dots
- Button interactions: scale-[0.98] on active
- Hover states: Slight background brightness increase
- PDF upload: Smooth height expansion for preview cards
- Scroll behavior: Smooth auto-scroll to latest message

**Interaction Patterns:**
- Enter to send message, Shift+Enter for new line
- Drag-and-drop PDF upload with visual feedback
- Click message to view source PDF section (if applicable)
- Hover message for actions menu (copy, delete, regenerate)
- Keyboard shortcuts indicator (Cmd/Ctrl+K for search)

## Key Design Principles

1. **Conversation-First:** Chat area is the hero - minimal distractions, maximum reading comfort
2. **Contextual Clarity:** Always show which PDF context is being used for responses
3. **Progressive Disclosure:** Hide advanced features in menus, show essentials upfront
4. **Responsive Typography:** Scale text sizes appropriately for mobile (14px base on small screens)
5. **Instant Feedback:** Every action has immediate visual confirmation
6. **Document Traceability:** Link AI responses to specific PDF sections when possible

## Accessibility
- High contrast text ratios (WCAG AAA where possible)
- Focus indicators on all interactive elements (ring-2 ring-accent)
- Screen reader labels for icon-only buttons
- Keyboard navigation for entire chat flow
- Dark mode maintained across all components including inputs

## Images
No hero images required. This is a utility application focused on functionality. Use:
- SVG icons from Heroicons (outline style for secondary actions, solid for primary)
- PDF thumbnail previews (generated on upload)
- User/AI avatars: Simple colored circles with initials or icon
- Empty state illustration: Simple SVG for "No conversations yet"