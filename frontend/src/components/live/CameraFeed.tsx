import { Camera, RefreshCcw } from "lucide-react"
import { useEffect } from "react"

interface CameraFeedProps {
  videoRef: React.RefObject<HTMLVideoElement | null>
  canvasRef: React.RefObject<HTMLCanvasElement | null>
  stream: MediaStream | null
  facingMode: "user" | "environment"
  onToggleCamera: () => void
  fps: number
  latencyMs: number
  queueDepth: number
  wsState: "disconnected" | "connecting" | "connected"
}

export function CameraFeed({
  videoRef,
  canvasRef,
  stream,
  facingMode,
  onToggleCamera,
  fps,
  latencyMs,
  queueDepth,
  wsState,
}: CameraFeedProps) {
  
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.srcObject = stream
    }
  }, [stream, videoRef])

  return (
    <div className="relative w-full aspect-video bg-black overflow-hidden rounded-[12px] sm:rounded-none">
      {/* Video Feed */}
      <video
        ref={videoRef as any}
        autoPlay
        playsInline
        muted
        className={`absolute inset-0 w-full h-full object-cover pointer-events-none transition-opacity duration-300 ${stream ? "opacity-100" : "opacity-0"}`}
        style={{ transform: facingMode === "user" ? "scaleX(-1)" : "none" }}
      />
      {!stream && (
        <div className="absolute inset-0 flex flex-col items-center justify-center text-foreground/40 bg-card/10 z-[2]">
          <Camera className="w-10 h-10 mb-3 opacity-50" />
          <span className="text-sm font-medium">Camera Offline</span>
        </div>
      )}

      {/* Overlay Canvas for Bounding Boxes */}
      <canvas
        ref={canvasRef as any}
        className="absolute inset-0 w-full h-full object-cover pointer-events-none z-10"
      />

      {/* Overlay System Telemetry (Bottom Left) */}
      <div className="absolute bottom-3 left-3 flex flex-wrap items-center gap-1.5 z-20">
        
        {/* Connection Pill */}
        <div className="flex items-center gap-1.5 bg-black/60 backdrop-blur-md border border-white/10 px-2 py-1 rounded-md text-[10px] uppercase font-bold tracking-widest text-white shadow-lg">
          {wsState === "connected" ? (
             <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
          ) : wsState === "connecting" ? (
             <span className="w-1.5 h-1.5 rounded-full bg-yellow-400 animate-pulse" />
          ) : (
             <span className="w-1.5 h-1.5 rounded-full bg-destructive" />
          )}
          
          <span className="opacity-90">{wsState}</span>
        </div>

        {/* Telemetry metrics */}
        {wsState === "connected" && (
           <>
             <div className="flex items-center bg-black/60 backdrop-blur-md border border-white/10 px-2 py-1 rounded-md text-[10px] uppercase tracking-widest font-mono text-white/50 shadow-lg">
               {fps} FPS
             </div>
             <div className="flex items-center bg-black/60 backdrop-blur-md border border-white/10 px-2 py-1 rounded-md text-[10px] uppercase tracking-widest font-mono text-white/50 shadow-lg">
               {latencyMs} ms
             </div>
             <div className="flex items-center bg-black/60 backdrop-blur-md border border-white/10 px-2 py-1 rounded-md text-[10px] uppercase tracking-widest font-mono text-white/50 shadow-lg">
               Q {queueDepth}
             </div>
           </>
        )}
      </div>

      {/* Camera Swap (Bottom Right) */}
      <button 
        onClick={onToggleCamera}
        className="absolute bottom-3 right-3 z-20 w-8 h-8 rounded-full bg-black/50 backdrop-blur-md flex items-center justify-center text-white hover:bg-black/80 transition-colors border border-white/10"
      >
        <RefreshCcw className="w-3.5 h-3.5 opacity-80" />
      </button>

      {/* Top Gradient for header blend */}
      <div className="absolute top-0 left-0 w-full h-16 bg-gradient-to-b from-black/60 to-transparent pointer-events-none z-[5]" />
      
      {/* Bottom Gradient for metrics clarity */}
      <div className="absolute bottom-0 left-0 w-full h-20 bg-gradient-to-t from-black/80 to-transparent pointer-events-none z-[5]" />
    </div>
  )
}
