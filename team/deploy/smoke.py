"""Authenticated smoke check. Credentials stay in a local mode-600 env file."""
import http.cookiejar
import json
from pathlib import Path
import sys
import urllib.parse
import urllib.request


base = "https://team.borili.uz"
credentials = dict(line.split("=", 1) for line in Path(sys.argv[1]).read_text().splitlines() if "=" in line)
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def get(path):
    with opener.open(base + path, timeout=30) as response:
        return json.load(response)


instance = get("/api/instances/")
csrf = get("/auth/get-csrf-token/")["csrf_token"]
data = urllib.parse.urlencode({"email": credentials["ADMIN_EMAIL"], "password": credentials["ADMIN_PASSWORD"], "csrfmiddlewaretoken": csrf}).encode()
request = urllib.request.Request(base + "/auth/sign-in/", data=data, headers={"Referer": base + "/", "Origin": base, "X-CSRFToken": csrf})
with opener.open(request, timeout=30) as response:
    assert response.status == 200
me = get("/api/users/me/")
assert me["email"].lower() == credentials["ADMIN_EMAIL"].lower(), "Password login did not authenticate the expected account"
workspaces = get("/api/users/me/workspaces/")
rows = workspaces if isinstance(workspaces, list) else workspaces.get("results", [])
assert any(row["slug"] == "sakura" for row in rows), "Sakura workspace is missing"
projects = get("/api/workspaces/sakura/projects/")
rows = projects if isinstance(projects, list) else projects.get("results", [])
assert any(row["identifier"] == "SAK" for row in rows), "Sakura project is missing"
print("HTTPS, CSRF, password login, authenticated user, workspace and project checks passed.")
