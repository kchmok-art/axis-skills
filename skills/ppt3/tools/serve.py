#!/usr/bin/env python3
"""덱 저장 서버 — 브라우저에서 글자를 고치는 즉시 원본 HTML 에 저장되게 한다.

RDDcat/maro-ppt 의 tools/serve.py (MIT) 를 Windows·프로젝트 폴더 기준으로 손본 것.
브라우저는 file:// 로 연 파일에 스스로 쓸 수 없다. 이 서버로 덱을 열면 편집할 때마다
덱이 PUT 으로 원본을 덮어쓴다. 파일 고르기 창이 없다.

  python tools/serve.py --open "덱.html"   # 서버가 없으면 띄우고(루트 = 그 파일의 폴더), 덱을 브라우저로 연다
  python tools/serve.py --stop             # 서버 끄기

- 127.0.0.1 에서만 듣는다. 루트 폴더 아래 .html 만 쓴다(PUT).
  읽기(GET)는 덱이 상대 경로로 부르는 사진·글꼴·스크립트(STATIC 확장자)까지 내준다 — 사진이 든 덱도 서버 모드에서 보인다.
  루트는 --open 한 파일의 폴더다. (환경변수 MARO_PPT_ROOT 로 바꿀 수 있다)
- 쓰기는 X-Maro 헤더가 있어야 받는다 → 다른 사이트가 몰래 쓸 수 없다(CORS 사전 요청을 허락하지 않는다).
- X-Base-Mtime 이 지금 파일과 다르면(에이전트가 그 사이 고쳤으면) 409 로 거절한다.
  덱은 409 를 받으면 새로고침하고, 저장 안 한 편집을 원래 글자 기준으로 다시 붙여 저장한다.
"""
import http.server, json, mimetypes, os, sys, subprocess, time, urllib.parse, urllib.request, tempfile, signal

PORT = int(os.environ.get("MARO_PPT_PORT", "8765"))
PIDFILE = os.path.join(tempfile.gettempdir(), f"maro-ppt-serve-{PORT}.pid")
ROOT = os.path.realpath(os.environ.get("MARO_PPT_ROOT") or os.getcwd())
HTML = (".html", ".htm")
STATIC = HTML + (".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".svg", ".ico", ".css", ".js", ".json",
                 ".woff", ".woff2", ".ttf", ".otf", ".mp4", ".webm", ".mp3", ".pdf")


def under(p, root):
    p, root = os.path.normcase(os.path.realpath(p)), os.path.normcase(os.path.realpath(root))
    return p == root or p.startswith(root.rstrip(os.sep) + os.sep)


def resolve(url_path, exts=HTML):
    rel = urllib.parse.unquote(url_path.split("?")[0]).lstrip("/")
    p = os.path.realpath(os.path.join(ROOT, *rel.split("/")))
    if not under(p, ROOT) or not p.lower().endswith(exts):
        return None
    return p


def ctype(p):
    if p.lower().endswith(HTML):
        return "text/html; charset=utf-8"
    t = mimetypes.guess_type(p)[0] or "application/octet-stream"
    return t + ("; charset=utf-8" if t.startswith("text/") or t.endswith(("javascript", "json")) else "")


def mtime(p):
    return int(os.stat(p).st_mtime_ns // 1_000_000)


class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body=b"", ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/__maro/ping":
            return self.send(200, {"ok": True, "root": ROOT})
        if u.path == "/__maro/stat":
            p = resolve(urllib.parse.parse_qs(u.query).get("p", [""])[0])
            if not p or not os.path.isfile(p):
                return self.send(404, {"error": "not found"})
            return self.send(200, {"mtime": mtime(p)})
        p = resolve(u.path, STATIC)           # 읽기는 사진·글꼴까지, 쓰기(PUT)는 .html 만
        if not p or not os.path.isfile(p):
            return self.send(404, b"not found", "text/plain")
        with open(p, "rb") as f:
            self.send(200, f.read(), ctype(p))

    def do_PUT(self):
        if self.headers.get("X-Maro") != "1":
            return self.send(403, {"error": "X-Maro header required"})
        p = resolve(urllib.parse.urlparse(self.path).path)
        if not p or not os.path.isfile(p):
            return self.send(404, {"error": "not found"})
        base = self.headers.get("X-Base-Mtime")
        if base and base != "0" and int(base) != mtime(p):
            return self.send(409, {"error": "changed on disk", "mtime": mtime(p)})
        n = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(n)
        if not data.strip():
            return self.send(400, {"error": "empty"})
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(p), prefix=".maro-", suffix=".tmp")
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, p)
        self.send(200, {"mtime": mtime(p)})


def ping():
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/__maro/ping", timeout=1) as r:
            d = json.load(r)
            return d if d.get("ok") else None
    except Exception:
        return None


def url_for(path, root):
    rel = os.path.relpath(os.path.realpath(path), root)
    return f"http://127.0.0.1:{PORT}/" + "/".join(urllib.parse.quote(s) for s in rel.split(os.sep))


def spawn(root):
    env = dict(os.environ, MARO_PPT_ROOT=root)
    kw = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "env": env}
    if os.name == "nt":
        kw["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kw["start_new_session"] = True
    subprocess.Popen([sys.executable, os.path.abspath(__file__), "--serve"], **kw)
    for _ in range(50):
        if ping():
            return True
        time.sleep(0.1)
    return False


def main():
    a = sys.argv[1:]
    if a[:1] == ["--serve"]:
        with open(PIDFILE, "w") as f:
            f.write(str(os.getpid()))
        http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
    elif a[:1] == ["--stop"]:
        try:
            os.kill(int(open(PIDFILE).read()), signal.SIGTERM)
            os.remove(PIDFILE)
            print("stopped")
        except Exception:
            print("not running")
    elif a[:1] == ["--open"] and len(a) == 2:
        path = os.path.realpath(a[1])
        if not os.path.isfile(path):
            sys.exit(f"파일이 없습니다: {path}")
        root = os.path.dirname(path)
        live = ping()
        if live and not under(path, live["root"]):
            sys.exit(f"저장 서버가 다른 폴더({live['root']})로 떠 있습니다. 먼저 --stop 한 뒤 다시 여세요.")
        if live:
            root = live["root"]
        elif not spawn(root):
            sys.exit("저장 서버를 띄우지 못했습니다.")
        u = url_for(path, root)
        print(u)
        import webbrowser
        webbrowser.open(u)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
