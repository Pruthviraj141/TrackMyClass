# UI/UX Audit

This document profiles the visual workflow in the `frontend` directory using React/Vite/Tailwind structure.

## Routes & Screens

### Public Workflows
1. **Landing** (`/`): Basic marketing layout outlining value props. Needs heavier polish.
2. **Registration** (`/register`):
   - **Good**: Handles graceful degradation into native WebRTC `<video>` calls natively prioritizing the environment (Rear) camera. Handles success alerts nicely.
   - **Weak**: Uses aggressive blocking loading overlays. Errors return unstyled strings. Mobile users might be confused if the camera flips weirdly.
3. **Institution Portal** (`/institution`): Small input code module.

### Admin Workflows
1. **Login** (`/login`): Standard username/password module. No remember-me logic.
2. **Dashboard** (`/admin/dashboard`): 
   - Statistical tracking grid.
   - Missing empty-states for 0 students/classes.
3. **Live Monitor** (`/admin/monitor`):
   - **Good**: Connects perfectly rendering bounding-boxes over `canvas` overlaid on `<video>`.
   - **Weak**: No socket logic. Just aggressive `setInterval` sending Base64 polling. This creates massive lag jumps depending on network stability rather than smooth degradation.
4. **Students Directory** (`/admin/students`): Basic list-rendering CRUD component. Missing complex paginations for > 100 students.

## Accessibility Issues
- Many inputs lack correct WAI-ARIA labels.
- Error validation lacks high contrast coloring in some sub-components.
- Heavy processing (like `POST /register`) locks UI thread slightly leading to unresponsiveness.
