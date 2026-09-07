import { useState } from "react"
import { useNavigate, useParams, Link } from "react-router-dom"
import { Landmark, LayoutGrid, Mail, Hash, HelpCircle, PhoneCall, MessageSquare, Loader2, ArrowRight } from "lucide-react"
import { api } from "@/lib/api"
import { useStore } from "@/store"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"

export default function InstitutionPortal() {
  const { collegeCode: routeCode } = useParams<{ collegeCode: string }>()
  const navigate = useNavigate()
  const { setInstitution } = useStore()

  const [name, setName] = useState("")
  const [instType, setInstType] = useState("")
  const [email, setEmail] = useState("")
  const [code, setCode] = useState(routeCode && routeCode !== "onboarding" ? routeCode.toUpperCase() : "")
  
  const [isLoading, setIsLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) {
      setErrorMsg("Please enter your institution name.")
      return
    }

    setIsLoading(true)
    setErrorMsg(null)

    try {
      const res = await api.post("/institutions/create", {
        name: name.trim(),
        type: instType,
        email: email.trim(),
        code: code.trim() || undefined
      })

      if (res.data.success) {
        const finalCode = res.data.code
        const finalName = res.data.institutionName
        
        setInstitution(finalCode, finalName)
        toast.success("Institution created successfully!")
        
        // Navigate to the newly created institution's login page as admin
        navigate(`/${finalCode.toLowerCase()}/login?role=admin`)
      } else {
        setErrorMsg(res.data.message || "Failed to create institution.")
      }
    } catch (err: any) {
        setErrorMsg(err.response?.data?.detail || "Could not create institution. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleSupportClick = (topic: string) => {
    toast.info(`${topic}: Our support team is available 24/7 at support@trackmyclass.edu`)
  }

  return (
    <div className="min-h-screen bg-[#f8f9fc] dark:bg-background flex flex-col justify-between items-center relative overflow-hidden select-none font-sans pb-12">
      
      {/* Top Header Bar */}
      <header className="w-full max-w-4xl mx-auto px-5 py-4 flex items-center justify-between z-10">
        
        {/* Logo / Brand */}
        <Link to="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center shadow-sm group-hover:scale-105 transition-transform">
            <Landmark className="w-4 h-4" />
          </div>
          <span className="font-bold text-[18px] tracking-tight text-slate-900 dark:text-foreground">
            TrackMyClass
          </span>
        </Link>

        {/* Existing Institution Sign In Link */}
        <div className="flex items-center gap-2 text-[13px] sm:text-[14px]">
          <span className="text-slate-500 dark:text-muted-foreground hidden xs:inline">
            Already have an institution?
          </span>
          <button 
            onClick={() => navigate(`/${code ? code.toLowerCase() : "DEMO2026"}/login`)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-3.5 py-1.5 rounded-full transition-colors text-[13px]"
          >
            Sign in
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="w-full max-w-[480px] px-4 flex-1 flex flex-col justify-center items-center my-4 z-10">
        
        {/* University Building Graphic Vector */}
        <div className="mb-4 flex items-center justify-center">
          <div className="relative w-24 h-24 sm:w-28 sm:h-28 flex items-center justify-center bg-indigo-50 dark:bg-indigo-950/40 rounded-full border border-indigo-100 dark:border-indigo-800/40 shadow-inner">
            <svg viewBox="0 0 100 100" className="w-16 h-16 sm:w-20 sm:h-20 text-indigo-600 dark:text-indigo-400" fill="none" xmlns="http://www.w3.org/2000/svg">
              {/* Cloud backdrops */}
              <circle cx="20" cy="30" r="10" fill="currentColor" fillOpacity="0.15" />
              <circle cx="80" cy="25" r="8" fill="currentColor" fillOpacity="0.15" />
              {/* Roof triangular pediment */}
              <path d="M50 20 L20 40 L80 40 Z" fill="currentColor" />
              {/* Flag atop roof */}
              <line x1="50" y1="20" x2="50" y2="10" stroke="#F59E0B" strokeWidth="2.5" strokeLinecap="round" />
              <polygon points="50,10 62,14 50,18" fill="#F59E0B" />
              {/* Main facade */}
              <rect x="25" y="40" width="50" height="42" fill="currentColor" fillOpacity="0.2" stroke="currentColor" strokeWidth="2" rx="2" />
              {/* Pillars */}
              <rect x="32" y="46" width="6" height="36" fill="currentColor" rx="1" />
              <rect x="47" y="46" width="6" height="36" fill="currentColor" rx="1" />
              <rect x="62" y="46" width="6" height="36" fill="currentColor" rx="1" />
              {/* Steps */}
              <rect x="20" y="82" width="60" height="4" fill="currentColor" rx="1" />
            </svg>
          </div>
        </div>

        {/* Setup Heading & Subheading */}
        <div className="text-center space-y-2 mb-6">
          <h1 className="text-[24px] sm:text-[28px] font-bold tracking-tight text-slate-900 dark:text-foreground leading-tight">
            Set up your institution on TrackMyClass
          </h1>
          <p className="text-[14px] font-medium text-slate-500 dark:text-muted-foreground leading-relaxed px-2">
            Join thousands of educational institutions using AI-powered attendance and classroom management.
          </p>
        </div>

        {/* Institution Setup Card */}
        <div className="w-full bg-white dark:bg-card border border-slate-200/80 dark:border-border/40 rounded-[24px] shadow-sm p-6 sm:p-8 space-y-5">
          
          {/* Error Banner */}
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

          <form onSubmit={handleSubmit} className="space-y-4">
            
            {/* Institution Name */}
            <div className="space-y-1.5">
              <label htmlFor="instName" className="block text-[13px] font-semibold text-slate-700 dark:text-slate-300">
                Institution name
              </label>
              <div className="relative">
                <Landmark className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input
                  id="instName"
                  type="text"
                  placeholder="Enter institution name"
                  value={name}
                  onChange={(e) => { setName(e.target.value); if (errorMsg) setErrorMsg(null); }}
                  className="h-[46px] pl-10 rounded-[12px] bg-white dark:bg-secondary/30 border-slate-200 dark:border-border/60 focus:border-indigo-500 text-[15px] shadow-none transition-all placeholder:text-slate-400"
                  required
                />
              </div>
            </div>

            {/* Institution Type */}
            <div className="space-y-1.5">
              <label htmlFor="instType" className="block text-[13px] font-semibold text-slate-700 dark:text-slate-300">
                Institution type
              </label>
              <div className="relative">
                <LayoutGrid className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <select
                  id="instType"
                  value={instType}
                  onChange={(e) => setInstType(e.target.value)}
                  className="w-full h-[46px] pl-10 pr-4 rounded-[12px] bg-white dark:bg-secondary/30 border border-slate-200 dark:border-border/60 focus:border-indigo-500 text-[15px] text-slate-900 dark:text-foreground shadow-none transition-all appearance-none cursor-pointer"
                >
                  <option value="" disabled>Select institution type</option>
                  <option value="University">University</option>
                  <option value="College">College</option>
                  <option value="School">School</option>
                  <option value="Training Institute">Training Institute</option>
                </select>
                <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                  ▼
                </div>
              </div>
            </div>

            {/* Institution Email */}
            <div className="space-y-1.5">
              <label htmlFor="instEmail" className="block text-[13px] font-semibold text-slate-700 dark:text-slate-300">
                Institution email
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input
                  id="instEmail"
                  type="email"
                  placeholder="Enter official email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="h-[46px] pl-10 rounded-[12px] bg-white dark:bg-secondary/30 border-slate-200 dark:border-border/60 focus:border-indigo-500 text-[15px] shadow-none transition-all placeholder:text-slate-400"
                />
              </div>
            </div>

            {/* Institution Code (Optional) */}
            <div className="space-y-1.5">
              <label htmlFor="instCode" className="block text-[13px] font-semibold text-slate-700 dark:text-slate-300">
                Institution code (optional)
              </label>
              <div className="relative">
                <Hash className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <Input
                  id="instCode"
                  type="text"
                  placeholder="Enter institution code"
                  value={code}
                  onChange={(e) => setCode(e.target.value.toUpperCase())}
                  className="h-[46px] pl-10 rounded-[12px] bg-white dark:bg-secondary/30 border-slate-200 dark:border-border/60 focus:border-indigo-500 text-[15px] uppercase font-mono shadow-none transition-all placeholder:text-slate-400"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !name.trim()}
              className="w-full h-[48px] mt-3 rounded-[12px] bg-[#1D70F5] hover:bg-blue-600 text-white font-semibold text-[15px] shadow-sm hover:shadow active:scale-[0.99] transition-all flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Creating Institution...</span>
                </>
              ) : (
                <span>Create Institution</span>
              )}
            </button>

            {/* Terms Disclaimer */}
            <p className="text-[12px] font-medium text-slate-500 dark:text-muted-foreground text-center leading-snug pt-1">
              By creating an institution, you agree to our{" "}
              <button 
                type="button" 
                onClick={() => toast.info("Terms of Service: By accessing TrackMyClass, you agree to standard academic data protection compliance.")} 
                className="font-semibold text-indigo-600 hover:underline dark:text-indigo-400"
              >
                Terms of Service
              </button>{" "}
              and{" "}
              <button 
                type="button" 
                onClick={() => toast.info("Privacy Policy: Biometric attendance data is encrypted and isolated per institution.")} 
                className="font-semibold text-indigo-600 hover:underline dark:text-indigo-400"
              >
                Privacy Policy
              </button>.
            </p>

          </form>

        </div>

        {/* Need Help Section */}
        <div className="w-full mt-8 text-center space-y-4">
          
          <div className="relative flex items-center justify-center">
            <div className="border-t border-slate-200 dark:border-border/40 w-full absolute"></div>
            <span className="bg-[#f8f9fc] dark:bg-background px-3 text-[13px] font-semibold text-slate-500 dark:text-muted-foreground relative z-10">
              Need help?
            </span>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <button
              onClick={() => handleSupportClick("Help Center")}
              className="bg-white dark:bg-card border border-slate-200/80 dark:border-border/40 hover:border-indigo-300 rounded-[16px] p-3 flex flex-col items-center justify-center gap-1.5 transition-all shadow-2xs group"
            >
              <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-secondary flex items-center justify-center group-hover:scale-110 transition-transform">
                <HelpCircle className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              </div>
              <span className="text-[12px] font-semibold text-slate-700 dark:text-slate-300">Help Center</span>
            </button>

            <button
              onClick={() => handleSupportClick("Contact Us")}
              className="bg-white dark:bg-card border border-slate-200/80 dark:border-border/40 hover:border-indigo-300 rounded-[16px] p-3 flex flex-col items-center justify-center gap-1.5 transition-all shadow-2xs group"
            >
              <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-secondary flex items-center justify-center group-hover:scale-110 transition-transform">
                <PhoneCall className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              </div>
              <span className="text-[12px] font-semibold text-slate-700 dark:text-slate-300">Contact Us</span>
            </button>

            <button
              onClick={() => handleSupportClick("Live Chat")}
              className="bg-white dark:bg-card border border-slate-200/80 dark:border-border/40 hover:border-indigo-300 rounded-[16px] p-3 flex flex-col items-center justify-center gap-1.5 transition-all shadow-2xs group"
            >
              <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-secondary flex items-center justify-center group-hover:scale-110 transition-transform">
                <MessageSquare className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              </div>
              <span className="text-[12px] font-semibold text-slate-700 dark:text-slate-300">Live Chat</span>
            </button>
          </div>

        </div>

      </main>

      {/* Decorative Wave & Footer */}
      <footer className="w-full text-center mt-6 pt-4 flex flex-col items-center justify-center gap-2">
        <p className="text-[13px] font-semibold text-indigo-900/70 dark:text-indigo-300/70 flex items-center justify-center gap-1.5">
          Building smarter classrooms together
        </p>
      </footer>

    </div>
  )
}
