import sys
import os
import json
from csv import reader


def guess_type(app_name, libs):
    if app_name in libs:
        return "library"

    if "lib" in app_name:
        return "library"

    if "api" in app_name:
        return "api"

    return "service"


def guess_domain_and_system(app_name, libs):
    if app_name in libs:
        system = libs[app_name]
        domain = system.replace("go-libs-", "") or "tech"

        return (domain, system)

    if "lib" in app_name:
        return ("betting", "go-libs-betting")

    if len(app_name.split(".")) == 3:
        return ("betting", app_name.split(".")[1])

    if len(app_name.split(".")) == 2:
        return ("betting", app_name.split(".")[0])

    return ("betting", "")


def fetch_apps(apps_file, libs):
    apps = []

    with open(apps_file, "r") as file:
        csv_file = reader(file)

        for row in csv_file:
            repo_url = row[0]
            repo_name = repo_url.strip().split("/")[-1]
            (domain, system) = guess_domain_and_system(repo_name, libs)

            app_details = {
                "domain": domain,
                "system": system,
                "repo_name": repo_name,
                "app_description": "",
                "type": guess_type(repo_name, libs),
                "owner": "betting",
            }

            apps.append(app_details)

    return apps


input_file = "betting.txt"
output_file = "backstage.apps.json"
libs_file = "../../backstage.go-libs.json"

file_libs = open(libs_file)
libs = json.load(file_libs)

if os.path.exists(output_file):
    os.remove(output_file)

applications = fetch_apps(input_file, libs)
with open(output_file, "a+") as file:
    file.write(json.dumps(applications))
