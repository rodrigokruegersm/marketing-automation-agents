# Adlytics Brand Guidelines

## Brand Identity

**Tagline:** Intelligence for Scale

**Brand Voice:** Professional, Data-driven, Trustworthy, Modern

---

## Color Palette - Clean Minimal

### Primary Colors
| Color | Hex | Usage |
|-------|-----|-------|
| **Deep Navy** | `#0A1628` | Primary background, headers |
| **Ocean Blue** | `#0066FF` | Primary action, links, accent |
| **Electric Blue** | `#3B82F6` | Secondary accent, hover states |

### Secondary Colors
| Color | Hex | Usage |
|-------|-----|-------|
| **Pure White** | `#FFFFFF` | Cards, text on dark |
| **Light Gray** | `#F8FAFC` | Secondary background |
| **Slate** | `#64748B` | Secondary text, borders |
| **Cool Gray** | `#E2E8F0` | Dividers, subtle borders |

### Semantic Colors
| Color | Hex | Usage |
|-------|-----|-------|
| **Success** | `#10B981` | Positive metrics, growth |
| **Warning** | `#F59E0B` | Alerts, attention needed |
| **Error** | `#EF4444` | Critical, losses, errors |
| **Info** | `#06B6D4` | Information, tips |

---

## Typography

### Primary Font
**Inter** - Clean, modern, highly readable
- Headers: Inter Bold (700)
- Body: Inter Regular (400)
- Labels: Inter Medium (500)

### Font Sizes
| Element | Size | Weight |
|---------|------|--------|
| H1 | 32px | Bold |
| H2 | 24px | Semibold |
| H3 | 18px | Semibold |
| Body | 14px | Regular |
| Small | 12px | Regular |
| Caption | 11px | Medium |

---

## Logo Concept

### Symbol
- Stylized "A" with integrated analytics chart
- Represents growth and data intelligence
- Clean geometric lines

### Wordmark
- "Adlytics" in Inter Bold
- "Ad" in Ocean Blue (#0066FF)
- "lytics" in Deep Navy (#0A1628)

### Logo Variations
1. Full logo (symbol + wordmark)
2. Symbol only (for favicons, app icons)
3. Wordmark only (for horizontal spaces)

---

## UI Components

### Cards
```css
background: #FFFFFF;
border: 1px solid #E2E8F0;
border-radius: 12px;
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
```

### Buttons - Primary
```css
background: #0066FF;
color: #FFFFFF;
border-radius: 8px;
font-weight: 600;
```

### Buttons - Secondary
```css
background: transparent;
border: 1px solid #E2E8F0;
color: #64748B;
border-radius: 8px;
```

### Metrics Cards
```css
background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
border: 1px solid #E2E8F0;
border-radius: 12px;
```

---

## Spacing System

| Token | Size |
|-------|------|
| xs | 4px |
| sm | 8px |
| md | 16px |
| lg | 24px |
| xl | 32px |
| 2xl | 48px |

---

## Border Radius

| Element | Radius |
|---------|--------|
| Buttons | 8px |
| Cards | 12px |
| Inputs | 8px |
| Badges | 6px |
| Full round | 9999px |

---

## Shadows

### Subtle
```css
box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
```

### Medium
```css
box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
```

### Large
```css
box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
```

---

## Application

### Dashboard Theme
- Light mode primary (Clean Minimal)
- Dark mode secondary (for night users)
- High contrast data visualizations
- Clear visual hierarchy

### Charts & Graphs
- Primary line/bar: Ocean Blue (#0066FF)
- Secondary: Electric Blue (#3B82F6)
- Positive: Success Green (#10B981)
- Negative: Error Red (#EF4444)
- Neutral: Slate (#64748B)
