import { useState } from "react"
import { Eye, EyeOff, Lock, Loader2, ArrowLeft } from "lucide-react"
import { useNavigate, useParams, Link, useSearchParams } from "react-router-dom"
import { api } from "@/lib/api"
import { Input } from "@/components/ui/input"

export default function Login() {
  const [identifier, setIdentifier] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  
  const navigate = useNavigate()
  const { collegeCode } = useParams<{ collegeCode: string }>()
  const [searchParams] = useSearchParams()
  const role = searchParams.get("role") || "student" // student, teacher, admin

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!identifier.trim() || !password) {
      setErrorMsg("Please enter your credentials.")
      return
    }

    setIsLoading(true)
    setErrorMsg(null)
    const cleanInput = identifier.trim()

    try {
      const formData = new FormData()
      const loginType = role === "student" ? "student" : "admin" 
      formData.append("login_type", loginType)
      formData.append("institution_id", collegeCode?.toUpperCase() || "DEMO2026")

      if (loginType === "admin") {
        formData.append("username", cleanInput)
      } else {
        formData.append("roll_number", cleanInput)
      }
      formData.append("password", password)

      const res = await api.post("/auth/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
      })

      const token = res.data?.access_token
      if (token) {
        localStorage.setItem("token", token)
        const prefix = collegeCode ? `/${collegeCode}` : "/DEMO2026"
        
        if (role === "admin") navigate(`${prefix}/admin/dashboard`)
        else if (role === "teacher") navigate(`${prefix}/teacher/attendance`)
        else navigate(`${prefix}/student/dashboard`)
      } else {
        setErrorMsg("Incorrect credentials.")
      }
    } catch (err: any) {
      setErrorMsg("Incorrect credentials.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#f8f9fc] dark:bg-background flex flex-col justify-between items-center px-4 py-8 select-none font-sans">
      
      {/* Top Spacer / Layout Wrapper */}
      <div className="w-full max-w-[400px] flex-1 flex flex-col justify-center items-center my-auto">
        
        {/* Brand Wordmark Header */}
        <div className="text-center mb-8 relative w-full flex justify-center items-center">
          <button 
            onClick={() => navigate(`/${collegeCode}`)}
            className="absolute left-0 p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors rounded-full hover:bg-slate-100 dark:hover:bg-secondary/50"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-[28px] sm:text-[32px] font-bold tracking-tight text-indigo-950 dark:text-indigo-300 inline-flex items-center gap-1.5">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-900 via-indigo-800 to-indigo-600 dark:from-indigo-300 dark:to-indigo-500">
              TrackMyClass
            </span>
          </h1>
        </div>

        {/* Auth Surface Card */}
        <div className="w-full bg-white dark:bg-card border border-slate-200/80 dark:border-border/40 rounded-[24px] shadow-sm p-6 sm:p-8 space-y-6">
          
          {/* Card Title & Description */}
          <div className="text-center space-y-1.5">
            <h2 className="text-[22px] font-bold tracking-tight text-slate-900 dark:text-foreground capitalize">
              {role} Sign In
            </h2>
            <p className="text-[14px] font-medium text-slate-500 dark:text-muted-foreground">
              Sign in to continue to {collegeCode?.toUpperCase()}.
            </p>
          </div>

          {/* Inline Error Alert */}
          {errorMsg && (
            <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800/50 text-red-600 dark:text-red-400 text-[13px] font-medium px-4 py-3 rounded-[12px] flex items-center justify-between animate-in fade-in slide-in-from-top-1 duration-200">
              <span>{errorMsg}</span>
              <button 
                onClick={() => setErrorMsg(null)} 
                className="text-red-400 hover:text-red-600 dark:hover:text-red-300 text-base font-bold ml-2 leading-none"
              >
                &times;
              </button>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-4" noValidate>
            
            {/* Email / Identifier Field */}
            <div className="space-y-2">
              <label 
                htmlFor="identifier" 
                className="block text-[13px] font-semibold text-slate-700 dark:text-slate-300"
              >
                Email
              </label>
              <Input
                id="identifier"
                type="text"
                autoComplete="username"
                placeholder="you@example.com"
                value={identifier}
                onChange={(e) => {
                  setIdentifier(e.target.value)
                  if (errorMsg) setErrorMsg(null)
                }}
                className="h-[46px] rounded-[12px] bg-white dark:bg-secondary/30 border-slate-200 dark:border-border/60 focus:border-indigo-500 focus:ring-indigo-500/20 text-[15px] px-3.5 shadow-none transition-all placeholder:text-slate-400"
                required
              />
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <label 
                htmlFor="password" 
                className="block text-[13px] font-semibold text-slate-700 dark:text-slate-300"
              >
                Password
              </label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value)
                    if (errorMsg) setErrorMsg(null)
                  }}
                  className="h-[46px] rounded-[12px] bg-white dark:bg-secondary/30 border-slate-200 dark:border-border/60 focus:border-indigo-500 focus:ring-indigo-500/20 text-[15px] pl-3.5 pr-11 shadow-none transition-all placeholder:text-slate-400"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors p-1"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>

              {/* Forgot password right aligned link */}
              <div className="flex justify-end pt-0.5">
                <button
                  type="button"
                  onClick={() => setErrorMsg("Please contact your administrator to reset your password.")}
                  className="text-[13px] font-semibold text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 transition-colors"
                >
                  Forgot password?
                </button>
              </div>
            </div>

            {/* Primary Sign In Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full h-[46px] mt-2 rounded-[12px] bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-[15px] shadow-sm hover:shadow active:scale-[0.99] transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed cursor-pointer"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <span>Sign in</span>
              )}
            </button>

            {/* Secondary Registration Link */}
            <div className="text-center pt-2">
              <p className="text-[13px] font-medium text-slate-500 dark:text-muted-foreground">
                New to TrackMyClass?{" "}
                <Link
                  to={collegeCode ? `/${collegeCode}/register` : "/DEMO2026/register"}
                  className="font-semibold text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 transition-colors"
                >
                  Contact Admin.
                </Link>
              </p>
            </div>
          </form>

          {/* Security Trust Signal Card */}
          <div className="pt-2 border-t border-slate-100 dark:border-border/30">
            <div className="bg-slate-50/80 dark:bg-secondary/20 border border-slate-100 dark:border-border/20 rounded-[14px] p-3 flex items-start gap-3 text-slate-500 dark:text-slate-400">
              <Lock className="w-4 h-4 text-indigo-600 dark:text-indigo-400 flex-shrink-0 mt-0.5" />
              <p className="text-[12px] leading-snug font-medium">
                Your account is protected with secure authentication.
              </p>
            </div>
          </div>

        </div>

      </div>

      {/* Footer */}
      <footer className="w-full text-center py-4">
        <p className="text-[12px] font-medium text-slate-400 dark:text-muted-foreground/60">
          TrackMyClass © 2026. Privacy | Help.
        </p>
      </footer>

    </div>
  )
}
