from csv import reader
import subprocess
import os


def github_commit(destination_dir):
    os.chdir(destination_dir)

    branch_name = "feat/backstage"
    commit_message = "chore: add entity descriptor"

    subprocess.run(["git", "checkout", "-b", branch_name])
    subprocess.run(["git", "add", "catalog-info.yaml"])
    subprocess.run(["git", "commit", "-m", commit_message])
    subprocess.run(["git", "push", "origin", branch_name])


apps_dir = f"{os.getcwd()}/backstage"

for count, repo_name in enumerate(os.listdir(apps_dir)):
    destination = f"{apps_dir}/{repo_name}"
    github_commit(destination)

print(f"Done!")
