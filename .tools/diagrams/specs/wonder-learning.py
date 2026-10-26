from svgdiagram import Flow, Sequence

PAGE = "work/applications/wonder-learning.html"

architecture = (
    Flow("wl-architecture", "Wonder Learning module structure",
         "Two pages share one data file and one progress module. The catalog page renders cards with filters and "
         "search; the course page runs the YouTube player, completion, resume and the quiz. Progress lives in "
         "localStorage under one key.", cols=4)
    .node("idx", "index.html", "catalog page", at=(0, 0), color="cyan")
    .node("cat", "catalog.js", "cards, category filter, search, continue link", at=(0, 1), span=2, color="blue")
    .node("crs", "course.html", "course page", at=(1, 0), color="cyan")
    .node("ply", "player.js", "lesson list, YouTube player, resume, quiz", at=(1, 1), span=2, color="blue")
    .node("yt", "YouTube iframe API", "YT.Player, onStateChange", at=(1, 3), color="red")
    .node("data", "course-data.js", "6 courses, 20 lessons, 18 quiz questions", at=(0, 3), color="yellow")
    .node("prog", "progress.js", "getProgress, setComplete, saveResume, saveQuiz, filterCourses", at=(2, 1), span=2, color="green")
    .node("ls", "localStorage", "key wl-progress", at=(2, 3), color="purple")
    .edge("idx", "cat").edge("crs", "ply").edge("ply", "yt", "postMessage")
    .edge("cat", "data", "import").edge("ply", "prog").edge("prog", "ls", "JSON")
)

journey = (
    Flow("wl-journey", "A learner's path through a course",
         "Pick a course from the catalog, watch each lesson (it is marked done when the video ends, or by hand), "
         "come back later to the saved position, then take the quiz once every lesson is done.", cols=4)
    .node("a", "Catalog", "filter by category, search", at=(0, 0), color="cyan")
    .node("b", "Course page", "first unfinished lesson opens", at=(0, 1), color="blue")
    .node("c", "Watch a lesson", "position saved every 5 s", at=(0, 2), color="blue")
    .node("d", "Video ends", "lesson marked done", at=(0, 3), color="green")
    .node("e", "Next lesson", "or pick any from the list", at=(1, 3), color="blue")
    .node("f", "All lessons done", "quiz unlocks", at=(1, 2), color="yellow")
    .node("g", "Knowledge check", "3 questions, right and wrong marked", at=(1, 1), color="yellow")
    .node("h", "Course complete", "best score shown on the catalog", at=(1, 0), color="green")
    .edge("a", "b").edge("b", "c").edge("c", "d").edge("d", "e").edge("e", "f", "last lesson")
    .edge("f", "g").edge("g", "h")
)

player = (
    Sequence("wl-player", "Talking to the YouTube player",
             "player.js loads the iframe API, creates the player when it is ready, saves the playback position while "
             "the video plays, and marks the lesson done when the video ends.",
             [("page", "player.js", "blue"), ("api", "iframe API", "red"), ("frame", "YouTube player", "red"), ("store", "progress.js", "green")])
    .msg("page", "api", "load https://www.youtube.com/iframe_api")
    .msg("api", "page", "onYouTubeIframeAPIReady()", dashed=True)
    .msg("page", "frame", "new YT.Player(videoId, start: saved seconds)")
    .msg("frame", "page", "onReady: hide the fallback link", dashed=True)
    .msg("frame", "page", "onStateChange: PLAYING", dashed=True)
    .msg("page", "store", "every 5 s: saveResume(lesson, getCurrentTime())")
    .msg("frame", "page", "onStateChange: ENDED", dashed=True)
    .msg("page", "store", "setComplete(lesson); clear the resume point")
    .note("If the API never loads within 8 s, a direct Watch on YouTube link appears", over=("page", "frame"))
)

DIAGRAMS = [architecture, journey, player]
