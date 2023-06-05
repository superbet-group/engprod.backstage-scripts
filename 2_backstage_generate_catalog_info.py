import os
import re
import json
import yaml


class YamlDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(YamlDumper, self).increase_indent(flow, False)


def json_to_yaml(json_value):
    return yaml.dump(
        json_value,
        Dumper=YamlDumper,
        default_flow_style=False,
        sort_keys=False,
        indent=2,
    )


def template_component(entity):
    template = {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "Component",
        "metadata": {
            "title": entity["title"],
            "name": entity["name"],
            "description": entity.get("description", ""),
            "annotations": {
                "github.com/project-slug": f"{entity['github_org_name']}/{entity['github_repo_name']}"
            },
        },
        "spec": {
            "type": entity["type"],
            "lifecycle": "production",
            "owner": entity["owner"],
            "domain": entity["domain"],
            "system": entity["system"],
        },
    }

    return template


def template_api(entity):
    template = {
        "apiVersion": "backstage.io/v1alpha1",
        "kind": "API",
        "metadata": {
            "title": entity["title"],
            "name": entity["name"],
            "annotations": {
                "github.com/project-slug": f"{entity['github_org_name']}/{entity['github_repo_name']}"
            },
        },
        "spec": {
            "type": "openapi",
            "lifecycle": "production",
            "owner": entity["owner"],
            "domain": entity["domain"],
            "system": entity["system"],
        },
    }

    return template


def append_openapi_definition(entity, api):
    openapi_definition = f"""  definition: |
    openapi: "3.0.0"
    info:
      version: 1.0.0
      title: {entity['title']}
"""

    return f"{api}{openapi_definition}"


def append_grafana_links(catalog_info, entity):
    name_without_prefix = entity["repo_name"].replace(f"{entity['domain']}.", "")
    name_snake_case = name_without_prefix.replace("-", "_")

    links = []
    for env, env_name in [("dev", "Staging"), ("pro", "Production")]:
        link = {
            "url": f"https://grafana.superology.{env}/d/lUF3So77z/apps-generic-per-pod?orgId=1&var-namespace={entity['domain']}-rosuperbetsport&var-container=rosuperbetsport-{name_without_prefix}&var-pod=All&var-consumer_groups=All&var-container_underscore=rosuperbetsport_{name_snake_case}",
            "title": f"Grafana Dashboard {env_name}",
            "icon": "dashboard",
            "type": "grafana-dashboard",
        }
        links.append(link)
    catalog_info["metadata"]["links"] = links
    return catalog_info


def extract_go_deps(app, apps_dir, libs):
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

        if dependency_repo_name in libs:
            prefix = libs[dependency_repo_name]
        else:
            prefix = f"go-libs-{app['domain']}"

        name = dependency_repo_name.replace(".", "-")
        dependencies.append(f"component:{prefix}_{name}")

    return dependencies


def extract_elixir_deps(app, apps_dir, libs):
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


def format_title(value):
    name = value.split("_")[1]
    title = re.sub("-", " ", name)
    return title.title()


def format_name(value, prefix):
    name = re.sub("-|\.|_", "-", value)
    return f"{prefix}_{name}"


def guess_language(destination):
    if os.path.exists(f"{destination}/mix.exs"):
        return "elixir"

    if os.path.exists(f"{destination}/go.mod"):
        return "go"

    return None


def api_catalog_info(app, dependencies):
    entity_name = format_name(app["repo_name"], app["domain"])
    entity = {
        "name": entity_name,
        "title": format_title(entity_name),
        "description": app.get("app_description", ""),
        "github_repo_name": app["repo_name"],
        "github_org_name": GITHUB_ORG_NAME,
        "type": app["type"],
        "domain": app["domain"],
        "system": f"{app['domain']}_{app['system']}",
        "owner": app["owner"],
    }

    component = template_component(entity)
    component["spec"]["providesApis"] = [entity["name"]]
    if dependencies:
        component["spec"]["dependsOn"] = dependencies
    if GITHUB_ORG_NAME == "superology-backend":
        component = append_grafana_links(component, app)

    api = template_api(entity)

    catalog_info_component = json_to_yaml(component)
    catalog_info_api = json_to_yaml(api)
    catalog_info_api = append_openapi_definition(entity, catalog_info_api)

    catalog_info = "---\n".join([catalog_info_component, catalog_info_api])
    return catalog_info


