import { Outlet, Link, useParams } from "react-router-dom"
import { Toaster } from "sonner"
import { Building2 } from "lucide-react"

export default function PublicLayout() {
  const { collegeCode } = useParams<{ collegeCode: string }>()

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 h-14 flex items-center justify-between">
          <Link to={collegeCode ? `/${collegeCode}` : "/"} className="flex items-center gap-2 font-bold text-lg tracking-tight text-primary">
            <Building2 className="w-5 h-5" />
            TrackMyClass
          </Link>
          <nav className="flex gap-4">
            {collegeCode && (
              <Link to={`/${collegeCode}/login`} className="text-sm font-medium hover:text-primary">Admin Login</Link>
            )}
          </nav>
        </div>
      </header>
      <main className="flex-1">
        <Outlet />
      </main>
      <Toaster position="top-center" />
    </div>
  )
}
