import base64
text = '''---
name: AgroTech Vision
colors:
  primary: '#15803d'
  on-primary: '#ffffff'
  primary-container: '#dcfce7'
  on-primary-container: '#14532d'
  secondary: '#ea580c'
  on-secondary: '#ffffff'
  secondary-container: '#ffedd5'
  on-secondary-container: '#7c2d12'
  surface: '#fafaf9'
  on-surface: '#1c1917'
  background: '#ffffff'
  on-background: '#1c1917'
typography:
  display-lg:
    fontFamily: Space Grotesk
    fontSize: 56px
    fontWeight: '700'
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '600'
  body-base:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
---
## Brand & Style
The design system represents the convergence of traditional Indian agriculture and modern edge computing. We emphasize soft glassmorphism, clean typography, and spacious layouts to create a premium, high-tech aesthetic.

## Hover Effects
Use pronounced hover effects on all interactive elements. Buttons scale slightly and glow; cards lift with a deepened drop-shadow.'''
with open('b64.txt', 'w', encoding='utf-8') as f:
    f.write(base64.b64encode(text.encode('utf-8')).decode('utf-8'))
