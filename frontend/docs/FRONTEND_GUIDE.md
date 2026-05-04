# Frontend Developer Guide

## Tech Stack
- **Framework**: React 18/19
- **Build Tool**: Vite
- **UI Components**: Ant Design (antd)
- **Styling**: Bootstrap 5 (standard classes) + Ant Design Themes
- **State Management**: React Hooks + Context API + Zustand (for some modules)
- **API Communication**: Custom `apiFetch` utility with JWT management

## Getting Started
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## Project Structure
- `src/components`: Reusable UI components.
  - `GenericCrudPage.jsx`: The heart of the dynamic UI.
- `src/pages`: Individual page components.
- `src/hooks`: Custom React hooks (e.g., `useCrudData`).
- `src/utils.js`: Centralized utility functions.
- `src/ProjectLayout.jsx`: Main wrapper for project-specific pages.

## Key Concepts

### Dynamic Rendering
ERPSeed uses metadata from the backend (`SysView`, `SysComponent`) to render UIs at runtime. The `ComponentRenderer` is responsible for transforming this metadata into React components.

### API Integration
Always use `apiFetch` from `@/utils.js` for API calls. It handles:
- Base URL injection
- Bearer token authentication
- Automatic 401 refresh token logic
- Standardized error notifications via Ant Design `message`.

### The Visual Builder
Located in `src/pages/VisualBuilder/`, it uses `@dnd-kit` for a drag-and-drop experience. It interacts with the `visual_builder_api` on the backend.

## Best Practices
1. **Reuse Components**: Use `GenericCrudPage` whenever possible for standard CRUD tasks.
2. **Standard Styling**: Prefer Ant Design components for complex UI elements and Bootstrap utilities for layout/spacing.
3. **Error Handling**: Wrap API calls in try/catch and use `message.error()` for user feedback.
4. **Translations**: Use the `i18n` setup for any hardcoded strings.

## Testing
- Unit tests: `npm test` (Vitest)
- E2E tests: `npx playwright test`
