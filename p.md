# TRACKMYCLASS — STUDENT ATTENDANCE SCREEN

# PREMIUM iOS-INSPIRED IMPLEMENTATION

Implement the **Student Attendance** screen using the attached approved reference image.

The attached image is the **VISUAL SOURCE OF TRUTH**.

Do NOT redesign the screen.
Do NOT replace it with the existing generic calendar layout.
Do NOT invent different cards, colors, spacing, navigation, or typography.

The goal is to transform the current Student Attendance page into a polished, premium, mobile-first experience inspired by high-quality iOS product design while remaining a web application.

---

# 1. PRODUCT GOAL

The screen should answer immediately:

* What is my attendance?
* What happened today?
* Which subject am I viewing?
* What happened on a selected date?
* Is my attendance improving?

The page must prioritize:

OVERALL ATTENDANCE
→ SUBJECT CONTEXT
→ CALENDAR
→ SELECTED DAY
→ ATTENDANCE DETAILS

The experience should feel calm, fast, personal, and premium.

---

# 2. IMPORTANT — REAL DATA ONLY

The approved image contains visual/example data.

DO NOT hardcode those values into production.

Do NOT use:

* fake percentages
* fake attendance counts
* fake subjects
* fake dates
* fake teachers
* placeholder activity
* generated trend values

Every number displayed must come from the authenticated student's real attendance data.

If data is unavailable:

show a truthful empty state.

Never replace missing data with fake numbers.

---

# 3. ATTENDANCE CALCULATION CORRECTNESS

Trace:

Student Attendance UI
→ API
→ service
→ repository
→ database
→ calculation
→ frontend

The displayed values must be mathematically correct.

Attendance should be scoped by:

Institution
+
Student
+
Subject
+
Class/Section
+
Session/date range

where applicable.

Do NOT calculate the overall attendance by blindly averaging rounded subject percentages.

Use the project's documented attendance rules.

Verify:

Present
Absent
Late
Not Marked

semantics before calculating.

---

# 4. SUBJECT SELECTOR / CONTEXT

The approved reference includes a subject context card.

Implement that visual treatment.

Example:

Data Structures
CS-B · Professor

These are visual examples only.

Use REAL subject/class data.

Selecting a subject must update:

* attendance percentage
* present/absent/late counts
* calendar indicators
* selected-day details
* trend/summary where applicable

No stale subject data may remain visible after switching.

---

# 5. TOP HEADER

Match the approved reference closely.

Use:

Back/navigation
Attendance
Calendar/action icon where shown

Keep the header compact.

Do not add unnecessary controls.

---

# 6. DAY / MONTH / OVERALL CONTROL

Implement the approved segmented control:

Day
Month
Overall

The control should feel like a premium iOS segmented control.

Use:

* smooth selection transition
* clear selected state
* accessible contrast
* comfortable touch target

Each mode must actually work.

Do NOT build a visual-only segmented control.

If a mode is not currently supported by the backend/product:

do not fake its information.

Either implement the real behavior or document the limitation.

---

# 7. ATTENDANCE HERO CARD

Implement the approved hero card.

The dominant metric is:

Overall Attendance

with the actual calculated percentage.

Use the approved circular/arc treatment.

Do not create a fake percentage.

The ring must visually correspond to the actual value.

For example:

If attendance = 78%

the progress visualization should represent approximately 78%.

Do not display misleading visual proportions.

---

# 8. SUMMARY COUNTS

Below the primary percentage, show the actual:

Present
Absent
Late

counts for the selected scope.

Make sure the values correspond exactly to the underlying records.

For example:

Selected subject
+
selected date range

must produce the correct count.

Do not mix:

monthly values
with
semester values.

---

# 9. TREND / CHANGE INDICATOR

The reference contains a small positive change indicator.

Do NOT display:

“+2.1% this month”

unless the backend/data actually supports that calculation.

If the comparison can be computed:

compare current period against the appropriate previous period according to product rules.

Then display the calculated difference.

If there is insufficient data:

show a truthful state such as:

“Not enough history yet”

rather than inventing a trend.

---

# 10. CALENDAR

This is the second major interaction.

Implement the premium calendar from the reference.

Requirements:

* correct month
* correct weekdays
* correct dates
* previous month dates where appropriate
* next month navigation
* selected day
* current day indication
* attendance status indication

The calendar MUST be generated from actual date data.

Do NOT hardcode September 2026 into the production component.

