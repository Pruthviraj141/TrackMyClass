import { useState, useEffect } from "react"
import { Bell, Sun, Moon, Shield, ChevronRight } from "lucide-react"

export function PreferencesSection() {
  const [theme, setTheme] = useState<"light" | "dark">("light")

  // Initialize theme based on document class
  useEffect(() => {
    if (document.documentElement.classList.contains("dark")) {
      setTheme("dark")
    } else {
      setTheme("light")
    }
  }, [])

  const toggleTheme = () => {
    if (theme === "light") {
      document.documentElement.classList.add("dark")
      setTheme("dark")
      localStorage.setItem("theme", "dark")
    } else {
      document.documentElement.classList.remove("dark")
      setTheme("light")
      localStorage.setItem("theme", "light")
    }
  }

  return (
    <div className="px-5 py-2 mt-2">
      <h2 className="text-[16px] font-semibold text-foreground mb-2 px-1">Preferences</h2>
      
      <div className="bg-card rounded-[20px] shadow-[0_4px_20px_rgb(0,0,0,0.03)] dark:shadow-[0_4px_20px_rgb(0,0,0,0.15)] border-none overflow-hidden">
        
        <button className="w-full flex items-center justify-between px-5 py-3.5 border-b border-border/40 hover:bg-muted/30 transition-colors focus:outline-none focus:bg-muted/30">
          <div className="flex items-center gap-3">
            <Bell className="w-4 h-4 text-foreground/60" />
            <span className="text-[14px] text-foreground font-medium">Notifications</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[13px] text-foreground/50">Enabled</span>
            <ChevronRight className="w-4 h-4 text-foreground/30" />
          </div>
        </button>
        
        <button 
          onClick={toggleTheme}
          className="w-full flex items-center justify-between px-5 py-3.5 border-b border-border/40 hover:bg-muted/30 transition-colors focus:outline-none focus:bg-muted/30"
        >
          <div className="flex items-center gap-3">
            {theme === "light" ? <Sun className="w-4 h-4 text-foreground/60" /> : <Moon className="w-4 h-4 text-foreground/60" />}
            <span className="text-[14px] text-foreground font-medium">Appearance</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[13px] text-foreground/50 capitalize">{theme}</span>
            <ChevronRight className="w-4 h-4 text-foreground/30" />
          </div>
        </button>

        <button className="w-full flex items-center justify-between px-5 py-3.5 hover:bg-muted/30 transition-colors focus:outline-none focus:bg-muted/30">
          <div className="flex items-center gap-3">
            <Shield className="w-4 h-4 text-foreground/60" />
            <span className="text-[14px] text-foreground font-medium">Privacy & Security</span>
          </div>
          <ChevronRight className="w-4 h-4 text-foreground/30" />
        </button>

      </div>
    </div>
  )
}
