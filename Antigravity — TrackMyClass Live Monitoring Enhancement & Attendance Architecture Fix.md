# TRACKMYCLASS — STUDENT EXPERIENCE MASTER UI REFINEMENT
# MOBILE-FIRST / IOS-INSPIRED / ALL STUDENT ROUTES

The current Student UI still does NOT feel like a polished mobile application.

Do a complete refinement of ALL Student-facing routes as ONE coherent product.

IMPORTANT:
Do not redesign the backend.
Do not invent data.
Do not install unnecessary packages.
Do not create separate visual systems for different pages.

The goal is:

REAL DATA
+
CORRECT LAYOUT
+
PREMIUM IOS-INSPIRED UI
+
MOBILE-FIRST
+
RESPONSIVE DESKTOP
+
LIGHT/DARK MODE

==================================================
1. FIX THE FUNDAMENTAL MOBILE LAYOUT
==================================================

The application must use the FULL actual mobile viewport.

For:
320px
375px
390px
430px

the Student application must:

- fill the viewport
- use consistent 16–20px horizontal padding
- have correctly centered content
- have no narrow desktop-like column
- have no giant unused side space
- have no horizontal scrolling
- have no clipped content
- have no bottom-navigation overlap

Do NOT make the entire page artificially narrow.

Each major section should use the available width correctly.

==================================================
2. HERO ATTENDANCE CARD — CRITICAL
==================================================

The current Attendance ring is incorrectly positioned toward the left with excessive empty space on the right.

FIX THIS.

The attendance visualization must be genuinely CENTERED inside its card.

Desired hierarchy:

           Overall Attendance

               100%
             [ RING ]

           6 / 6 classes

     Present   Absent   Late

The ring and percentage must sit visually in the center of the hero card.

Do NOT leave the ring anchored to the left unless the approved reference explicitly requires a two-column layout.

The percentage must be the visual focus.

The ring must visually represent the REAL attendance percentage.

If attendance = 75%, the ring must represent approximately 75%.
If attendance = 100%, the ring is complete.

Do not hardcode values.

The ring should feel premium:
- smooth stroke
- restrained gradient/brand treatment
- balanced size
- perfect circular geometry
- strong central typography
- subtle animation only when appropriate
- excellent spacing

Do not make the ring oversized.

Do not make it tiny.

==================================================
3. STUDENT HOME
==================================================

Refine the Student Home into this hierarchy:

Header
→ Greeting
→ Overall Attendance
→ Next Class
→ Today's Classes
→ Attendance by Subject
→ Bottom Navigation

Hero:

Overall Attendance
percentage
Present
Absent
Late
Total Classes

Next Class:

ONLY show a real upcoming class from the API.

If none exists:

“No upcoming classes”

Do NOT fabricate:
subject
teacher
room
time
countdown

Today's Classes:

ONLY real classes belonging to the authenticated student.

Attendance by Subject:

ONLY real subjects returned by backend data.

Each subject should clearly show:

Subject
Attendance %
Attended / Total

Never show a subject that does not exist in the database.

==================================================
4. STUDENT ATTENDANCE
==================================================

Refine the Attendance page using the same design language.

The hero percentage/ring must be centered.

Keep:

Day
Month
Overall

only if these modes are actually supported.

Calendar:

- generated from real dates
- real attendance markers
- selected date
- current date
- previous/next month
- no fake colored dates

Selected day:

show real subject/session/status/time where available.

No record ≠ Absent.

No session ≠ Absent.

Never fabricate calendar states.

==================================================
5. STUDENT CLASSES
==================================================

Make Classes feel like a premium mobile schedule application.

Show REAL enrolled classes only.

Suggested hierarchy:

Today's Classes
Upcoming
All Classes

Each class:

Subject
Time
Room if available
Teacher if available
Section if available
Status if real

If a field does not exist in backend data:

DO NOT INVENT IT.

Use a clean empty state when the student has no classes.

Make cards easy to scan with one hand.

==================================================
6. STUDENT PROFILE
==================================================

