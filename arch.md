Yes bro. **This is the correct correction to make before doing more UI.** The current flow mixed up three different concepts:

**Institution discovery/access ≠ user authentication ≠ institution administration.**
done with loe 
That is why the experience feels dumb and why you are hitting errors.

# The correct TrackMyClass flow

Think of the product like this:

```text
                    TRACKMYCLASS
                         │
                 ┌───────┴────────┐
                 │                │
          CREATE INSTITUTION   ACCESS INSTITUTION
                 │                │
          Institution Admin      Institution ID/Code
          creates workspace             │
                                       ▼
                              Institution identified
                                       │
                          ┌────────────┼────────────┐
                          │            │            │
                       STUDENT      TEACHER      ADMIN
                          │            │            │
                       Login        Login        Login
                          │            │            │
                       Student      Teacher     Institution
                       Portal       Portal       Admin
```

## 1. First screen — Institution Access

This should be **completely different** from the normal Login page.

Route:

```text
/institution/access
```

Screen:

> **Welcome to TrackMyClass**

> Enter your institution ID to continue.

```text
Institution ID
[ VIT2026 ]

        Continue
```

That's it.

No:

* student email
* teacher email
* password
* face registration
* giant institution creation form

The purpose of this page is only:

**“Which institution are you trying to access?”**

---

# 2. Institution verification

When the user enters:

```text
VIT2026
```

frontend calls something like:

```http
POST /public/institutions/resolve
```

Backend verifies the code.

Successful response conceptually:

```json
{
  "institution": {
    "id": "inst_123",
    "name": "Vishwakarma Institute of Technology",
    "slug": "vit-pune"
  }
}
```

Now the application knows:

> You're accessing VIT Pune.

The frontend should show:

### Vishwakarma Institute of Technology

```text
Continue as

[ Student ]

[ Teacher ]

[ Institution Admin ]
```

**The institution code is NOT asked again.**

That is the mistake in the current flow.

---

# 3. Student Login

Route:

```text
/institution/vit-pune/student/login
```

Now the student sees:

> Welcome back

> Vishwakarma Institute of Technology

```text
Email
[ ]

Password
[ ]

Forgot password?

[ Sign in ]
```

That's all.

There is **NO institution-code field** here.

Because institution context has already been established.

---

# 4. Teacher Login

Route:

```text
/institution/vit-pune/teacher/login
```

Same principle:

> Teacher Sign In

> Vishwakarma Institute of Technology

```text
Email
[ ]

Password
[ ]

[ Sign in ]
```

Again:

**NO institution code.**

The backend receives the institution context together with authentication and verifies that the teacher actually belongs to that institution.

---

# 5. Institution Admin Login

This should be separate.

Route:

```text
/institution/vit-pune/admin/login
```

For example:

> Institution Administration

```text
Admin email
[ ]

Password
[ ]

[ Sign in ]
```

Admin gets access to:

```text
Admin Dashboard
Students
Classes
Sessions
Attendance
Reports
Analytics
Diagnostics
Settings
```

Students and teachers should never see those things.

---

# 6. Student registration

This should also respect the institution-first flow.

The student does:

```text
Institution Access
        ↓
Enter Institution ID
        ↓
Institution verified
        ↓
Student
        ↓
Create Student Account
        ↓
Personal Details
        ↓
Face Registration
        ↓
Review
        ↓
Account Created
        ↓
Student Dashboard
```

So the student **never enters the institution code twice**.

The registration URL could be:

```text
/institution/vit-pune/student/register
```

### Registration steps

```text
1. Account
2. Personal Details
3. Face Registration
4. Review
5. Complete
```

And because the institution is already known, fields can be:

```text
Full Name
Roll Number
Email
Password
Class / Section
```

Institution:

```text
Vishwakarma Institute of Technology
```

shown as **read-only context**, not another input.

---

# 7. Teacher registration should be different

This is important.

I would **NOT** allow unrestricted teacher self-registration.

Better:

```text
Institution Admin
       ↓
Creates / invites teacher
       ↓
Teacher receives invitation
       ↓
Teacher sets account/password
       ↓
Teacher Login
```

Possible route:

```text
/institution/vit-pune/teacher/accept-invite
```

This prevents random people from claiming to be teachers.

So:

**Student → controlled self-registration**

**Teacher → institution-controlled onboarding**

