# Design Guidelines

## Core Principles

**Simplicity Through Reduction**  
Remove everything that doesn't serve the core purpose. Start complex, then deliberately simplify.

**Immediate Feedback**  
Every interaction must respond within 100ms. Use loading states and animations to acknowledge user actions.

**Content First**  
The interface should recede when content is present and emerge when guidance is needed.

## Practical Guidelines

### Typography
- Use system fonts: `-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif`
- Establish clear hierarchy with consistent scale (1.25x ratio)
- Minimum 1.5x line height for body text
- Generous white space between sections

### Colors
- Limit to 3-4 colors maximum
- Use slightly desaturated colors for sophistication
- Primary action = brand color, errors = red, success = green
- Most UI should be neutral grays to let content shine

### Spacing
- Use consistent spacing scale: 4px, 8px, 12px, 16px, 24px, 32px, 40px
- Group related elements through proximity
- Generous padding in interactive elements (minimum 44x44px touch targets)

### Interactive Elements
- **Buttons**: Clear hover, active, disabled states with subtle shadows
- **Inputs**: Visible focus states with color + shadow, helpful placeholders
- **Feedback**: Loading spinners, success confirmations, clear error messages
- **Animations**: 150ms for quick actions, 250ms for transitions, 400ms for page changes

## CSS Variables Reference
```css
--primary: #4F46E5;       /* Primary actions */
--primary-hover: #4338CA;  /* Hover state */
--text-primary: #111827;   /* Main text */
--text-secondary: #6B7280; /* Secondary text */
--border: #E5E7EB;        /* Borders */
--error: #DC2626;         /* Error states */
```

## Quick Checklist
- [ ] Can users understand what to do without instructions?
- [ ] Does every interaction provide immediate visual feedback?
- [ ] Is text readable with good contrast and spacing?
- [ ] Are touch/click targets at least 44x44px?
- [ ] Do animations feel natural, not decorative?
- [ ] Does the design work on mobile devices?