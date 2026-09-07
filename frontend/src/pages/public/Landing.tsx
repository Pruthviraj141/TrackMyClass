import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Building2, ArrowRight, Loader2 } from "lucide-react"
import { api } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useStore } from "@/store" // We will create this Zustand store

export default function Landing() {
  const [code, setCode] = useState("")
  const [error, setError] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const { setInstitution } = useStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!code.trim()) return

    setIsLoading(true)
    setError("")

    try {
      const res = await api.post("/institutions/verify-code", { code: code.trim() })
      if (res.data.valid) {
        setInstitution(res.data.code, res.data.institutionName)
        navigate(`/${res.data.code.toLowerCase()}`)
      } else {
        setError("Invalid college code. Please check and try again.")
      }
    } catch (err) {
      setError("Unable to verify code at this time.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8 text-center animate-in fade-in zoom-in-95 duration-500 ease-out">
        <div className="space-y-4">
          <div className="mx-auto w-12 h-12 bg-primary/10 flex items-center justify-center rounded-xl animate-bounce-slow">
            <Building2 className="w-6 h-6 text-primary" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight">TrackMyClass</h1>
          <p className="text-muted-foreground">
            Enter your institution's college code to access the attendance system.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Input
              type="text"
              placeholder="e.g. DEMO2026"
              value={code}
              onChange={(e) => { setCode(e.target.value.toUpperCase()); setError("") }}
              className="text-center text-lg h-12 uppercase tracking-widest font-mono"
              autoComplete="off"
              autoFocus
            />
            {error && <p className="text-sm text-destructive font-medium">{error}</p>}
          </div>
          
          <Button type="submit" className="w-full h-12 text-base font-semibold" disabled={isLoading || !code.trim()}>
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                Continue <ArrowRight className="w-4 h-4 ml-2" />
              </>
            )}
          </Button>
        </form>

        <p className="text-xs text-muted-foreground pt-8">
          If you are a student, your instructor or department will provide this code.
        </p>
        <p className="text-xs text-muted-foreground pt-2">
          New institution?{" "}
          <button onClick={() => navigate("/onboarding")} className="text-primary font-semibold hover:underline">
            Set up your institution
          </button>
        </p>
      </div>
    </div>
  )
}