**Admin → institution-controlled**

That's much more realistic.

---

# 8. Creating an institution is a completely different journey

This is where our previous Institution Portal was wrong.

It should NOT look like:

> “Enter your institution code”

because the institution doesn't have a code yet.

Instead:

```text
/institution/register
```

This is for the person creating a **new TrackMyClass institution**.

Example:

# Create your institution

```text
Institution name
[ Vishwakarma Institute of Technology ]

Institution type
[ College ▼ ]

Official email
[ admin@college.edu ]

Create institution
```

Then:

```text
Create Institution
        ↓
Institution created
        ↓
Institution ID generated
        ↓
Create first Admin
        ↓
Admin Dashboard
```

For example:

```text
Your institution is ready

Institution ID

VIT2026

Share this ID with students and teachers.
```

That ID becomes the gateway to the institution.

---

# 9. The complete product flow

This is the flow I'd lock into the project:

```text
                    TRACKMYCLASS
                         │
              ┌──────────┴──────────┐
              │                     │
       CREATE INSTITUTION      ACCESS INSTITUTION
              │                     │
       /institution/register   /institution/access
              │                     │
              ▼                     ▼
       Institution created     Institution ID
              │                     │
              ▼                     ▼
       First Admin account     Institution verified
                                    │
                         ┌──────────┼──────────┐
                         │          │          │
                      STUDENT    TEACHER     ADMIN
                         │          │          │
                       Login      Login      Login
                         │          │          │
                         ▼          ▼          ▼
                     Student    Teacher     Admin
                     Dashboard  Dashboard   Dashboard
```

---

# 10. After Student Login

```text
Student
  │
  ├── Home
  ├── Attendance
  ├── Classes
  ├── Profile
  └── Face Registration
```

Student should only see **their own data**.

For example:

```text
87.4% attendance

Today's classes

Attendance history

Profile

Face recognition status
```

They should NEVER see:

* other students
* institution-wide analytics
* teacher controls
* diagnostics
* Redis
* recognition-worker information
* admin reports

---

# 11. After Teacher Login

```text
Teacher
  │
  ├── Home
  ├── Classes
  ├── Live
  ├── Attendance
  ├── Students
  ├── Reports
  └── More
```

Teacher can access only authorized classes/students.

Flow:

```text
Teacher
 ↓
Select Class
 ↓
Start Session
 ↓
Live Camera
 ↓
Face Recognition
 ↓
Attendance Events
 ↓
Attendance Review
 ↓
Finalize
 ↓
Report
```

This is the core TrackMyClass workflow.

---

# 12. Institution Admin

```text
Admin
 │
 ├── Overview
 ├── Students
 ├── Classes & Sessions
 ├── Attendance
 ├── Reports
 ├── Analytics
 ├── System / Diagnostics
 └── Settings
```

Admin controls the institution.

They can:

```text
Add student
Invite teacher
Create class
Manage sessions
View institution attendance
Generate reports
View analytics
Manage institution
```

---

# 13. The most important security rule

There is one subtle thing we must get right.

Entering:

```text
VIT2026
```

does **NOT** mean:

> “I am authorized to access VIT.”

It only means:

> “I want to access the VIT institution.”

Then authentication happens.

So:

```text
Institution ID
        ↓
Identify institution
        ↓
User Login
        ↓
Authenticate identity
        ↓
Check membership
        ↓
Authorize role
        ↓
Give access
```

The backend must verify:

```text
Does this user actually belong to this institution?
Is this user actually a student/teacher/admin?
What resources can they access?
```

This is essential for your existing tenant-isolation architecture.

---

# 14. Routes I would lock

```text
/
├── institution
│   ├── access
│   ├── register
│   └── :institutionSlug
│       ├── welcome
│       │
│       ├── student
│       │   ├── login
│       │   ├── register
│       │   └── dashboard
│       │
│       ├── teacher
│       │   ├── login
│       │   └── dashboard
│       │
│       └── admin
│           ├── login
│           └── dashboard
│
└── public
    ├── terms
    └── privacy
```

Then protected application routes:

```text
/student/*
/teacher/*
/admin/*
```

The exact route syntax can be adapted to your existing React router.

---

# 15. What I would change RIGHT NOW

Before designing another screen, I'd have Antigravity perform a **flow correction pass**.

Not another UI redesign.

