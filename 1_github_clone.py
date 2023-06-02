import json
import subprocess
import os


def clone_github_repo(repo_name, destination_dir):
    github_https_url = (
        f"https://{GITHUB_TOKEN}:x-oauth-basic@github.com/{GITHUB_ORG_NAME}/{repo_name}"
    )

    try:
        git_command = f"git clone {github_https_url} {destination_dir}/{repo_name}"
        process = subprocess.Popen(git_command.split())
        process.wait()

        if process.returncode == 0:
            print(f"Repo {repo_name} cloned successfully.")
        else:
            print(f"Error cloning repository {repo_name}.")

    except Exception as e:
        print(f"Error cloning repository: {e}")


GITHUB_ORG_NAME = os.getenv("GITHUB_ORG_NAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

input_file = "backstage.apps.json"
destination = "./backstage"

f = open(input_file)
applications = json.load(f)

for count, app in enumerate(applications):
    clone_github_repo(app["repo_name"], destination)

    print(f"\n{count+1}/{len(applications)} - {app['repo_name']} cloned")
    count += 1


print(f"\n\nDone - {len(applications)} apps cloned")
