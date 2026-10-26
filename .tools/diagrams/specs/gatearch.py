from svgdiagram import Flow, Sequence

PAGE = "work/applications/gatearch.html"

request = (
    Flow("ga-request", "What happens on every request",
         "Each page includes bootstrap.php, which starts a hardened session and rejects a POST without a valid CSRF "
         "token. The page's first line checks the role. Queries go through repo.php only, output through h(), and a "
         "successful POST ends in a redirect.", cols=4)
    .node("req", "HTTP request", "Apache, web root is public/", at=(0, 0), color="cyan")
    .node("boot", "bootstrap.php", "session: HttpOnly, SameSite=Lax", at=(0, 1), color="blue")
    .node("csrf", "verify_csrf()", "POST without token: 403", at=(0, 2), color="red")
    .node("role", "require_role()", "logged out: login page, wrong role: 403", at=(0, 3), color="red")
    .node("page", "Page script", "validate input on the server", at=(1, 3), color="blue")
    .node("repo", "repo.php", "prepared statements only", at=(1, 2), color="green")
    .node("db", "MySQL 8", "keys, checks, cascades", at=(1, 1), color="yellow")
    .node("out", "Response", "h() on all output, or redirect after POST", at=(2, 3), color="cyan")
    .edge("req", "boot").edge("boot", "csrf").edge("csrf", "role").edge("role", "page")
    .edge("page", "repo").edge("repo", "db", "PDO").edge("page", "out")
)

schema = (
    Flow("ga-schema", "Database schema",
         "Students and admins share the users table. Enrollments link a student to a course, unique per pair; each "
         "enrollment has at most one grade. Deleting a user or a course cascades to enrollments and grades. Login "
         "attempts and the audit log stand alone.", cols=4)
    .node("users", "users", "id, username UNIQUE, full_name, password_hash, role student or admin", at=(0, 0), span=2, color="blue")
    .node("courses", "courses", "id, code UNIQUE, name, credits 1 to 12, description", at=(0, 2), span=2, color="blue")
    .node("enr", "enrollments", "student_id, course_id, UNIQUE pair, enrolled_at", at=(1, 1), span=2, color="green")
    .node("grades", "grades", "enrollment_id UNIQUE, grade 0 to 100, updated_at", at=(2, 1), span=2, color="yellow")
    .node("la", "login_attempts", "username, ip, attempted_at", at=(2, 3), color="grey")
    .node("audit", "audit_log", "actor, action, detail, created_at", at=(2, 0), color="grey")
    .edge("enr", "users", "ON DELETE CASCADE", exit="t", enter="b")
    .edge("enr", "courses", "ON DELETE CASCADE", exit="t", enter="b")
    .edge("grades", "enr", "ON DELETE CASCADE")
)

login = (
    Sequence("ga-login", "Logging in",
             "The throttle is checked before the password. Unknown users and wrong passwords get the same answer. "
             "A correct login clears the failures, re-hashes the password if PHP's default changed, and gets a fresh "
             "session ID.",
             [("b", "Browser", "cyan"), ("l", "login.php", "blue"), ("r", "repo.php", "green"), ("d", "Database", "yellow")])
    .msg("b", "l", "POST username, password, csrf")
    .msg("l", "r", "recent_failures(user, ip)")
    .msg("r", "d", "COUNT per username and per IP, last 15 min")
    .note("5 per username or 20 per IP: Too many failed attempts", over=("l", "r"))
    .msg("l", "r", "find_user_by_username()")
    .msg("l", "l", "password_verify()")
    .msg("l", "r", "wrong: record_failure(); right: clear_failures()")
    .msg("l", "l", "session_regenerate_id(true), store id and role")
    .msg("l", "b", "302 to admin.php or dashboard.php", dashed=True)
)

DIAGRAMS = [request, schema, login]
