import { useEffect, useRef, useState, useCallback } from "react"
import { toast } from "sonner"
import { useParams, useNavigate } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"
import { api } from "@/lib/api"

import { LiveHeader } from "@/components/live/LiveHeader"
import { AttendanceMetrics } from "@/components/live/AttendanceMetrics"
import { CameraFeed } from "@/components/live/CameraFeed"
import { SessionControls } from "@/components/live/SessionControls"
import { RecentEvents, type RecognitionEvent } from "@/components/live/RecentEvents"
import { AttendanceReviewScreen } from "@/components/live/AttendanceReviewScreen"

const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsHostname = window.location.hostname;
const WS_BASE = wsHostname === 'localhost' ? 'ws://localhost:8000' : `${wsProtocol}//${wsHostname}`;
const MAX_RECONNECT_ATTEMPTS = 5
const FRAME_INTERVAL_MS = 250
const JPEG_QUALITY = 0.7

interface DetectedFace {
  student_id: string
  name: string
  confidence: number
  status: "marked" | "already_marked" | "tracking" | "cooldown" | "unknown"
  box: [number, number, number, number]
  roll_number?: string
}

export default function TeacherLiveClassroom() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const intervalRef = useRef<number | null>(null)
  const reconnectRef = useRef(0)

  const [stream, setStream] = useState<MediaStream | null>(null)
  const [facingMode, setFacingMode] = useState<"user" | "environment">("user")
  const [wsState, setWsState] = useState<"disconnected" | "connecting" | "connected">("disconnected")
  const [isEnding, setIsEnding] = useState(false)
  const [isReviewing, setIsReviewing] = useState(false)
  const [sessionStartTime, setSessionStartTime] = useState(Date.now())

  // Config State
  const [isConfiguring, setIsConfiguring] = useState(true)
  const [subjectInput, setSubjectInput] = useState("")
  const [isStartingSession, setIsStartingSession] = useState(false)
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null)

  // Session Data & Metrics
  const [subject, setSubject] = useState("Loading Course...")
  // Using some mock values if empty initially, but replaced aggressively by WS 
  const [presentCount, setPresentCount] = useState(0)
  const [unknownCount, setUnknownCount] = useState(0)
  const [totalCount, setTotalCount] = useState(0)

  // Telemetry
  const [latencyMs, setLatencyMs] = useState(0)
  const [queueDepth, setQueueDepth] = useState(0)
  // Simplified FPS calc
  const [fps] = useState(Math.round(1000 / FRAME_INTERVAL_MS)) 

  const [recentEvents, setRecentEvents] = useState<RecognitionEvent[]>([])

  const streamRef = useRef<MediaStream | null>(null)

  // ── Camera ──────────────────────────────────────────────────────────────────
  const startCamera = useCallback(async () => {
    try {
      if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop())
      const s = await navigator.mediaDevices.getUserMedia({
        video: { facingMode, width: { ideal: 1280 }, height: { ideal: 720 } },
      })
      streamRef.current = s
      setStream(s)
      if (videoRef.current) videoRef.current.srcObject = s
    } catch {
      toast.error("Could not access camera.")
    }
  }, [facingMode])

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop())
      streamRef.current = null
    }
    setStream(null)
  }, [])

  useEffect(() => {
    if (!isConfiguring) {
      startCamera()
    }
    return () => { stopCamera() }
  }, [facingMode, isConfiguring, startCamera, stopCamera])

  // ── Frame sending ────────────────────────────────────────────────────────────
  const sendFrame = useCallback(() => {
    if (!videoRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return

    const tmp = document.createElement("canvas")
    tmp.width = videoRef.current.videoWidth || 640
    tmp.height = videoRef.current.videoHeight || 480
    const ctx = tmp.getContext("2d")
    if (!ctx) return
    ctx.drawImage(videoRef.current, 0, 0, tmp.width, tmp.height)

    tmp.toBlob(
      (blob) => {
        if (blob && wsRef.current?.readyState === WebSocket.OPEN) {
          blob.arrayBuffer().then(buf => wsRef.current?.send(buf))
        }
      },
      "image/jpeg",
      JPEG_QUALITY
    )
  }, [])

  // ── Event Logs Management ────────────────────────────────────────────────────
  const addEvent = useCallback((face: DetectedFace) => {
    const isUnknown = face.status === "unknown"
    const st: "verified" | "unknown" = isUnknown ? "unknown" : "verified"
    const name = isUnknown ? "Unknown face" : face.name

    setRecentEvents(prev => {
      // Avoid duplicate logs for same name within short window
      if (prev.length > 0 && prev[0].name === name) return prev
      
      const newEvent: RecognitionEvent = {
        id: Math.random().toString(),
        name,
        status: st,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        rollNumber: face.roll_number
      }
      return [newEvent, ...prev].slice(0, 10) // Keep last 10
    })
  }, [])

  // ── WebSocket ────────────────────────────────────────────────────────────────
  const connectWS = useCallback(() => {
    const token = localStorage.getItem("token")
    const currentSessionId = sessionId || activeSessionId
    if (!token || !currentSessionId) return

    setWsState("connecting")
    const url = `${WS_BASE}/api/v1/ws/monitor/${currentSessionId}?token=${token}`
    const ws = new WebSocket(url)
    ws.binaryType = "arraybuffer"
    wsRef.current = ws

    ws.onopen = () => {
      setWsState("connected")
      reconnectRef.current = 0
      toast.success("Live monitoring started")
      if (intervalRef.current !== null) clearInterval(intervalRef.current)
      intervalRef.current = window.setInterval(sendFrame, FRAME_INTERVAL_MS)
    }

    ws.onmessage = (evt) => {
      if (typeof evt.data !== "string") return
      const msg = JSON.parse(evt.data)

      if (msg.type === "recognition.result") {
        setPresentCount(msg.faces_recognized ?? presentCount)
        
        let localUnknown = 0
        if (msg.results) {
           localUnknown = msg.results.filter((f: any) => f.status === "unknown").length
           setUnknownCount(localUnknown)
        }

        setLatencyMs(msg.processing_ms ?? 0)
        setQueueDepth(msg.queue_size ?? 0) // Assume backend passes this eventually
        
        if (msg.session_subject) setSubject(msg.session_subject)
        
        if (!msg.session_active) {
          handleEndSession()
          return
        }
        drawBoundingBoxes(msg.results ?? [])

        // Manage events
        for (const face of msg.results ?? []) {
          if (face.status === "marked" || face.status === "unknown") {
             addEvent(face)
          }
        }
      } else if (msg.type === "worker.unavailable" || msg.type === "inference.error") {
          setQueueDepth(prev => prev + 1)
      } else if (msg.type === "error") {
        ws.close()
      }
    }

    ws.onerror = () => setWsState("disconnected")
    ws.onclose = () => {
      setWsState("disconnected")
      if (intervalRef.current !== null) clearInterval(intervalRef.current)
      
      if (!isEnding && reconnectRef.current < MAX_RECONNECT_ATTEMPTS) {
        const delay = Math.min(1000 * 2 ** reconnectRef.current, 10000)
        reconnectRef.current++
        toast.warning(`Reconnecting... attempt ${reconnectRef.current}`)
        setTimeout(connectWS, delay)
      }
    }
  }, [sessionId, activeSessionId, sendFrame, isEnding, addEvent])

  useEffect(() => {
    if (!isConfiguring) {
      connectWS()
    }
    return () => {
      if (intervalRef.current !== null) clearInterval(intervalRef.current)
      wsRef.current?.close()
    }
  }, [connectWS, isConfiguring])

  // ── Bounding boxes ────────────────────────────────────────────────────────────
  const drawBoundingBoxes = (faces: DetectedFace[]) => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    const vidW = videoRef.current?.videoWidth || 1280
    const vidH = videoRef.current?.videoHeight || 720
    const scaleX = canvas.width / vidW
    const scaleY = canvas.height / vidH

    faces.forEach((face) => {
      const isUnknown = face.status === "unknown"
      
      const [x1, y1, x2, y2] = face.box
      let rx = facingMode === "user" ? canvas.width - x2 * scaleX : x1 * scaleX
      const ry = y1 * scaleY
      const rw = (x2 - x1) * scaleX
      const rh = (y2 - y1) * scaleY

      // Colors matching the screenshot exactly
      const boxColor = isUnknown ? "#f59e0b" : "#4f46e5" // Amber vs Indigo
      const badgeBg = isUnknown ? "#3b1e00" : "#1e1e2d"
      const textColor = isUnknown ? "#f59e0b" : "#ffffff"

      // 1. Draw viewfinder box corners
      const cornerSize = 16
      ctx.strokeStyle = boxColor
      ctx.lineWidth = 2
      ctx.beginPath()
      // Top Left
      ctx.moveTo(rx, ry + cornerSize); ctx.lineTo(rx, ry); ctx.lineTo(rx + cornerSize, ry)
      // Top Right
      ctx.moveTo(rx + rw - cornerSize, ry); ctx.lineTo(rx + rw, ry); ctx.lineTo(rx + rw, ry + cornerSize)
      // Bottom Right
      ctx.moveTo(rx + rw, ry + rh - cornerSize); ctx.lineTo(rx + rw, ry + rh); ctx.lineTo(rx + rw - cornerSize, ry + rh)
      // Bottom Left
      ctx.moveTo(rx, ry + rh - cornerSize); ctx.lineTo(rx, ry + rh); ctx.lineTo(rx + cornerSize, ry + rh)
      ctx.stroke()

      // 2. Draw Label Badge
      const labelText = isUnknown ? "Unknown" : `${face.name}`
      const subText = isUnknown ? "Not registered" : `Roll No. ${face.roll_number || "N/A"}`
      
      ctx.font = "bold 13px -apple-system, BlinkMacSystemFont, sans-serif"
      const nameWidth = ctx.measureText(labelText).width
      
      ctx.font = "11px -apple-system, BlinkMacSystemFont, sans-serif"
      const subWidth = ctx.measureText(subText).width
      
      const badgeW = Math.max(nameWidth, subWidth) + 30
      const badgeH = 38
      const badgeX = rx + (rw / 2) - (badgeW / 2) // Center horizontally
      const badgeY = ry - 44

      // Badge Bg (Pill)
      ctx.fillStyle = badgeBg
      ctx.beginPath()
      ctx.roundRect(badgeX, badgeY, badgeW, badgeH, 13)
      ctx.fill()
      ctx.lineWidth = 1
      ctx.strokeStyle = boxColor + "40" // slight border
      ctx.stroke()

      // Active Dot
      ctx.fillStyle = boxColor
      ctx.beginPath()
      ctx.arc(badgeX + 12, badgeY + badgeH / 2, 3, 0, Math.PI * 2)
      ctx.fill()

      // Name Text
      ctx.fillStyle = textColor
      ctx.font = "bold 13px -apple-system, BlinkMacSystemFont, sans-serif"
      ctx.fillText(labelText, badgeX + 22, badgeY + 16)

      // Sub text
      ctx.fillStyle = isUnknown ? "#f59e0b" : "#22c55e"
      ctx.font = "11px -apple-system, BlinkMacSystemFont, sans-serif"
      ctx.fillText(subText, badgeX + 22, badgeY + 30)
    })
  }

  // ── Session Controls ────────────────────────────────────────────────────────
  const handleEndSession = () => {
    if (isEnding) return
    setIsEnding(true)
    if (intervalRef.current !== null) clearInterval(intervalRef.current)
    wsRef.current?.close(1000, "Teacher paused session for review")
    stopCamera()
    setIsReviewing(true)
    setIsEnding(false)
  }

  const handleFinalizeSession = async () => {
    setIsEnding(true)
    try {
      await api.post("/attendance/session/end")
      // Invalidate attendance cache so the Attendance page shows the new subject immediately
      queryClient.invalidateQueries({ queryKey: ['teacher-attendance'] })
      toast.success("Attendance Finalized successfully.")
      navigate(-1) 
    } catch {
      toast.error("Failed to finalize session.")
      setIsEnding(false)
    }
  }

  if (isConfiguring) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-background flex items-center justify-center p-4">
        <div className="bg-white dark:bg-card max-w-sm w-full rounded-[24px] p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.15)] border border-border/40 animate-in fade-in zoom-in-95 duration-500 relative overflow-hidden">
          {/* Accent decoration */}
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-blue-400"></div>

          <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100 mb-2 mt-2">New Session</h2>
          <p className="text-slate-500 dark:text-slate-400 font-medium text-[15px] mb-8 leading-snug">
            Enter the subject or class name you are teaching today.
          </p>
          
          <input 
            type="text"
            className="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-3.5 mb-6 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all font-medium text-[16px] text-slate-900 dark:text-slate-100 placeholder:text-slate-400"
            placeholder="e.g., Computer Networks"
            value={subjectInput}
            onChange={(e) => setSubjectInput(e.target.value)}
            disabled={isStartingSession}
            autoFocus
            onKeyDown={(e) => {
              if (e.key === "Enter" && subjectInput.trim() && !isStartingSession) {
                // Submit logic triggered by enter key. (Wrapped loosely around the button's onClick)
              }
            }}
          />
          
          <button 
            disabled={!subjectInput.trim() || isStartingSession}
            onClick={async () => {
              try {
                setIsStartingSession(true)
                const res = await api.post("/attendance/session/start", { subject_name: subjectInput })
                setActiveSessionId(res.data.session.session_id)
                setSubject(subjectInput)
                setSessionStartTime(Date.now())
                setIsConfiguring(false)
              } catch (e: any) {
                toast.error(e.response?.data?.message || "Failed to start session")
                setIsStartingSession(false)
              }
            }}
            className="w-full bg-primary hover:bg-primary/95 text-primary-foreground font-semibold py-4 rounded-xl transition-all disabled:opacity-50 flex justify-center items-center shadow-lg shadow-primary/20"
          >
            {isStartingSession ? <span className="animate-pulse">Starting stream...</span> : "Launch Live Scanner"}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background relative flex justify-center overflow-hidden">
      <div className="w-full max-w-md bg-background min-h-screen shadow-2xl flex flex-col relative md:max-w-4xl md:flex-row md:items-stretch">
        
        {/* Mobile: Top to Bottom Stack. Desktop: Left/Right Split */}
        <div className="flex-1 flex flex-col w-full h-[100dvh]">
          
          <LiveHeader 
            courseName={subject} 
            sessionStatus={wsState === "connected" ? "LIVE" : "CONNECTING"}
            startTimeMs={sessionStartTime}
          />
          
          <div className="flex-1 overflow-y-auto w-full md:flex md:flex-row md:overflow-hidden pb-safe">
            
            {isReviewing ? (
              <AttendanceReviewScreen 
                 subject={subjectInput} 
                 presentCount={presentCount} 
                 totalCount={totalCount} 
                 onFinalize={handleFinalizeSession} 
                 isFinalizing={isEnding} 
              />
            ) : (
              <>
                {/* Left Column (Camera + Controls) */}
                <div className="w-full md:w-[65%] flex flex-col">
                  <div className="px-3 md:px-5">
                     <CameraFeed 
                       videoRef={videoRef}
                       canvasRef={canvasRef}
                       stream={stream}
                       facingMode={facingMode}
                       onToggleCamera={() => setFacingMode(f => f === "user" ? "environment" : "user")}
                       fps={fps}
                       latencyMs={latencyMs}
                       queueDepth={queueDepth}
                       wsState={wsState}
                     />
                  </div>

                  <div className="hidden md:flex flex-col mt-4">
                     <AttendanceMetrics present={presentCount} unknown={unknownCount} total={totalCount} />
                     <SessionControls onEndSession={handleEndSession} isEnding={isEnding} />
                  </div>
                </div>

                {/* Right Column (Metrics + Logs for Desktop, Stacked for Mobile) */}
                <div className="w-full md:w-[35%] flex flex-col md:border-l border-border/40 bg-card/10 h-full">
                  
                  <div className="md:hidden mt-2">
                     <AttendanceMetrics present={presentCount} unknown={unknownCount} total={totalCount} />
                     <SessionControls onEndSession={handleEndSession} isEnding={isEnding} />
                  </div>

                  <div className="h-[1px] w-full bg-border/40 my-2 md:hidden" />
                  
                  <RecentEvents events={recentEvents} isProcessing={wsState === "connected"} />
                </div>
              </>
            )}

          </div>

        </div>

      </div>
    </div>
  )
}
