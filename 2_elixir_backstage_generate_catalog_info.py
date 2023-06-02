import os
import re
import json


TEMPLATE_COMPONENT_SERVICE = """
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  title: {title}
  name: {name}
  annotations:
    github.com/project-slug: {org_name}/{repo_name}
  links:
    - url: https://grafana.superology.dev/d/lUF3So77z/apps-generic-per-pod?orgId=1&var-namespace={domain}-rosuperbetsport&var-container=rosuperbetsport-{name_without_prefix}&var-pod=All&var-consumer_groups=All&var-container_underscore=rosuperbetsport_{name_snake_case}
      title: Grafana Dashboard Staging
      icon: dashboard
      type: grafana-dashboard
    - url: https://grafana.superology.pro/d/lUF3So77z/apps-generic-per-pod?orgId=1&var-namespace={domain}-rosuperbetsport&var-container=rosuperbetsport-{name_without_prefix}&var-pod=All&var-consumer_groups=All&var-container_underscore=rosuperbetsport_{name_snake_case}
      title: Grafana Dashboard Production
      icon: dashboard
      type: grafana-dashboard
spec:
  type: {type}
  lifecycle: production
  owner: {owner}
  domain: {domain}
  system: {system}
"""


TEMPLATE_COMPONENT_LIB = """
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  title: {title}
  name: {name}
  annotations:
    github.com/project-slug: {org_name}/{repo_name}
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
    github.com/project-slug: {org_name}/{repo_name}
  links:
    - url: https://grafana.superology.dev/d/lUF3So77z/apps-generic-per-pod?orgId=1&var-namespace={domain}-rosuperbetsport&var-container=rosuperbetsport-{name_without_prefix}&var-pod=All&var-consumer_groups=All&var-container_underscore=rosuperbetsport_{name_snake_case}
      title: Grafana Dashboard Staging
      icon: dashboard
      type: grafana-dashboard
    - url: https://grafana.superology.pro/d/lUF3So77z/apps-generic-per-pod?orgId=1&var-namespace={domain}-rosuperbetsport&var-container=rosuperbetsport-{name_without_prefix}&var-pod=All&var-consumer_groups=All&var-container_underscore=rosuperbetsport_{name_snake_case}
      title: Grafana Dashboard Production
      icon: dashboard
      type: grafana-dashboard
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
    github.com/project-slug: {org_name}/{repo_name}
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
    mix_file = open(f"{apps_dir}/{app['repo_name']}/mix.exs")
    mix_file_content = mix_file.read()
    deps_regex = re.compile(r" Deps.Superology.*")

    deps_list = deps_regex.findall(mix_file_content)
    dependencies = []

    for dependency in deps_list:
        dependency = dependency.strip().replace("()", "").replace(",", "")

        if not dependency.startswith("Deps.Superology."):
            continue

        prefix = libs[dependency]
        name = dependency.split(".")[-1].replace("_", "-")

        dependencies.append(f"component:{prefix}_{name}")

    return dependencies


def format_title(value, prefix):
    title = re.sub("-|\.|_", " ", value).replace(f"{prefix} ", "", 1)
    return title.title()


def format_name(app):
    name = re.sub("-|\.|_", "-", app["repo_name"]).replace(f"{app['domain']}-", "", 1)

    if app["type"] == "library":
        return f"{app['system']}_{name}"

    return f"{app['domain']}_{name}"


def catalog_info_component(app, destination, libs):
    name = format_name(app)

    if app["type"] == "library":
        template = TEMPLATE_COMPONENT_LIB
    else:
        template = TEMPLATE_COMPONENT_SERVICE

    template = template.format(
        name=name,
        name_without_prefix=name.split("_")[1],
        name_snake_case=name.split("_")[1].replace("-", "_"),
        title=format_title(app["repo_name"], app["domain"]),
        repo_name=app["repo_name"],
        type=app["type"],
        domain=app["domain"],
        system=f"{app['domain']}_{app['system']}",
        owner=app["owner"],
        org_name=GITHUB_ORG_NAME,
    )

    return template


def catalog_info_component_api(app, destination, libs):
    name = format_name(app)

    template = TEMPLATE_COMPONENT_API.format(
        name=name,
        name_without_prefix=name.split("_")[1],
        name_snake_case=name.split("_")[1].replace("-", "_"),
        title=format_title(app["repo_name"], app["domain"]),
        repo_name=app["repo_name"],
        type=app["type"],
        domain=app["domain"],
        system=f"{app['domain']}_{app['system']}",
        owner=app["owner"],
        org_name=GITHUB_ORG_NAME,
    )

    return template


def catalog_info_api(app, destination, libs):
    name = format_name(app)

    template = TEMPLATE_API.format(
        name=name,
        title=format_title(app["repo_name"], app["domain"]),
        repo_name=app["repo_name"],
        domain=app["domain"],
        system=f"{app['domain']}_{app['system']}",
        owner=app["owner"],
        org_name=GITHUB_ORG_NAME,
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

    if not os.path.exists(f"{destination}/mix.exs"):
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
libs_file = "backstage.elixir-libs.json"

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
        print(
            f"{count+1}/{len(applications)} - {app['repo_name']} -> not an Elixir project"
        )

    count += 1

print(f"\n\nDone - {len(applications)} descriptors created!")