---

# 11. CALENDAR STATUS

Attendance indicators should derive from actual attendance.

For example:

Present:
restrained green

Absent:
restrained red

Late:
restrained amber

No record:
neutral

Selected date:
TrackMyClass indigo/blue-violet accent

Do not use color alone.

Use subtle visual markers/icons where appropriate.

---

# 12. CALENDAR VISUAL DESIGN

Match the approved iOS-inspired style:

* soft cells
* rounded corners
* generous spacing
* subtle surface elevation
* restrained borders
* clear selected state

Do NOT make the calendar look like:

* a spreadsheet
* Material Design
* Bootstrap
* old-school calendar widgets

---

# 13. SELECTED DAY

When the user selects a date, update the lower section.

Show:

date
subject
attendance status
lecture/session details where supported

Example:

Present
Data Structures
09:00–10:00 AM

Use real session data.

Do not fabricate lecture times.

---

# 14. SELECTED-DAY STATE

Handle:

Present
Absent
Late
Not Marked
No Session
No Attendance Data

These states must be clearly distinguishable.

Do not treat:

No Session

as:

Absent.

Do not treat:

No data

as:

Absent.

---

# 15. DATE NAVIGATION

When switching month:

* fetch/use the correct attendance data
* update calendar
* preserve subject selection
* prevent stale results
* handle loading cleanly

Rapid month switching must not allow an old request to overwrite the latest month.

---

# 16. MOBILE-FIRST

Primary:

390 × 844

Also test:

320 × 844
375 × 812
430 × 932

The mobile screen must preserve the approved visual hierarchy.

At 320px:

* no horizontal overflow
* no clipped cards
* calendar remains usable
* bottom navigation remains accessible
* selected-day section remains readable

Do NOT simply shrink typography to force the layout to fit.

---

# 17. DESKTOP RESPONSIVENESS

Support:

768
1024
1280
1440

Desktop should expand naturally.

Do NOT stretch everything across the entire width.

Use an appropriately constrained content area.

Possible desktop composition:

sidebar/navigation
+
attendance workspace
+
optional supporting context

Preserve the mobile information hierarchy.

---

# 18. BOTTOM NAVIGATION

Match the approved Student navigation:

Home
Attendance
Classes
Profile

Attendance must be visibly active.

Reuse the existing navigation implementation.

Do NOT create a duplicate navigation component.

---

# 19. IOS-INSPIRED VISUAL LANGUAGE

The reference is inspired by iOS.

Implement the characteristics, NOT proprietary Apple UI code.

Use:

* generous whitespace
* rounded surfaces
* subtle translucency where appropriate
* soft shadows
* tactile controls
* clear hierarchy
* restrained animation

Do NOT overdo glassmorphism.

This is a web SaaS product with an iOS-inspired visual language.

---

# 20. TYPOGRAPHY

Use:

```css id="4sfhjs"
font-family:
  -apple-system,
  BlinkMacSystemFont,
  "SF Pro Display",
  "SF Pro Text",
  "Segoe UI",
  Roboto,
  Helvetica,
  Arial,
  sans-serif;
```

Do NOT bundle proprietary Apple fonts.

Use:

400
500
600
700

with 700 used sparingly.

Use tabular numerals for:

attendance percentages
counts
dates

where appropriate.

---

# 21. COLORS

Use the established TrackMyClass palette.

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

Neutrals:

soft off-white
white
deep charcoal
cool gray

Do NOT introduce unrelated colors.

---

# 22. LIGHT MODE

Match the approved reference.

Use:

soft background
white/elevated surfaces
deep text
subtle borders
soft shadows

Do not make every surface pure white.

Maintain depth through subtle contrast.

---

# 23. DARK MODE

Implement a first-class dark mode version.

Do NOT invert colors.

Use:

deep charcoal background
slightly elevated surfaces
soft white text
subtle borders
restrained indigo
restrained semantic colors

The calendar must remain readable.

The progress ring must remain clear.

The selected day must remain obvious.

---

# 24. THEME SWITCHING

Use the existing global theme implementation.

Theme must persist across:

Home
Attendance
Classes
Profile

Switching themes should not reload the page.

Do not create a page-specific theme system.

---

# 25. MOTION

Use subtle motion for:

* segmented control changes
* month transitions
* date selection
* card updates
* theme transition

Use short, natural transitions.

Respect:

`prefers-reduced-motion`

No flashy animation.