Make Profile feel premium and personal.

Show only real student information.

Possible:

Profile
Name
Email
Roll Number
Class / Section
Institution

Then:

Attendance Summary
Face Recognition Status
Preferences
Security
Logout

Do not expose:

face embeddings
biometric vectors
model information
internal IDs

Use the existing backend data.

If a field does not exist:

hide it rather than inventing it.

==================================================
7. FACE REGISTRATION
==================================================

Use the approved Face Registration design language.

It must feel like the SAME application.

Mobile-first:

Introduction
→ Camera
→ Position
→ Capture
→ Review
→ Processing
→ Success

Camera must be real.

Use real camera lifecycle.

Camera must stop when leaving the route.

Do not fake face detection or success.

Keep biometric implementation details hidden from the student.

==================================================
8. STUDENT LOGIN
==================================================

Student Login must look like the same premium application.

Institution context should already be established by the institution-first flow.

Do NOT unnecessarily ask the student for institution code again if institution context already exists.

Use the existing authentication API.

No fake fields.

No fake states.

==================================================
9. STUDENT REGISTRATION
==================================================

Registration should be:

Institution context
→ Account details
→ Personal details
→ Face registration
→ Review
→ Complete

Use only backend-supported fields.

Do not ask for institution information twice.

Do not invent registration steps unsupported by the backend.

==================================================
10. REAL DATA — ABSOLUTE RULE
==================================================

THIS IS NON-NEGOTIABLE.

ALL STUDENT ROUTES MUST USE REAL DATABASE/API DATA.

Never use:

- dummy
- mock
- demo
- sample
- faker
- random
- hardcoded
- placeholder
- screenshot values
- fake fallback values

Search the Student production code for these patterns and remove fake production data.

If data does not exist:

show an honest empty/unavailable state.

REAL DATA OR HONEST EMPTY/ERROR STATE.

No third option.

==================================================
11. DATA CONSISTENCY
==================================================

The same data must remain consistent across:

Student Home
Student Attendance
Student Classes
Student Profile
Face Registration status
Teacher Attendance
Teacher-created attendance
Reports

Subject-specific attendance must remain separate.

For the same:

student
+
subject
+
session/date range

the result must match everywhere.

Do not patch one page with a special calculation.

Fix the underlying API/service/repository if needed.

==================================================
12. IOS-INSPIRED DESIGN SYSTEM
==================================================

Make the Student experience feel like a premium iOS-inspired application.

Use:

- generous whitespace
- soft surfaces
- subtle borders
- restrained shadows
- 12–20px rounded corners
- polished segmented controls
- tactile buttons
- clean list rows
- strong hierarchy
- subtle transitions
- no excessive glassmorphism

DO NOT make every element a card.

Use hierarchy and composition.

==================================================
13. TYPOGRAPHY
==================================================

Use:

-apple-system,
BlinkMacSystemFont,
"SF Pro Display",
"SF Pro Text",
"Segoe UI",
Roboto,
Helvetica,
Arial,
sans-serif

Do NOT bundle proprietary Apple fonts.

Use:

400
500
600
700

Use 700 sparingly.

Use tabular numerals for attendance statistics.

==================================================
14. COLOR SYSTEM
==================================================

Primary:

Indigo / Blue-Violet

Success:

restrained Green

Warning:

restrained Amber

Danger:

restrained Red

Info:

restrained Blue

Light:

soft off-white background
white surfaces
deep charcoal text
cool gray secondary text

Dark:

deep charcoal background
elevated dark surfaces
soft white text
subtle borders

No neon.
No cyberpunk.
No excessive purple.
No random colors.

==================================================
15. LIGHT + DARK MODE
==================================================

Both modes must actually work across EVERY Student route.

Do not simply invert colors.

Verify:

Home
Attendance
Classes
Profile
Face Registration
Login
Registration

Theme switching must persist.

==================================================
16. NAVIGATION
==================================================

Student bottom navigation:

Home
Attendance
Classes
Profile

Active destination must be visually obvious.

Navigation should be fixed correctly to the mobile viewport.

