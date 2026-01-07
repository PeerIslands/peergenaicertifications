# RAG Application Design Guidelines

## Design Approach
**System Selected:** Material Design (data-dense technical application)
**Rationale:** This utility-focused application requires clear information hierarchy, robust component patterns for data visualization, and intuitive interaction models for file upload and chat interfaces.

## Typography System
- **Primary Font:** Inter or Roboto via Google Fonts CDN
- **Display/Headers:** Font weight 600-700, sizes: text-3xl (section headers), text-2xl (subsection headers)
- **Body Text:** Font weight 400, text-base for general content, text-sm for secondary information
- **Code/Technical:** JetBrains Mono (monospace) for chunk previews, file names, and technical details
- **Chat Messages:** text-base for user queries, slightly larger text-lg for AI responses

## Layout & Spacing System
**Spacing Units:** Tailwind units of 2, 4, 6, 8, and 12 (e.g., p-4, m-8, gap-6)
- Container: max-w-7xl with px-6 on mobile, px-8 on desktop
- Section padding: py-8 on mobile, py-12 on desktop
- Card padding: p-6 for major cards, p-4 for nested components
- Grid gaps: gap-6 for major layouts, gap-4 for compact lists

## Application Structure

### Header/Navigation (Fixed Top)
- Height: h-16
- Logo/title on left, settings/help icons on right
- Minimal, non-distracting presence
- Shadow or subtle border for depth separation

### Main Content Area (Two-Tab Interface)

**Tab 1: Upload & Processing Dashboard**
- Split layout: 40% left (upload zone), 60% right (visualization)
- Upload zone: Large drag-and-drop area with dashed border, centered icon and text
- File preview card below upload (after upload): Shows PDF name, page count, file size
- Processing visualization: Vertical timeline/stepper showing three stages:
  1. **Chunking Stage:** Progress bar, chunk count, preview of 2-3 sample chunks in cards
  2. **Vectorization Stage:** Progress indicator, embedding dimension count, vector count
  3. **Database Storage:** Completion status, total vectors stored, storage confirmation

**Tab 2: Chat Interface**
- Three-column layout on desktop (20%-50%-30%), single column on mobile
- Left sidebar (collapsible on mobile): Document metadata, chunk settings, uploaded files list
- Center: Chat conversation area with message bubbles (user right-aligned, AI left-aligned)
- Right sidebar: "Retrieved Context" panel showing relevant chunks used for answers with similarity scores

## Component Library

### Cards
- Elevated cards with subtle shadow
- Rounded corners (rounded-lg)
- White/neutral background
- Padding: p-6 for major cards, p-4 for list items

### Upload Zone
- Large rectangular area (min-h-64)
- Dashed border (border-2 border-dashed)
- Centered upload icon (from Heroicons: ArrowUpTray, size: w-12 h-12)
- Supporting text below icon explaining drag-drop or click to browse

### Processing Visualization
- Stepper/Timeline component with three nodes connected by lines
- Each stage shows: Icon + Label + Status + Details card
- Active stage highlighted, completed stages with checkmark icon
- Progress bars for active stages
- Expandable detail cards showing sample data (chunks, vectors)

### Chat Components
- Message bubbles: rounded-2xl, max-w-3xl for readability
- User messages: Compact, right-aligned
- AI responses: More spacious, left-aligned with avatar icon
- Input area: Fixed bottom, elevated card with textarea and send button (Heroicons: PaperAirplane)

### Context Display Cards
- Compact cards in right sidebar
- Each shows: Chunk text (truncated), similarity score badge, expand/collapse toggle
- Stacked vertically with gap-3
- Highlighted when referenced in AI response

### Data Visualization
- Progress bars: h-2 height, rounded-full, animated fill
- Badges: For counts, scores, statuses (pill-shaped, text-xs)
- Icons: Heroicons library throughout (Document for PDFs, Cube for vectors, Database for storage)

### Buttons
- Primary action (Upload, Send): Solid fill, px-6 py-3, rounded-lg
- Secondary actions (Clear, Reset): Outline style, same padding
- Icon buttons (Settings, Help): p-2, rounded-full

## Interaction Patterns
- Tab switching: Smooth transition, maintain state
- File upload: Immediate visual feedback, progress indication
- Processing stages: Auto-advance with animation between stages
- Chat: Streaming response with typing indicator
- Context highlighting: Click chunk in sidebar to highlight in chat response

## Responsive Behavior
- Desktop (lg+): Three-column chat, side-by-side upload/visualization
- Tablet (md): Two-column chat (hide left sidebar to drawer), stacked upload/visualization
- Mobile: Single column throughout, collapsible sidebars, full-width components

## Accessibility
- ARIA labels for all interactive elements
- Keyboard navigation for tabs, chat input, file upload
- Focus indicators on all interactive elements
- High contrast text (WCAG AA minimum)
- Screen reader announcements for processing stage changes

## Images
No hero images needed for this application-focused interface. Use icons exclusively from Heroicons library for all visual indicators.