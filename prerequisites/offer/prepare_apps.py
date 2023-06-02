import sys
import json
from csv import reader


def guess_type(app_name, libs):
    if app_name in libs:
        return "library"

    if "api" in app_name:
        return "api"

    return "service"


def fetch_apps(apps_file, libs):
    apps = []

    with open(apps_file, "r") as file:
        csv_file = reader(file)

        for row in csv_file:
            [
                _,
                _relations,
                _components,
                name,
                _,
                _,
                _status,
                _priority,
                _deployments,
                description,
                _complexity,
            ] = row

            app_details = {
                "domain": "offer",
                "system": "system",
                "repo_name": name,
                "app_description": description,
                "type": guess_type(name, libs),
                "owner": "offer",
            }

            apps.append(app_details)

    return apps


input_file = "offer.csv"
output_file = "backstage.apps.json"
libs_file = "../../backstage.go-libs.json"

file_libs = open(libs_file)
libs = json.load(file_libs)

applications = fetch_apps(input_file, libs)
with open(output_file, "a+") as file:
    file.write(json.dumps(applications))