---

# 26. LOADING

Use skeleton states.

Examples:

hero metric skeleton
summary skeleton
calendar skeleton
selected-day skeleton

Do NOT show fake previous data while the new subject/month is loading unless explicitly intentional and labeled.

Do not use a giant full-screen spinner.

---

# 27. ERROR

If attendance cannot load:

“Unable to load attendance.”

Action:

“Try again”

Do NOT display fallback fake values.

A failed request must NEVER look like legitimate attendance data.

---

# 28. EMPTY STATE

For a student with no attendance records:

“No attendance records yet.”

Supporting:

“Your attendance will appear here after your first class.”

Do not display:

0%
87%
100%

unless those values are genuinely meaningful from the data model.

---

# 29. SUBJECT EMPTY STATE

If the student has no attendance records for the selected subject:

show:

“No attendance for this subject yet.”

Do not inherit values from another subject.

---

# 30. ATTENDANCE DATA CONSISTENCY

The same attendance record should produce consistent results across:

Student Dashboard
Student Attendance
Teacher Attendance
Reports
Admin Analytics

For:

same student
same subject
same session range

the displayed percentage must agree.

If different screens calculate differently:

fix the common authoritative calculation.

---

# 31. CACHE / STATE CORRECTNESS

Verify:

Subject A
→ Subject B
→ Subject A

always returns correct data.

Verify:

September
→ October
→ September

always returns correct data.

No stale percentages.

No stale calendar markers.

No stale selected-day information.

---

# 32. REQUEST CORRECTNESS

Audit React effects.

Make sure there is:

* no request loop
* no duplicate fetch
* no unnecessary refetch
* no stale response overwrite
* no subject-switch race
* no month-switch race

Use cancellation or stale-result protection appropriately.

---

# 33. ACCESSIBILITY

Implement:

* semantic buttons
* accessible segmented control
* accessible calendar navigation
* keyboard navigation where appropriate
* visible focus
* screen-reader-friendly date/status
* non-color-only status
* 44px+ touch targets where practical

Calendar date buttons must be understandable to assistive technologies.

---

# 34. PERFORMANCE

Keep the screen lightweight.

Do NOT install a giant calendar framework if the project already has sufficient capabilities.

Prefer existing dependencies or a small native implementation.

Avoid:

* unnecessary rerenders
* repeated API calls
* expensive calendar recalculation
* unnecessary animations

---

# 35. DEPENDENCY RULE

Before installing ANY package:

inspect existing `package.json`.

Prefer existing:

* icon library
* chart library
* date utilities
* UI components

Do not install multiple libraries solving the same problem.

If a dependency is genuinely required, document why.

---

# 36. REAL BROWSER TEST

Login as a real student.

Perform:

1. Open Attendance
2. Verify real overall attendance
3. Compare against backend/API
4. Select subject A
5. Verify subject-specific attendance
6. Select subject B
7. Verify independent attendance
8. Return to subject A
9. Verify correct value
10. Navigate to previous month
11. Navigate forward
12. Select a real attendance date
13. Verify selected-day details
14. Switch light/dark
15. Reload
16. Verify theme persistence
17. Verify data remains identical
18. Return to Home
19. Return to Attendance
20. Verify state remains correct

---

# 37. CONTROLLED DATA TEST

Use a controlled test student.

Example:

Data Structures:

Present
Present
Present
Absent

Expected:

75%

Operating Systems:

Present
Absent
Absent
Absent

Expected:

25%

Verify the UI displays the correct values.

Do not use visual examples as evidence.

---

# 38. AUTOMATED TESTS

Add/update tests covering:

* attendance calculation
* subject selection
* calendar generation
* date selection
* month navigation
* Present state
* Absent state
* Late state
* no-session state
* empty state
* loading state
* API error
* stale response protection
* theme rendering
* responsive rendering where the test framework supports it

---

# 39. VISUAL QA

Compare the REAL running implementation against the attached reference.

Inspect:

* header
* title
* segmented control
* hero card
* progress visualization
* summary counts
* subject card
* calendar
* selected day
* bottom navigation
* spacing
* typography
* shadows
* colors
* corner radii

Correct visible mismatches.

Do not stop at “functionally correct.”

---

# 40. REGRESSION

After implementation, verify:

Student Home
Student Profile
Student Classes
Face Registration
Teacher Attendance
Teacher Live
Students Directory
Admin Dashboard
Login

