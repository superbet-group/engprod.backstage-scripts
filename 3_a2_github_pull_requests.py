import os
import requests
import json


def github_pr(repo_name):
    pr_title = "Backstage - add entity descriptor"
    pr_body = f"""
  An entity descriptor is a YAML file containing metadata, enabling the visualization and management of a particular entity within the Backstage.

  Details: https://happening-docs-engprod-prod.teleport.eu-central-1.prod.incubator.sb-cloud.io/incubator-handbook/Backstage/software_catalog/2._happenings_software_catalog/index.html#library
  """

    pr_url = f"https://api.github.com/repos/{GITHUB_ORG_NAME}/{repo_name}/pulls"
    pr_headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    pr_payload = {
        "title": pr_title,
        "body": pr_body,
        "head": "feat/backstage",
        "base": "master",
        "assignees": [],
        "reviewers": [],
    }

    response = requests.post(pr_url, data=json.dumps(pr_payload), headers=pr_headers)
    response.raise_for_status()

    pr_data = response.json()
    print(f"Pull request created: {pr_data['html_url']}")


GITHUB_ORG_NAME = os.getenv("GITHUB_ORG_NAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
apps_dir = "./backstage"
count = 0

for count, repo_name in enumerate(os.listdir(apps_dir)):
    destination = f"{apps_dir}/{repo_name}"
    github_pr(destination)
    count += 1

print(f"Done - {count} PRs created!")
