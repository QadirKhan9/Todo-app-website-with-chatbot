# Dark Mode Feature

This project includes a complete dark mode implementation with:

- Theme context for managing light/dark/system themes
- CSS variables for consistent theming
- Theme toggle button component
- Local storage persistence
- System preference detection
- Smooth transitions
- Next.js App Router compatibility

## Key Files

- `src/context/ThemeContext.tsx` - Theme provider and context
- `src/components/ThemeToggle.tsx` - Toggle button component
- `src/hooks/useSystemTheme.ts` - System theme detection hook
- `src/components/ThemedCard.tsx` - Example themed component
- `src/components/ThemeSelector.tsx` - Theme selection dropdown
- Updated `src/app/layout.tsx` - Wraps app with ThemeProvider
- Updated `src/app/globals.css` - Theme CSS variables and transitions

## Usage

Import and use the ThemeToggle component anywhere in your app:

```jsx
import ThemeToggle from '@/components/ThemeToggle';

function Header() {
  return (
    <header>
      <h1>My App</h1>
      <ThemeToggle />
    </header>
  );
}
```

Access theme information in any component:

```jsx
import { useTheme } from '@/context/ThemeContext';

function MyComponent() {
  const { theme, setTheme } = useTheme();
  
  return <div>Current theme: {theme}</div>;
}
```