Respect safe-area spacing.

Do not let content disappear behind the navigation.

==================================================
17. MICRO-INTERACTIONS
==================================================

Use subtle motion for:

- navigation
- subject selection
- calendar selection
- cards
- theme switching
- loading
- success/error states

Do not over-animate.

Respect prefers-reduced-motion.

==================================================
18. LOADING
==================================================

Never show fake data while loading.

Use:

- skeleton text
- skeleton metrics
- skeleton cards
- skeleton lists

Do not show previous unrelated values as current data.

==================================================
19. ERROR
==================================================

When API fails:

show a clear human-readable error.

Example:

“Unable to load your attendance.”

“Try again”

Do not replace failed data with fake numbers.

==================================================
20. EMPTY STATES
==================================================

Each route needs a proper empty state.

Examples:

No classes
No upcoming classes
No attendance records
No subjects
No profile information available

Empty means EMPTY.

Do not manufacture data.

==================================================
21. RESPONSIVE DESIGN
==================================================

Primary:

320px
375px
390px
430px

Also:

768px
1024px
1280px
1440px

Mobile must be intentionally designed.

Desktop should adapt naturally.

Do not make desktop simply a stretched mobile layout.

==================================================
22. DESKTOP STUDENT EXPERIENCE
==================================================

Desktop should remain simple.

Use a constrained content area.

Do not turn Student Home into an enterprise dashboard.

Students need personal information, not institution-wide analytics.

At larger sizes, use more breathing room and balanced composition.

==================================================
23. ACCESSIBILITY
==================================================

Use:

semantic HTML
keyboard navigation
visible focus
44px+ touch targets where practical
accessible labels
screen-reader-friendly status
non-color-only state indicators

Calendar buttons must be accessible.

==================================================
24. PERFORMANCE
==================================================

Do not add unnecessary dependencies.

Reuse:

existing icon library
existing date utilities
existing API client
existing theme system
existing components

Avoid:

duplicate requests
request loops
excessive renders
unnecessary polling
large assets
unnecessary animations

==================================================
25. FINAL VISUAL CORRECTION
==================================================

Pay special attention to the current problems visible in the Student Home screenshot:

- attendance ring is NOT centered
- hero card has too much empty right-side space
- page feels too narrow
- typography hierarchy is weak
- subject/class content feels visually incomplete
- mobile composition feels like a desktop page inside a phone
- bottom navigation needs proper full-width mobile treatment

Fix these issues across ALL Student screens, not just Home.

==================================================
26. REAL BROWSER QA
==================================================

Run the actual application.

Verify:

Student Login
→ Student Home
→ Attendance
→ Classes
→ Profile
→ Face Registration

Test:

real data
subject switching
attendance values
class information
theme switching
navigation
loading
errors
empty states

Check:

320
375
390
430

and desktop:

1024
1440

==================================================
27. DATA AUDIT
==================================================

Search production Student UI code for:

mock
dummy
demo
sample
faker
random
placeholder
fallback
hardcoded
87.4
92
100
+2.1

Inspect every occurrence.

Keep legitimate test fixtures.

Remove fake data from production paths.

==================================================
28. FINAL QUALITY BAR

Do not aim for:

“Looks better.”

Aim for:

REAL DATA
+
CORRECT CALCULATIONS
+
CENTERED COMPOSITION
+
PREMIUM TYPOGRAPHY
+
MOBILE-FIRST UX
+
RESPONSIVE DESKTOP
+
LIGHT/DARK
+
ACCESSIBILITY
+
FAST INTERACTION

The Student section must feel like ONE carefully designed product.

A recruiter opening the app should immediately see:

a polished mobile application

not:

a desktop website squeezed into a phone.

FINAL RULE:

The visual reference controls the DESIGN.

The database/API controls the DATA.

The backend controls AUTHORIZATION.

Never sacrifice correctness for visual completeness.

Make the Student experience feel genuinely premium, centered, spacious, and iOS-inspired — while keeping the implementation simple and using only the dependencies already required by the application.