No existing navigation/theme/shared-component regressions.

---

# 41. DOCUMENTATION

Update:

```text id="zwu2bj"
docs/UI_DESIGN_SYSTEM.md
docs/UI_IMPLEMENTATION_LOG.md
docs/CHANGELOG.md
docs/ENGINEERING_ROADMAP.md
```

Also update relevant attendance documentation if calculation behavior changes.

Document:

* screen implementation
* subject behavior
* calculation rules
* calendar behavior
* theme behavior
* responsive behavior
* tests
* browser verification
* defects/fixes

Clearly distinguish:

TESTED
OBSERVED
ESTIMATED

---

# 42. FINAL REPORT

Return:

## UI

What was implemented.

## Data

Where attendance data comes from.

## Calculation

Exact attendance formula.

## Subject Isolation

How subject-specific attendance is enforced.

## Calendar

How dates/statuses are derived.

## Theme

Light/dark implementation.

## Responsive

Actual viewports tested.

## Tests

Passed/failed.

## Browser Verification

Actual student workflow.

## Defects

DISCOVERED
→ REPRODUCED
→ ROOT CAUSE
→ FIXED
→ REGRESSION TESTED

## Remaining Issues

Anything unresolved.

---

# 43. DEFINITION OF DONE

[ ] Approved reference implemented faithfully
[ ] Real authenticated student data
[ ] No fake attendance
[ ] No hardcoded percentages
[ ] Correct overall calculation
[ ] Correct subject calculation
[ ] Subject switching works
[ ] Month navigation works
[ ] Calendar uses real data
[ ] Selected day works
[ ] Present/Absent/Late states correct
[ ] No-data state correct
[ ] Loading state correct
[ ] Error state correct
[ ] No stale subject data
[ ] No stale month data
[ ] No request loops
[ ] No duplicate fetches
[ ] Light mode works
[ ] Dark mode works
[ ] Theme persists
[ ] Mobile 320px works
[ ] Mobile 375px works
[ ] Mobile 390px works
[ ] Mobile 430px works
[ ] Tablet works
[ ] Desktop works
[ ] Accessibility checked
[ ] No unnecessary dependency added
[ ] Automated tests pass
[ ] Real browser verification completed
[ ] Regression completed
[ ] Documentation updated

---

# FINAL RULE

This is NOT a decorative attendance calendar.

It is the student's authoritative view of their attendance.

Every percentage must be traceable to real attendance records.

Every calendar state must be traceable to real sessions.

Every subject must remain independent.

The attached image controls the visual design.

The existing TrackMyClass backend/data model controls the functional truth.

Make it look like an exceptionally polished iOS-inspired product while keeping the implementation simple, maintainable, responsive, and real.



# CRITICAL DATA INTEGRITY REQUIREMENT

THIS IS A REAL PRODUCTION APPLICATION.

DO NOT USE DUMMY DATA ANYWHERE IN THE STUDENT ATTENDANCE SCREEN.

The following are STRICTLY FORBIDDEN in production UI:

- hardcoded attendance percentages
- hardcoded Present/Absent/Late counts
- fake subjects
- fake student names
- fake class names
- fake teacher names
- fake dates
- fake calendar attendance markers
- fake trend values
- fake “improvement” percentages
- random values
- mock API responses
- sample JSON
- screenshot/example values
- fallback demo objects
- placeholder attendance records
- fabricated recent activity

Do NOT use values from the approved design image as application data.

The visual reference controls ONLY DESIGN.

The backend/database controls ALL DATA.

==================================================
REAL DATA ONLY
==================================================

Every visible value must come from the authenticated student's real application data.

Trace every displayed value through:

DATABASE
→ REPOSITORY
→ SERVICE
→ API
→ FRONTEND STATE
→ UI

For every number displayed, it must be possible to answer:

“Which real attendance records produced this number?”

If that cannot be answered, DO NOT DISPLAY THE NUMBER.

==================================================
NO FAKE FALLBACKS
==================================================

This is especially important.

If the API fails:

DO NOT show 87.4%
DO NOT show 0%
DO NOT show 100%
DO NOT show yesterday's unrelated value
DO NOT show demo values

Instead show:

“Unable to load attendance.”

with:

“Try again”

If the student genuinely has no attendance records:

show:

“No attendance records yet.”

Do not replace missing data with believable fake data.

==================================================
LOADING DATA
==================================================

While data is loading:

show skeleton/loading UI.