Not another dashboard.

First fix the product's navigation and authentication architecture:

```text
Institution Access
        ↓
Institution Context
        ↓
Role Selection
        ↓
Student / Teacher / Admin Login
        ↓
Role Dashboard
```

Then:

```text
Student Registration
        ↓
Institution already known
        ↓
Account
        ↓
Personal Details
        ↓
Face Registration
        ↓
Review
        ↓
Dashboard
```

That will eliminate the stupid:

```text
Institution Code
↓
Institution Login
↓
Institution Code AGAIN
```

flow.

### And one more important distinction

**Institution Access** and **Create Institution** should look completely different.

`/institution/access`

= **“I already belong to an institution.”**

`/institution/register`

= **“I am creating a new institution.”**

That single distinction will make the whole product feel dramatically more professional.

Your existing documentation already establishes institution-code verification and tenant-aware authorization, so this flow is much more consistent with what TrackMyClass already has than adding another parallel onboarding model.

---

## 🔥 Antigravity should fix the flow before more UI

I would give Antigravity a **new architecture-correction task**, not another individual screen prompt.

# CRITICAL ARCHITECTURE + UX CORRECTION

# TRACKMYCLASS — INSTITUTION-FIRST ACCESS FLOW

The current authentication/onboarding flow is logically incorrect.

STOP adding new UI screens until the institution/user access flow is corrected.

The required product model is:

INSTITUTION IDENTIFICATION
→ USER AUTHENTICATION
→ ROLE AUTHORIZATION
→ ROLE-SPECIFIC APPLICATION

The institution code/ID must establish the institution context BEFORE Student/Teacher/Admin login.

A user must NOT be asked for the institution code again after institution access has already been verified.

---

# 1. REQUIRED PRODUCT FLOW

Implement this conceptual flow:

TrackMyClass
│
├── Create Institution
│
│   /institution/register
│
│   Create institution
│   ↓
│   Generate institution ID/code
│   ↓
│   Create first institution admin
│   ↓
│   Admin Dashboard
│
└── Access Existing Institution
│
/institution/access
│
Enter institution ID/code
│
↓
Verify institution
│
↓
Institution context established
│
├── Student
│   ↓
│   Student Login / Registration
│   ↓
│   Student Dashboard
│
├── Teacher
│   ↓
│   Teacher Login
│   ↓
│   Teacher Dashboard
│
└── Institution Admin
↓
Admin Login
↓
Admin Dashboard

---

# 2. REMOVE THE INCORRECT FLOW

The application MUST NOT do:

Institution Code
→ Institution Login
→ Institution Code again
→ Student/Teacher Login

That is incorrect.

Institution identity must be established once at the entry point.

After that, the user should see the selected institution and choose their role.

---

# 3. INSTITUTION ACCESS SCREEN

Create/use:

/institution/access

Purpose:

Identify an EXISTING institution.

This is NOT institution creation.

UI should contain approximately:

TrackMyClass

Welcome to your institution

Institution ID / Code

[ input ]

[ Continue ]

Supporting text:

“Enter the institution ID provided by your college, school, or organization.”

Do NOT ask:

email
password
student details
teacher details

at this stage.

---

# 4. INSTITUTION RESOLUTION

Inspect existing backend institution-code verification.

Reuse the existing endpoint if available.

Do NOT create a duplicate institution verification API without necessity.

The backend should resolve:

institution code
→ institution identity/public metadata

The frontend may receive safe information such as:

institution ID
institution name
institution slug
public logo if supported

Do not treat the returned institution identity as authorization.

---

# 5. AFTER INSTITUTION VERIFICATION

After successful institution verification, show a distinct institution welcome/role-selection screen.

Example:

Vishwakarma Institute of Technology

Welcome to TrackMyClass

Continue as:

[ Student ]

[ Teacher ]

[ Institution Admin ]

The exact role options must correspond to the roles actually supported by the application.

The institution code must NOT be requested again.

---

# 6. STUDENT LOGIN

Route concept:

/institution/:institutionSlug/student/login

OR adapt to the existing router architecture.

The page should show:

Institution name

Student Sign In

Email

Password

Forgot password if actually supported

Sign In

There must be NO institution code input on this page.

The previously resolved institution context should be carried forward safely.

---

# 7. TEACHER LOGIN

Route concept:

