import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import PublicLayout from '@/layouts/PublicLayout'
import AdminLayout from '@/layouts/AdminLayout'
import StudentLayout from '@/layouts/StudentLayout'
import TeacherLayout from '@/layouts/TeacherLayout'

import Landing from '@/pages/public/Landing'
import InstitutionPortal from '@/pages/public/InstitutionPortal'
import RoleSelect from '@/pages/public/RoleSelect'
import Register from '@/pages/public/Register'
import Login from '@/pages/public/Login'
import AdminDashboard from '@/pages/admin/Dashboard'
import TeacherLiveClassroom from '@/pages/teacher/LiveClassroom'
import StudentsDir from '@/pages/admin/StudentsDir'
import Reports from '@/pages/admin/Reports'
import StudentDashboard from '@/pages/student/Dashboard'
import StudentAttendance from '@/pages/student/Attendance'
import StudentProfile from '@/pages/student/Profile'
import FaceRegistration from '@/pages/student/FaceRegistration'
import TeacherAttendance from '@/pages/teacher/Attendance'
import PlaceholderPage from '@/pages/Placeholder'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public entry points */}
        <Route path="/" element={<Landing />} />
        <Route path="/onboarding" element={<InstitutionPortal />} />

        {/* Institution-scoped public routes */}
        <Route path="/:collegeCode" element={<PublicLayout />}>
          <Route index element={<RoleSelect />} />
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
        </Route>

        {/* Admin Routes scoped to College */}
        <Route path="/:collegeCode/admin" element={<AdminLayout />}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="sessions/:sessionId/monitor" element={<TeacherLiveClassroom />} />
          <Route path="students" element={<StudentsDir />} />
          <Route path="reports" element={<Reports />} />
        </Route>

        {/* Student Routes scoped to College */}
        <Route path="/:collegeCode/student" element={<StudentLayout />}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<StudentDashboard />} />
          <Route path="attendance" element={<StudentAttendance />} />
          <Route path="profile" element={<StudentProfile />} />
          <Route path="face-enrollment" element={<FaceRegistration />} />
          <Route path="classes" element={<PlaceholderPage title="Classes & Schedule" />} />
        </Route>

        {/* Teacher Routes scoped to College */}
        <Route path="/:collegeCode/teacher" element={<TeacherLayout />}>
          <Route index element={<Navigate to="attendance" replace />} />
          <Route path="attendance" element={<TeacherAttendance />} />
          <Route path="live" element={<TeacherLiveClassroom />} />
          <Route path="classes" element={<PlaceholderPage title="Class Management" />} />
          <Route path="dashboard" element={<PlaceholderPage title="Teacher Dashboard" />} />
          <Route path="more" element={<PlaceholderPage title="Settings & More" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
