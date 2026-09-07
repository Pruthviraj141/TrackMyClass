import { create } from "zustand"
import { persist } from "zustand/middleware"

interface AppState {
  collegeCode: string | null
  institutionName: string | null
  setInstitution: (code: string, name: string) => void
  clearInstitution: () => void
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      collegeCode: null,
      institutionName: null,
      setInstitution: (code, name) => set({ collegeCode: code, institutionName: name }),
      clearInstitution: () => set({ collegeCode: null, institutionName: null }),
    }),
    {
      name: "tmc-institution-storage",
    }
  )
)
