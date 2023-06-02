import os
import re
import json


TEMPLATE_COMPONENT = """
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  title: {title}
  name: {name}
  annotations:
    github.com/project-slug: superbet-group/{repo_name}
spec:
  type: {type}
  lifecycle: production
  owner: {owner}
  domain: {domain}
  system: {system}
"""

TEMPLATE_COMPONENT_API = """
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  title: {title}
  name: {name}
  annotations:
    github.com/project-slug: superbet-group/{repo_name}
spec:
  type: {type}
  lifecycle: production
  owner: {owner}
  domain: {domain}
  system: {system}
  providesApis:
    - {name}
"""

TEMPLATE_API = """
apiVersion: backstage.io/v1alpha1
kind: API
metadata:
  title: {title}
  name: {name}
  annotations:
    github.com/project-slug: superology-backend/{repo_name}
spec:
  type: openapi
  lifecycle: production
  owner: {owner}
  domain: {domain}
  system: {system}
  definition: |
    openapi: "3.0.0"
    info:
      version: 1.0.0
      title: {title}
"""


def extract_deps(app, apps_dir, libs):
    mod_file = open(f"{apps_dir}/{app['repo_name']}/go.mod")
    mod_file_content = mod_file.read()
    deps_regex = re.compile(r"github.com\/superbet-group\/.*")

    deps_list = deps_regex.findall(mod_file_content)
    dependencies = []

    for dependency in deps_list:
        if dependency.endswith("// indirect"):
            continue
        if app["repo_name"] in dependency:
            continue

        dependency_repo_name = (
            dependency.split(" ")[0]
            .replace("/v1", "")
            .replace("/v2", "")
            .replace("/v3", "")
            .replace("/v4", "")
            .replace("/go", "")
            .split("/")[-1]
        )

        name = dependency_repo_name.replace(".", "-")
        if dependency_repo_name in libs:
            prefix = libs[dependency_repo_name]
        else:
            prefix = f"go-libs-{app['domain']}"

        dependencies.append(f"component:{prefix}_{name}")

    return dependencies


def format_title(value):
    title = re.sub("-|\.|_", " ", value)
    return title.title()


def format_name(value, prefix):
    name = re.sub("-|\.|_", "-", value)
    return f"{prefix}_{name}"


def catalog_info_component(app, destination, libs):
    template = TEMPLATE_COMPONENT.format(
        name=format_name(app["repo_name"], app["domain"]),
        title=format_title(app["repo_name"]),
        repo_name=app["repo_name"],
        type=app["type"],
        domain=app["domain"],
        system=f"{app['domain']}_{app['system']}",
        owner=app["owner"],
    )

    return template


def catalog_info_component_api(app, destination, libs):
    template = TEMPLATE_COMPONENT_API.format(
        name=format_name(app["repo_name"], app["domain"]),
        title=format_title(app["repo_name"]),
        repo_name=app["repo_name"],
        type=app["type"],
        domain=app["domain"],
        system=f"{app['domain']}_{app['system']}",
        owner=app["owner"],
    )

    return template


def catalog_info_api(repo_name, destination, libs):
    template = TEMPLATE_API.format(
        name=format_name(app["repo_name"], app["domain"]),
        title=format_title(app["repo_name"]),
        repo_name=app["repo_name"],
        domain=app["domain"],
        system=f"{app['domain']}_{app['system']}",
        owner=app["owner"],
    )

    return template


def depends_on_list(dependencies):
    if not dependencies:
        return ""

    newline = "\n"

    depends_on_template = f"""  dependsOn:
{newline.join([f"    - {dep}" for dep in dependencies])}
"""

    return depends_on_template


def generate_catalog_info(app, apps_dir, libs):
    destination = f"{apps_dir}/{app['repo_name']}"

    if not os.path.exists(f"{destination}/go.mod"):
        return None

    app_dependencies = extract_deps(app, apps_dir, libs)

    if app["type"] == "api":
        component_template = catalog_info_component_api(app, apps_dir, libs)
        component_template = "".join(
            [component_template, depends_on_list(app_dependencies)]
        )

        api_template = catalog_info_api(app, apps_dir, libs)
        template = "---".join([component_template, api_template])
    else:
        component_template = catalog_info_component(app, apps_dir, libs)
        template = "".join([component_template, depends_on_list(app_dependencies)])

    return template


def create_catalog_info_file(app, apps_dir, content):
    destination = f"{apps_dir}/{app['repo_name']}"
    filename = f"{destination}/catalog-info.yaml"

    with open(filename, "w") as file:
        file.write(content)


GITHUB_ORG_NAME = os.getenv("GITHUB_ORG_NAME")

apps_dir = "./backstage"
input_file = "backstage.apps.json"
libs_file = "backstage.go-libs.json"

file_apps = open(input_file)
applications = json.load(file_apps)

file_libs = open(libs_file)
libs = json.load(file_libs)

for count, app in enumerate(applications):
    template = generate_catalog_info(app, apps_dir, libs)

    if template:
        create_catalog_info_file(app, apps_dir, template)
        print(
            f"{count+1}/{len(applications)} - {app['repo_name']} catalog-info.yaml added"
        )
    else:
        print(f"{count+1}/{len(applications)} - {app['repo_name']} -> not a GO project")

    count += 1

print(f"\n\nDone - {len(applications)} descriptors created!")