def service_catalog_info(app, dependencies):
    entity_name = format_name(app["repo_name"], app["domain"])
    entity = {
        "name": entity_name,
        "title": format_title(entity_name),
        "description": app.get("app_description", ""),
        "github_repo_name": app["repo_name"],
        "github_org_name": GITHUB_ORG_NAME,
        "type": app["type"],
        "domain": app["domain"],
        "system": f"{app['domain']}_{app['system']}",
        "owner": app["owner"],
    }

    catalog_info = template_component(entity)
    if dependencies:
        catalog_info["spec"]["dependsOn"] = dependencies
    if GITHUB_ORG_NAME == "superology-backend":
        catalog_info = append_grafana_links(catalog_info, app)

    return json_to_yaml(catalog_info)


def library_catalog_info(app, dependencies):
    entity_name = format_name(app["repo_name"], app["domain"])
    entity = {
        "name": entity_name,
        "title": format_title(entity_name),
        "description": app.get("app_description", ""),
        "github_repo_name": app["repo_name"],
        "github_org_name": GITHUB_ORG_NAME,
        "type": app["type"],
        "domain": app["domain"],
        "system": f"{app['domain']}_{app['system']}",
        "owner": app["owner"],
    }

    catalog_info = template_component(entity)
    if dependencies:
        catalog_info["spec"]["dependsOn"] = dependencies

    return json_to_yaml(catalog_info)


def generate_catalog_info(app, apps_dir, libs):
    destination = f"{apps_dir}/{app['repo_name']}"
    language = guess_language(destination)

    if language == "go":
        app_dependencies = extract_go_deps(app, apps_dir, libs["go"])
    elif language == "elixir":
        app_dependencies = extract_elixir_deps(app, apps_dir, libs["elixir"])
    else:
        app_dependencies = []

    if app["type"] == "api":
        catalog_info = api_catalog_info(app, app_dependencies)
    elif app["type"] == "library":
        catalog_info = library_catalog_info(app, app_dependencies)
    elif app["type"] == "service":
        catalog_info = service_catalog_info(app, app_dependencies)

    return catalog_info


def create_catalog_info_file(app, apps_dir, content):
    destination = f"{apps_dir}/{app['repo_name']}"
    filename = f"{destination}/catalog-info.yaml"

    with open(filename, "w") as file:
        file.write(content)


def fetch_libs():
    go_libs_file = "backstage.go-libs.json"
    elixir_libs_file = "backstage.elixir-libs.json"

    happening_libs = {
        "go": {},
        "elixir": {},
    }

    with open(go_libs_file, "r") as file:
        libs = json.load(file)
        happening_libs["go"] = libs

    with open(elixir_libs_file, "r") as file:
        libs = json.load(file)
        happening_libs["elixir"] = libs

    return happening_libs


GITHUB_ORG_NAME = os.getenv("GITHUB_ORG_NAME")
apps_dir = "./backstage"
input_file = "backstage.apps.json"

file_apps = open(input_file)
applications = json.load(file_apps)
libs = fetch_libs()
total = 0
report = []

for count, app in enumerate(applications):
    if not os.path.exists(f"{apps_dir}/{app['repo_name']}"):
        print(f"{count+1}/{len(applications)} - {app['repo_name']} -> not found")
        continue

    template = generate_catalog_info(app, apps_dir, libs)

    if template:
        create_catalog_info_file(app, apps_dir, template)
        print(
            f"{count+1}/{len(applications)} - {app['repo_name']} -> catalog-info.yaml added"
        )
        total += 1
    else:
        print(
            f"{count+1}/{len(applications)} - {app['repo_name']} -> language not supported"
        )


print(f"\n\nDone - {total}/{len(applications)} descriptors created!")
