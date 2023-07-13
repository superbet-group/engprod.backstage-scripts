import json
import requests
import os


def guess_type(app_name, libs):
    if app_name in libs:
        return "library"

    if "api" in app_name:
        return "api"

    return "service"


def guess_system(app_name, libs):
    if app_name in libs:
        return "elixir-libs-stats"


def get_organization_repos():
    url = f"https://api.github.com/orgs/{GITHUB_ORG_NAME}/repos"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
    }

    repos = []
    page = 1
    per_page = 100

    while True:
        params = {"page": page, "per_page": per_page}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            repo_data = response.json()

            if len(repo_data) == 0:
                break

            print(f"Fetching apps from GitHub: {page}/6")
            repos.extend(repo_data)
            page += 1
        else:
            print(f"Failed to fetch repositories for organization '{GITHUB_ORG_NAME}'.")
            print(f"Status Code: {response.status_code}")
            break

    return repos


def fetch_apps(libs):
    repos = get_organization_repos()
    apps = []

    for repo in repos:
        if repo["name"].startswith("stats."):
            if repo["name"] in ["stats.gitops", "stats.documentation"]:
                continue

            name = repo["name"]
            system = guess_system(name, libs)

            app_details = {
                "domain": "stats",
                "system": system,
                "repo_name": name,
                "app_description": "",
                "type": guess_type(name, libs),
                "owner": "stats",
            }

            apps.append(app_details)

    return apps


GITHUB_ORG_NAME = os.getenv("GITHUB_ORG_NAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
output_file = "backstage.apps.json"
libs_file = "../../backstage.elixir-libs.json"

file_libs = open(libs_file)
libs = json.load(file_libs)

if os.path.exists(output_file):
    os.remove(output_file)

applications = fetch_apps(libs)
with open(output_file, "a+") as file:
    file.write(json.dumps(applications))
