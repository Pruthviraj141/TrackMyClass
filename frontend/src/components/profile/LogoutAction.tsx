import { useNavigate } from "react-router-dom"
import { toast } from "sonner"
// import { api } from "@/lib/api" // Assuming you might have a backend logout API later.

export function LogoutAction() {
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      // Typically invoke a backend logout if required, e.g. api.post('/auth/logout')
      localStorage.removeItem("token")
      toast.success("Successfully logged out")
      navigate("/login", { replace: true })
    } catch (error) {
      toast.error("Failed to log out")
    }
  }

  return (
    <div className="px-5 py-4 mb-20">
      <button 
        onClick={handleLogout}
        className="w-full bg-card rounded-[20px] shadow-[0_4px_20px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_20px_rgb(0,0,0,0.15)] border-none p-4 text-center font-medium text-destructive transition-transform active:scale-[0.98] hover:bg-destructive/5 focus:outline-none focus:ring-2 focus:ring-destructive/30"
      >
        Log out
      </button>
    </div>
  )
}
