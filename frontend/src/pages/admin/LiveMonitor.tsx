import { useEffect, useRef, useState, useCallback } from "react"
import { Camera, StopCircle, RefreshCcw, Wifi, WifiOff } from "lucide-react"
import { toast } from "sonner"
import { useParams } from "react-router-dom"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsHostname = window.location.hostname;
const WS_BASE = wsHostname === 'localhost' ? 'ws://localhost:8000' : `${wsProtocol}//${wsHostname}`;
const MAX_RECONNECT_ATTEMPTS = 5
const FRAME_INTERVAL_MS = 250  // target ~4 FPS; server-side rate limit is 5/s
const JPEG_QUALITY = 0.7

interface DetectedFace {
  student_id: string
  name: string
  confidence: number
  status: "marked" | "marked" | "tracking" | "already_marked" | "cooldown" | "unknown"
  box: [number, number, number, number]
}

export default function LiveMonitor() {
  const { sessionId, collegeCode } = useParams<{ sessionId: string; collegeCode: string }>()
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const intervalRef = useRef<number | null>(null)
  const reconnectRef = useRef(0)

  const [stream, setStream] = useState<MediaStream | null>(null)
  const [isTracking, setIsTracking] = useState(false)
  const [wsState, setWsState] = useState<"disconnected" | "connecting" | "connected">("disconnected")
  const [facingMode, setFacingMode] = useState<"user" | "environment">("user")
  const [detectedCount, setDetectedCount] = useState(0)
  const [recognizedCount, setRecognizedCount] = useState(0)
  const [subject, setSubject] = useState("")
  const [processingMs, setProcessingMs] = useState(0)

  // ── Camera ──────────────────────────────────────────────────────────────────
  const startCamera = useCallback(async () => {
    try {
      if (stream) stream.getTracks().forEach(t => t.stop())
      const s = await navigator.mediaDevices.getUserMedia({
        video: { facingMode, width: { ideal: 640 }, height: { ideal: 480 } },
      })
      setStream(s)
      if (videoRef.current) videoRef.current.srcObject = s
    } catch {
      toast.error("Could not access camera.")
    }
  }, [facingMode])

  const stopCamera = useCallback(() => {
    stream?.getTracks().forEach(t => t.stop())
    setStream(null)
    stopTracking()
  }, [stream])

  useEffect(() => {
    startCamera()
    return () => { stream?.getTracks().forEach(t => t.stop()) }
  }, [facingMode])

  // ── WebSocket ────────────────────────────────────────────────────────────────
  const connectWS = useCallback(() => {
    const token = localStorage.getItem("token")
    if (!token || !sessionId) {
      toast.error("Cannot connect: missing token or session ID")
      return
    }

    setWsState("connecting")
    const url = `${WS_BASE}/api/v1/ws/monitor/${sessionId}?token=${token}`
    const ws = new WebSocket(url)
    ws.binaryType = "arraybuffer"
    wsRef.current = ws

    ws.onopen = () => {
      setWsState("connected")
      reconnectRef.current = 0
      toast.success("Live tracking connected")
    }

    ws.onmessage = (evt) => {
      if (typeof evt.data !== "string") return
      const msg = JSON.parse(evt.data)

      if (msg.type === "recognition.result") {
        setDetectedCount(msg.faces_detected ?? 0)
        setRecognizedCount(msg.faces_recognized ?? 0)
        setProcessingMs(msg.processing_ms ?? 0)
        if (msg.session_subject) setSubject(msg.session_subject)
        if (!msg.session_active) {
          toast.error("Session ended — stopping tracking.")
          stopTracking()
          return
        }
        drawBoundingBoxes(msg.results ?? [])

        // Toast for newly marked faces
        for (const face of msg.results ?? []) {
          if (face.status === "marked") {
            toast.success(`✅ ${face.name} marked present`, { duration: 2500 })
          }
        }
      } else if (msg.type === "worker.unavailable" || msg.type === "inference.error") {
        toast.error(msg.message ?? "Inference error")
      } else if (msg.type === "error") {
        toast.error(msg.message ?? "Connection error")
        ws.close()
      }
    }

    ws.onerror = () => {
      setWsState("disconnected")
    }

    ws.onclose = () => {
      setWsState("disconnected")
      stopFrameInterval()
      if (reconnectRef.current < MAX_RECONNECT_ATTEMPTS && isTracking) {
        const delay = Math.min(1000 * 2 ** reconnectRef.current, 15000)
        reconnectRef.current++
        toast.warning(`Reconnecting… attempt ${reconnectRef.current}`)
        setTimeout(connectWS, delay)
      } else if (reconnectRef.current >= MAX_RECONNECT_ATTEMPTS) {
        toast.error("Could not reconnect. Please stop and restart tracking.")
        setIsTracking(false)
      }
    }
  }, [sessionId, isTracking])

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

  const stopFrameInterval = () => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }

  const startTracking = () => {
    if (!stream) { toast.error("Camera not started"); return }
    setIsTracking(true)
    reconnectRef.current = 0
    connectWS()
    intervalRef.current = window.setInterval(sendFrame, FRAME_INTERVAL_MS)
  }

  const stopTracking = () => {
    setIsTracking(false)
    stopFrameInterval()
    wsRef.current?.close(1000, "User stopped")
    wsRef.current = null
    setWsState("disconnected")
    clearCanvas()
  }

  // ── Bounding boxes ────────────────────────────────────────────────────────────
  const clearCanvas = () => {
    const ctx = canvasRef.current?.getContext("2d")
    if (ctx && canvasRef.current) ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)
  }

  const drawBoundingBoxes = (faces: DetectedFace[]) => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    const vidW = videoRef.current?.videoWidth || 640
    const vidH = videoRef.current?.videoHeight || 480
    const scaleX = canvas.width / vidW
    const scaleY = canvas.height / vidH

    faces.forEach((face) => {
      const [x1, y1, x2, y2] = face.box
      let rx = facingMode === "user" ? canvas.width - x2 * scaleX : x1 * scaleX
      const ry = y1 * scaleY
      const rw = (x2 - x1) * scaleX
      const rh = (y2 - y1) * scaleY

      const colorMap: Record<string, string> = {
        marked: "#22c55e",
        already_marked: "#22c55e",
        tracking: "#eab308",
        cooldown: "#3b82f6",
        unknown: "#ef4444",
      }
      const color = colorMap[face.status] ?? "#ef4444"

      ctx.strokeStyle = color
      ctx.lineWidth = 3
      ctx.strokeRect(rx, ry, rw, rh)
      ctx.fillStyle = color
      ctx.fillRect(rx, ry - 24, rw, 24)
      ctx.fillStyle = "#fff"
      ctx.font = "bold 13px Inter, sans-serif"
      ctx.fillText(face.name, rx + 4, ry - 7)
    })
  }

  // ── Cleanup ──────────────────────────────────────────────────────────────────
  useEffect(() => () => { stopTracking(); stopCamera() }, [])

  return (
    <div className="space-y-4 max-w-5xl mx-auto h-[calc(100vh-6rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Live Monitor</h1>
          {subject && <p className="text-sm text-muted-foreground">Session: {subject}</p>}
        </div>
        <div className="flex items-center gap-2">
          {wsState === "connected"
            ? <Badge className="bg-green-500 flex gap-1"><Wifi className="h-3 w-3" /> Live</Badge>
            : wsState === "connecting"
            ? <Badge variant="outline" className="flex gap-1"><Wifi className="h-3 w-3 animate-pulse" /> Connecting</Badge>
            : <Badge variant="outline" className="flex gap-1"><WifiOff className="h-3 w-3" /> Offline</Badge>
          }
          <Badge variant="outline">Detected: {detectedCount}</Badge>
          <Badge className="bg-green-500">Recognized: {recognizedCount}</Badge>
          {processingMs > 0 && <Badge variant="outline">{processingMs}ms</Badge>}
        </div>
      </div>

      {/* Camera + Canvas */}
      <Card className="flex-1 overflow-hidden flex flex-col border-0 shadow-lg relative bg-black">
        <CardContent className="p-0 flex-1 relative flex items-center justify-center">
          {stream ? (
            <video
              ref={videoRef}
              autoPlay playsInline muted
              className="absolute inset-0 w-full h-full object-contain pointer-events-none"
              style={{ transform: facingMode === "user" ? "scaleX(-1)" : "none" }}
            />
          ) : (
            <div className="text-zinc-500 flex flex-col items-center">
              <Camera className="h-12 w-12 mb-2 opacity-50" />
              <span>Camera Offline</span>
            </div>
          )}

          <canvas
            ref={canvasRef}
            className="absolute inset-0 w-full h-full object-contain pointer-events-none z-10"
          />

          {/* Controls */}
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-4 bg-background/80 backdrop-blur-md px-6 py-3 rounded-full shadow-xl border border-border/50 z-20">
            <Button variant="outline" size="icon" className="rounded-full" onClick={() => setFacingMode(f => f === "user" ? "environment" : "user")}>
              <RefreshCcw className="h-5 w-5" />
            </Button>

            {!isTracking ? (
              <Button
                className="rounded-full px-8 bg-primary hover:bg-primary/90 shadow-lg"
                onClick={startTracking}
                disabled={!stream}
              >
                <Camera className="mr-2 h-5 w-5" /> Start Tracking
              </Button>
            ) : (
              <Button
                variant="destructive"
                className="rounded-full px-8 animate-pulse shadow-lg"
                onClick={stopTracking}
              >
                <StopCircle className="mr-2 h-5 w-5" /> Stop Tracking
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
