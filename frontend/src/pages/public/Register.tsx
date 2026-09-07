import { useState, useRef, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Camera, CheckCircle2, Loader2, RefreshCcw, VideoOff } from "lucide-react"
import { toast } from "sonner"
import { useNavigate, useParams } from "react-router-dom"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { api } from "@/lib/api"

const registerSchema = z.object({
  name: z.string().min(2, "Name is required"),
  roll_number: z.string().min(2, "Roll number is required"),
  gender: z.string().min(1, "Gender is required"),
  password: z.string().min(4, "Password must be at least 4 characters"),
  consent: z.boolean().refine(val => val === true, {
    message: "You must consent to biometric data collection to register."
  }),
})

type RegisterFormValues = z.infer<typeof registerSchema>

export default function Register() {
  const navigate = useNavigate()
  const { collegeCode } = useParams<{ collegeCode: string }>()
  const videoRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [frames, setFrames] = useState<string[]>([])
  const [isCapturing, setIsCapturing] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [facingMode, setFacingMode] = useState<"user" | "environment">("user")
  
  // Timer states
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null)
  const [command, setCommand] = useState("")

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  })

  const startCamera = async () => {
    try {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop())
      }
      const newStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode, width: { ideal: 640 }, height: { ideal: 480 } },
      })
      streamRef.current = newStream
      setStream(newStream)
      if (videoRef.current) {
        videoRef.current.srcObject = newStream
      }
    } catch (err) {
      toast.error("Could not access camera. Please allow permissions.")
      console.error(err)
    }
  }

  useEffect(() => {
    startCamera()
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop())
        streamRef.current = null
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [facingMode])

  const flipCamera = () => {
    setFacingMode((prev) => (prev === "user" ? "environment" : "user"))
  }

  const startCaptureProcess = async () => {
    if (!videoRef.current) return
    setIsCapturing(true)
    setFrames([])
    setTimeRemaining(30)
    setCommand("Look Straight 😐")
    
    let currentFrames: string[] = []
    let timeLeft = 30

    const canvas = document.createElement("canvas")
    const context = canvas.getContext("2d")

    const timerInterval = setInterval(() => {
      timeLeft -= 1
      setTimeRemaining(timeLeft)

      if (timeLeft > 25) setCommand("Look Straight 😐")
      else if (timeLeft > 20) setCommand("Look Left 👈")
      else if (timeLeft > 15) setCommand("Look Right 👉")
      else if (timeLeft > 10) setCommand("Look Up 🆙")
      else if (timeLeft > 5) setCommand("Look Down ⬇️")
      else setCommand("Smile! 😊")

      if (timeLeft <= 0) {
        clearInterval(timerInterval)
        setIsCapturing(false)
        setTimeRemaining(null)
        setCommand("Done! ✅")
        setFrames(currentFrames)
        toast.success(`Face data captured successfully.`)
      }
    }, 1000)

    const captureInterval = setInterval(() => {
      if (timeLeft <= 0) {
        clearInterval(captureInterval)
        return
      }
      if (context && videoRef.current) {
        canvas.width = videoRef.current.videoWidth
        canvas.height = videoRef.current.videoHeight
        context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height)
        const dataUrl = canvas.toDataURL("image/jpeg", 0.7) // Slightly lower quality for smaller payload
        const base64 = dataUrl.split(",")[1]
        currentFrames.push(base64)
      }
    }, 1000)
  }

  const onSubmit = async (data: RegisterFormValues) => {
    if (frames.length === 0) {
      toast.error("Please capture your face samples first.")
      return
    }

    setIsSubmitting(true)
    try {
      await api.post("/registration/register", {
        ...data,
        frames,
        collegeCode,
      })
      toast.success("Registration successful! You can now mark attendance.")
      navigate(`/${collegeCode}/login`)
    } catch (err: any) {
      let errorMsg = "Registration failed. Try again.";
      const detail = err.response?.data?.detail;
      if (typeof detail === "string") {
        errorMsg = detail;
      } else if (Array.isArray(detail)) {
        errorMsg = detail[0]?.msg || JSON.stringify(detail);
      }
      toast.error(errorMsg)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-xl">
      <Card className="border-0 shadow-lg md:border md:shadow-sm">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Student Registration</CardTitle>
          <CardDescription>Enroll your face data for automatic attendance.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            
            {/* Camera Section */}
            <div className="space-y-3">
              <Label className="text-base">Face Data Capture</Label>
              <div className="relative aspect-[4/3] bg-muted rounded-xl overflow-hidden border border-border flex items-center justify-center">
                {stream ? (
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover"
                    style={{ transform: facingMode === "user" ? "scaleX(-1)" : "none" }}
                  />
                ) : (
                  <div className="flex flex-col items-center text-muted-foreground">
                    <VideoOff className="h-8 w-8 mb-2" />
                    <span>Camera starting...</span>
                  </div>
                )}
                
                {/* Timer and Command Overlay */}
                {timeRemaining !== null && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/40 text-white p-4">
                    <div className="text-6xl font-bold mb-4">{timeRemaining}s</div>
                    <div className="text-3xl font-bold text-center bg-black/60 px-6 py-3 rounded-full border border-white/20 backdrop-blur-md">
                      {command}
                    </div>
                  </div>
                )}

                {/* Camera Overlay Controls */}
                <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-4 px-4">
                  <Button
                    type="button"
                    variant="secondary"
                    size="icon"
                    onClick={flipCamera}
                    disabled={isCapturing}
                    className="rounded-full shadow-md bg-background/80 backdrop-blur"
                  >
                    <RefreshCcw className="h-4 w-4" />
                  </Button>
                  
                  <Button
                    type="button"
                    onClick={startCaptureProcess}
                    disabled={isCapturing || !stream}
                    className="rounded-full shadow-md px-6 bg-primary text-primary-foreground font-semibold"
                  >
                    {isCapturing ? (
                      <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Recording...</>
                    ) : frames.length > 0 ? (
                      <><RefreshCcw className="mr-2 h-4 w-4" /> Retake</>
                    ) : (
                      <><Camera className="mr-2 h-4 w-4" /> Start Capture</>
                    )}
                  </Button>
                </div>
              </div>
              
              {/* Progress indication */}
              {isCapturing && (
                <div className="flex flex-col gap-2 justify-center mt-2">
                  <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary transition-all duration-1000 ease-linear"
                      style={{ width: `${((30 - (timeRemaining || 0)) / 30) * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-primary text-center font-medium animate-pulse">
                    Keep your face clearly visible...
                  </p>
                </div>
              )}
              {!isCapturing && frames.length > 0 && (
                <p className="text-xs text-green-600 text-center font-bold">
                  ✅ Face data captured successfully ({frames.length} frames).
                </p>
              )}
              {!isCapturing && frames.length === 0 && (
                <p className="text-xs text-muted-foreground text-center">
                  Look straight into the camera and ensure good lighting.
                </p>
              )}
            </div>

            <div className="grid gap-4 pt-4 border-t">
              <div className="grid gap-2">
                <Label htmlFor="name">Full Name</Label>
                <Input id="name" {...register("name")} placeholder="John Doe" />
                {errors.name && <span className="text-xs text-destructive">{errors.name.message}</span>}
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="roll_number">Roll Number</Label>
                  <Input id="roll_number" {...register("roll_number")} placeholder="CS2101" />
                  {errors.roll_number && <span className="text-xs text-destructive">{errors.roll_number.message}</span>}
                </div>
                
                <div className="grid gap-2">
                  <Label htmlFor="gender">Gender</Label>
                  <select 
                    id="gender" 
                    {...register("gender")}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  >
                    <option value="">Select...</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                  {errors.gender && <span className="text-xs text-destructive">{errors.gender.message}</span>}
                </div>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="password">PIN / Password</Label>
                <Input id="password" type="password" {...register("password")} placeholder="••••" />
                {errors.password && <span className="text-xs text-destructive">{errors.password.message}</span>}
              </div>

              <div className="flex flex-col gap-2">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="consent"
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                    {...register("consent")}
                  />
                  <Label htmlFor="consent" className="text-sm text-muted-foreground leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                    I consent to the collection and use of my biometric facial data for attendance tracking.
                  </Label>
                </div>
                {errors.consent && <span className="text-xs text-destructive">{errors.consent.message}</span>}
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full h-12 text-lg font-bold" 
              disabled={isSubmitting || frames.length === 0}
            >
              {isSubmitting ? (
                <><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Registering...</>
              ) : (
                "Complete Registration"
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