Do NOT temporarily render hardcoded example values.

For example, do not do:

attendance ?? 87.4

Do not do:

subjects.length ? subjects : demoSubjects

Do not do:

data || mockData

Do not do:

percentage || 0

unless zero is mathematically and semantically correct.

==================================================
NULL / MISSING VALUES
==================================================

Handle null/missing data explicitly.

A missing value is NOT automatically:

0
100
Present
Absent

Use an intentional unavailable/empty state.

==================================================
AUTHENTICATED STUDENT
==================================================

Only display data belonging to the currently authenticated student.

Do NOT obtain the student identity from:

- query parameters
- arbitrary URL IDs
- hidden form fields
- client-controlled localStorage values
- manually supplied student IDs

Use the existing authenticated-user architecture.

Backend authorization remains authoritative.

==================================================
INSTITUTION ISOLATION
==================================================

Attendance must belong to the authenticated student's institution.

Do not display records from another institution.

Never trust a client-supplied institution_id as proof of access.

==================================================
SUBJECT-SPECIFIC DATA
==================================================

Every subject must be loaded from actual backend data.

When the student selects:

Data Structures

the displayed:

- percentage
- present count
- absent count
- late count
- calendar markers
- selected-day details
- trend

must correspond ONLY to Data Structures records.

When switching to:

Operating Systems

ALL subject-specific information must update to Operating Systems data.

No previous-subject values may remain.

==================================================
ATTENDANCE CALCULATION
==================================================

Do not calculate from presentation values.

Calculate from the authoritative attendance records.

Conceptually:

attendance =
eligible attended sessions / eligible sessions

Use the application's actual attendance semantics for:

Present
Late
Absent
Not Marked
Cancelled
Excused

Document exactly which states are included.

Do not silently invent rules.

==================================================
OVERALL ATTENDANCE
==================================================

Do NOT calculate:

average(subject percentages)

unless the domain explicitly defines overall attendance that way.

Prefer calculation from the underlying eligible sessions according to the project's documented attendance rule.

Do not average already-rounded percentages.

Round only the final displayed value.

==================================================
CALENDAR
==================================================

Calendar status must come from actual session/attendance records.

A green date means there is an actual corresponding attendance state.

A red date means there is an actual corresponding attendance state.

A blank date means there is no relevant attendance record/session.

DO NOT color dates simply to make the calendar look populated.

==================================================
TREND
==================================================

Only display a trend when sufficient historical real data exists.

Every chart point must correspond to real attendance data.

DO NOT generate:

- fake historical points
- synthetic curves
- random fluctuations
- placeholder improvements

If insufficient data exists:

“Not enough attendance history to show a trend.”

==================================================
INSIGHTS
==================================================

Every insight must be derived from actual data.

For example:

“Attendance improved 4.2% this month”

is allowed ONLY if 4.2% is actually calculated from real periods.

Otherwise:

DO NOT INVENT AN INSIGHT.

Use a neutral state instead.

==================================================
RECENT ACTIVITY
==================================================

Every recent attendance event must come from an actual persisted attendance/session record.

Never create fake recent events merely to make the dashboard look populated.

==================================================
CROSS-SCREEN CONSISTENCY
==================================================

For the same student + subject + session range:

Student Dashboard
=
Student Attendance
=
Teacher Attendance
=
Reports

The values must agree.

If they do not agree, find the root cause.

Do NOT patch one screen with a special calculation.

==================================================
REAL DATABASE VERIFICATION
==================================================

Create a controlled test dataset using REAL database records.

Example:

Data Structures:
3 Present
1 Absent

Expected:
75%

Operating Systems:
1 Present
3 Absent

Expected:
25%

Verify:

database
→ API
→ frontend
→ displayed result

matches exactly.

==================================================
PRODUCTION CODE AUDIT
==================================================

Search the production frontend for:

mock
dummy
demo
sample
placeholder
faker
random
fallback
87.4
92
100

Inspect every occurrence.

Do NOT blindly delete legitimate unit-test fixtures.

Separate:

TEST FIXTURES

from:

PRODUCTION DATA PATH.

The production Student Attendance screen must never consume fake data.

==================================================
ABSOLUTE RULE
==================================================

REAL DATA OR HONEST EMPTY/ERROR STATE.

There is NO third option.

If the backend cannot provide a value:

DO NOT MAKE ONE UP.

Never sacrifice data integrity for visual completeness.