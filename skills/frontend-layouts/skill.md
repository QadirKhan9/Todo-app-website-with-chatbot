---
name: frontend-layouts
description: Build responsive frontend pages, components, and layouts with modern styling techniques. Use for web app and landing page designs.
---

# Frontend Layouts & Components

## Instructions

1. **Page Layouts**
   - Full-width sections
   - Grid and flexbox for responsive layouts
   - Header, main, footer structure

2. **Components**
   - Buttons, cards, forms, modals
   - Reusable and modular components
   - Accessible and keyboard-navigable

3. **Styling**
   - CSS variables for colors and spacing
   - Modern typography (sans-serif, readable sizes)
   - Gradients, shadows, and hover effects

4. **Responsive Design**
   - Mobile-first approach
   - Use media queries for breakpoints
   - Test across devices

5. **Animations & Interactions**
   - Smooth hover/focus transitions
   - Fade-in, slide-in, or scale animations
   - Scroll-triggered animations

## Best Practices
- Keep components reusable and DRY
- Follow semantic HTML structure
- Use high-contrast colors for readability
- Optimize for performance (minimal CSS/JS)
- Ensure accessibility (ARIA labels, focus states)

## Example Structure
```html
<header class="site-header">
  <nav class="nav">
    <a href="#" class="logo">Logo</a>
    <ul class="nav-links">
      <li><a href="#">Home</a></li>
      <li><a href="#">About</a></li>
      <li><a href="#">Contact</a></li>
    </ul>
  </nav>
</header>

<main class="main-content">
  <section class="section hero">
    <h1 class="animate-fade-in">Welcome to Our Website</h1>
    <p class="animate-fade-in-delay">We build modern web experiences.</p>
    <button class="cta-button">Get Started</button>
  </section>

  <section class="section features">
    <div class="card animate-slide-in">
      <h3>Feature One</h3>
      <p>Description of feature.</p>
    </div>
    <div class="card animate-slide-in-delay">
      <h3>Feature Two</h3>
      <p>Description of feature.</p>
    </div>
  </section>
</main>

<footer class="site-footer">
  <p>&copy; 2026 My Company</p>
</footer>
