# Design Guidelines: AI Chat Application with Analytics

## Design Approach
**Utility-Focused Design System Approach** - Following Material Design principles for this productivity-focused AI chat application. The interface prioritizes efficiency, clarity, and data visualization over visual flourishes.

## Core Design Elements

### Color Palette
**Dark Mode Primary:**
- Background: 220 13% 9% (rich dark slate)
- Surface: 220 13% 11% (elevated surfaces)
- Primary: 217 91% 60% (vibrant blue for AI responses)
- Secondary: 262 83% 58% (purple for user messages)
- Accent: 142 69% 58% (green for analytics indicators)
- Text Primary: 210 40% 98%
- Text Secondary: 215 20% 65%

**Light Mode:**
- Background: 0 0% 100%
- Surface: 210 40% 98%
- Primary: 217 91% 60%
- Secondary: 262 83% 58%
- Accent: 142 69% 58%

### Typography
- **Primary Font:** Inter (clean, readable for chat)
- **Monospace:** JetBrains Mono (for code blocks in responses)
- **Headers:** 24px/32px semibold
- **Body:** 16px/24px regular
- **Small:** 14px/20px regular

### Layout System
**Spacing Units:** Consistent use of Tailwind units 2, 4, 6, and 8
- Component padding: p-4, p-6
- Section margins: m-4, m-8
- Element gaps: gap-4, gap-6

### Component Library

#### Main Layout
- **Split Layout:** 70% chat interface, 30% analytics sidebar
- **Chat Container:** Full height with message list and input area
- **Analytics Panel:** Fixed sidebar with collapsible sections

#### Chat Components
- **Message Bubbles:** 
  - User messages: Right-aligned, secondary color background
  - AI responses: Left-aligned, primary color background
  - Rounded corners (rounded-2xl), generous padding (p-4)
- **Input Area:** Fixed bottom, elevated surface with subtle shadow
- **Typing Indicators:** Animated dots for AI processing

#### Analytics Components
- **Metrics Cards:** Clean cards showing conversation count, response time, user satisfaction
- **Charts:** Line charts for conversation trends, bar charts for topic distribution
- **Data Tables:** Sortable tables for detailed conversation logs

#### Navigation
- **Header Bar:** Minimal top bar with app title and settings toggle
- **Action Buttons:** Primary button for send, ghost buttons for secondary actions
- **Controls:** Clear history, export data, theme toggle

### Visual Hierarchy
- **Primary Focus:** Chat input and latest messages
- **Secondary:** Analytics metrics and visualizations  
- **Tertiary:** Historical data and settings

### Interactive States
- **Hover:** Subtle background lightening (5% opacity overlay)
- **Active:** Slight scale reduction (scale-95)
- **Focus:** Clear outline with primary color
- **Loading:** Skeleton states for AI responses

### Responsive Behavior
- **Desktop:** Full split layout
- **Tablet:** Collapsible analytics sidebar
- **Mobile:** Full-screen chat with analytics as modal overlay

## Key Design Principles
1. **Conversation Flow:** Smooth scrolling, clear message separation
2. **Data Clarity:** Analytics presented without overwhelming the chat experience
3. **Performance Feedback:** Clear indicators for AI processing and response states
4. **Accessibility:** High contrast ratios, keyboard navigation, screen reader support