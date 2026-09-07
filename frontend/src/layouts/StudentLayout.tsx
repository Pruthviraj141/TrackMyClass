import { Outlet } from "react-router-dom"

export default function StudentLayout() {
  // Authentication check could go here if needed
  return (
    <div className="min-h-screen bg-background">
      <Outlet />
    </div>
  )
}
