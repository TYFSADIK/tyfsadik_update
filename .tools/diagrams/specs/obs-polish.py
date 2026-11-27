from svgdiagram import Bars, Flow, Sequence, Stack, Timeline

PAGE = "work/applications/obs-polish.html"

pipeline = (
    Flow("polish-pipeline", "One camera frame through the filter",
         "Every effect is a GPU pass, and a pass that is switched off costs nothing. A small copy of the frame goes to "
         "face analysis on its own thread (MediaPipe on Windows and Linux, Apple's Vision on macOS); the passes use "
         "its latest answer, so analysis never holds up a frame.", cols=4)
    .node("cam", "Camera frame", "from any OBS video source", at=(0, 0), color="grey")
    .node("sm", "Smooth, brighten, foundation", "skin inside the tracked face", at=(0, 1), color="blue")
    .node("sh", "Makeup + shape", "lips, blush, eyes, brows; jaw, chin, nose", at=(0, 2), color="blue")
    .node("bg", "Background", "blur, colour or image", at=(0, 3), color="purple")
    .node("small", "384 px copy", "read back one frame late", at=(1, 0), color="grey")
    .node("vis", "Face analysis", "MediaPipe or Vision: landmarks, eyes, brows, iris, person", at=(1, 1), color="yellow")
    .node("gr", "Soft light, look, tone", "glow, 3D LUT, vignette, grain", at=(1, 3), color="green")
    .node("st", "Sticker", "follows the face and its tilt", at=(2, 3), color="orange")
    .node("out", "OBS output", "stream, recording, virtual camera", at=(2, 2), color="cyan")
    .edge("cam", "sm").edge("sm", "sh").edge("sh", "bg").edge("bg", "gr", exit="b", enter="t")
    .edge("gr", "st", exit="b", enter="t").edge("st", "out")
    .edge("cam", "small", exit="b", enter="t").edge("small", "vis")
)

cost = (
    Bars("polish-cost", "Time per 1080p frame (ms)",
         "Measured by rendering through a real libobs with OpenGL and waiting for the GPU every frame, on a MacBook Air M2, "
         "best of two runs of 200 frames (version 0.4.0). Pass-through is OBS capturing the source with the filter doing nothing.", unit="ms")
    .bar("Pass-through", 0.89, "", "grey")
    .bar("Defaults (smooth, brighten, sharpen)", 2.53, "", "green")
    .bar("Beauty, face shape and makeup (0.3.0 set)", 2.54, "", "green")
    .bar("Plus foundation, jaw, chin, nose, lips and eye makeup", 2.81, "", "green")
    .bar("Everything, adding soft light, look, vignette, grain, background blur, sticker", 3.69, "", "yellow")
)

analysis = (
    Sequence("polish-analysis", "How analysis stays off the render thread",
             "If analysis is still busy when a frame arrives, that frame is simply not analysed; the effects keep using "
             "the last result, smoothed over time against landmark jitter.",
             [("gpu", "Render thread", "blue"), ("stage", "Staging surface", "grey"), ("q", "Analysis thread", "yellow"),
              ("res", "Latest result", "green")])
    .msg("gpu", "stage", "copy a 384 px frame")
    .msg("stage", "q", "next frame: submit it, unless analysis is busy")
    .msg("q", "q", "faces, iris, lips and eye masks, person mask: a few ms to 20 ms")
    .msg("q", "res", "store under a lock")
    .msg("res", "gpu", "read every frame", dashed=True)
)

stack = (
    Stack("polish-stack", "What it is built from",
          "Everything below the OBS layer ships inside the plugin or with the operating system; nothing is downloaded at run time.")
    .layer("OBS", ["libobs 30 API\nOBS 30 to 33", "Direct3D 11\nOpenGL, Metal", "Tools menu\n+ hotkey"], "grey")
    .layer("Analysis", ["MediaPipe on\nONNX Runtime", "Apple Vision\n(macOS)", "Tracking,\nsmoothing"], "yellow")
    .layer("Effects", ["Bilateral\nskin filter", "Soft-light\nmakeup", "Displacement\nfield", "Dual-filter\nblur", "3D LUT"], "blue")
    .layer("Assets", ["17 looks", "10 stickers", "4 backdrops"], "green")
    .layer("Tests", ["Headless libobs\nrender harness", "24 checks", "Windows, Linux,\nmacOS in CI"], "purple")
)

timeline = (
    Timeline("polish-timeline", "Build status",
             "Version 0.5.0 adds 47 effects, contrast and a vignette that lightens on Windows, macOS and Linux; "
             "GPU inference for the face models comes next.")
    .phase("Filter + Vision", "beauty, shape", "done")
    .phase("Release 0.1.0", "11 checks", "done")
    .phase("Makeup, 0.2.0", "14 checks", "done")
    .phase("Windows, Linux, 0.3.0", "OBS 30 to 33", "done")
    .phase("Eyes, face, 0.4.0", "24 checks", "done")
    .phase("Effects, 0.5.0", "29 checks", "done")
)

DIAGRAMS = [pipeline, analysis, cost, stack, timeline]