/institution/:institutionSlug/teacher/login

Teacher Sign In

Institution name

Email

Password

Sign In

NO institution-code field.

Backend must verify teacher membership.

---

# 8. ADMIN LOGIN

Route concept:

/institution/:institutionSlug/admin/login

Institution Administration

Admin email

Password

Sign In

NO institution-code field.

Backend must verify admin role and institution membership.

---

# 9. INSTITUTION CONTEXT

Do not rely on a client-controlled institution_id for authorization.

The frontend may maintain institution context for navigation/UI.

The backend MUST validate:

authenticated user
+
institution
+
membership
+
role

before allowing protected resources.

If the current JWT architecture already supports institution claims, preserve it while ensuring server-side authorization remains authoritative.

Do not create insecure client-only tenant authorization.

---

# 10. STUDENT REGISTRATION

Student registration must inherit the institution context.

Flow:

Institution Access
→ Institution verified
→ Student
→ Register

Student registration should NOT ask for institution code again.

Conceptual route:

/institution/:institutionSlug/student/register

Fields should use the existing backend contract.

Potential:

Full name
Email
Password
Roll number
Class / Section

Only include fields actually supported by the backend.

Institution should appear as read-only context:

“Vishwakarma Institute of Technology”

Do not make the student manually select another institution after verification.

---

# 11. STUDENT FACE REGISTRATION

After successful student account creation:

Account
→ Personal Details
→ Face Registration
→ Review
→ Complete

The existing Face Registration screen should integrate naturally into this onboarding flow.

Do NOT send the student back to institution selection.

Do NOT ask for institution code again.

---

# 12. TEACHER ONBOARDING

Inspect the existing teacher-management architecture.

Prefer:

Institution Admin
→ Invite/Create Teacher
→ Teacher accepts invitation
→ Teacher sets credentials
→ Teacher Login

Do NOT introduce unrestricted public teacher signup unless the existing product explicitly supports it.

---

# 13. INSTITUTION CREATION

Keep institution creation completely separate from institution access.

Route:

/institution/register

Purpose:

Create a NEW institution.

This flow may contain:

Institution name
Institution type
Official email
Other backend-supported institution fields

After successful creation:

Institution created
→ Institution ID/code generated
→ First admin onboarding
→ Admin Dashboard

Do not ask for an institution code to create a new institution unless the backend explicitly requires a parent/organization code.

---

# 14. ADMIN ROLE

The first institution creator should become the appropriate institution administrator only if the existing backend architecture supports that behavior.

Do not silently grant SUPER_ADMIN privileges.

Distinguish:

SUPER_ADMIN
INSTITUTION_ADMIN
TEACHER
STUDENT

according to the current role model.

---

# 15. ROUTING RULES

The router must enforce logical separation.

Public:

/institution/access
/institution/register

Institution-aware but unauthenticated:

/institution/:institutionSlug
/institution/:institutionSlug/student/login
/institution/:institutionSlug/student/register
/institution/:institutionSlug/teacher/login
/institution/:institutionSlug/admin/login

Protected:

/student/*
/teacher/*
/admin/*

Use the existing application's routing conventions where different.

Do not create duplicate routes.

---

# 16. AUTHORIZATION

Authentication and authorization are separate.

Authentication:

“Who are you?”

Authorization:

“Are you allowed to access this institution/resource?”

Every protected request must continue using the existing server-side authorization architecture.

The UI must never be the authorization authority.

---

# 17. NO INSTITUTION CODE DUPLICATION

This is a HARD REQUIREMENT.

Once:

/institution/access

has successfully established the institution context, subsequent login/registration screens MUST NOT ask for the institution code again.

The only exception would be an explicit “Switch institution” action.

---

# 18. SWITCH INSTITUTION

Provide a clear way to leave the current institution context.

Example:

“Switch institution”

This should take the user back to:

/institution/access

Do not silently allow users to switch institutions by editing URL parameters.

---

# 19. ERROR HANDLING

Institution access failure:

“Couldn't find that institution.”

Invalid code:

“Check your institution ID and try again.”

Login failure:

“Incorrect email or password.”

Membership failure:

“You don't have access to this institution.”

Do NOT expose:

database errors
Redis errors
JWT internals
stack traces
SQL errors
Python exceptions

---

# 20. LOADING STATES

Institution verification:

“Checking institution…”

Login:

“Signing in…”

Registration:

“Creating account…”

Use button-level loading.

Prevent duplicate submissions.

---

# 21. SECURITY TESTS

Verify:

* valid institution code resolves correct institution
* invalid institution code rejected
* student cannot authenticate into another institution
* teacher cannot authenticate into another institution
* admin cannot access another institution
* URL institution slug cannot bypass membership
* client-controlled institution_id cannot bypass authorization
* institution context is not treated as proof of identity
* JWT/authentication flow remains secure

---

# 22. ROUTE TEST MATRIX

Create automated tests for:

### Public

/institution/access
/institution/register

### Institution context

valid institution
invalid institution
switch institution

### Student

student login
student registration
student dashboard
student cannot access teacher routes
student cannot access admin routes

### Teacher

teacher login
teacher dashboard
teacher cannot access student/admin restricted resources

### Admin

admin login
admin dashboard
admin cannot access another institution

---

# 23. REAL BROWSER TEST

Use a real running application.

Test the exact workflow:

1. Open TrackMyClass
2. Choose Access Institution
3. Enter valid institution ID
4. Institution resolves
5. Institution name appears
6. Choose Student
7. Student login appears WITHOUT institution-code field
8. Login
9. Student dashboard loads
10. Logout
11. Return to institution context
12. Choose Teacher
13. Teacher login appears WITHOUT institution-code field
14. Authenticate appropriate teacher
15. Teacher dashboard loads
16. Logout
17. Choose Admin
18. Admin login appears WITHOUT institution-code field
19. Admin dashboard loads
20. Switch institution
21. Return to institution access

Also test invalid institution codes.

---

# 24. UI REQUIREMENT

The institution access screen must be visually DIFFERENT from:

Student Login
Teacher Login
Admin Login
Institution Creation

Each has a different purpose.

Do not reuse one giant form for all four workflows.

---

# 25. DO NOT REDESIGN EVERYTHING

Preserve the existing approved visual language:

* Apple-style system typography
* indigo / blue-violet brand
* premium SaaS
* mobile-first
* light/dark mode
* semantic states
* accessible controls

This task is about correcting the FLOW and integrating the correct UI, not replacing the entire design system.

---

# 26. DOCUMENT THE NEW FLOW

Update:

docs/ARCHITECTURE_CURRENT.md
docs/ARCHITECTURE_TARGET.md
docs/API_INVENTORY.md
docs/UI_DESIGN_SYSTEM.md
docs/UI_IMPLEMENTATION_LOG.md
docs/CHANGELOG.md
docs/ENGINEERING_ROADMAP.md

Add/update a dedicated flow document if useful:

docs/AUTHENTICATION_AND_TENANT_FLOW.md

Document:

Institution creation
Institution access
Institution resolution
Student login
Teacher login
Admin login
Student registration
Teacher onboarding
Tenant authorization
Switch institution

---

# 27. DEFINITION OF DONE

[ ] Institution creation is separate from institution access
[ ] Institution access is the first step for existing institution users
[ ] Institution ID/code is entered once
[ ] Institution is resolved by backend
[ ] Student login does not ask institution code again
[ ] Teacher login does not ask institution code again
[ ] Admin login does not ask institution code again
[ ] Institution context persists correctly through authentication
[ ] Backend validates user membership
[ ] Tenant isolation remains enforced
[ ] Student registration inherits institution context
[ ] Face registration integrates into student onboarding
[ ] Teacher onboarding follows actual institutional permissions
[ ] Switch institution works
[ ] Invalid institution handled correctly
[ ] Loading states work
[ ] Error states work
[ ] Mobile works
[ ] Desktop works
[ ] Light mode works
[ ] Dark mode works
[ ] Automated route/security tests pass
[ ] Real browser workflow passes
[ ] Documentation updated

FINAL RULE:

DO NOT patch the current broken flow with more forms.

FIX THE PRODUCT MODEL.

The correct sequence is:

INSTITUTION IDENTIFICATION
→ AUTHENTICATION
→ AUTHORIZATION
→ ROLE APPLICATION

A user should NEVER have to repeatedly enter the same institution information merely because they are moving from institution access to Student/Teacher/Admin login.

**I would do this correction before we generate any more pages.** Once this flow is fixed, the rest of the UI routes become much easier to make logically consistent.
