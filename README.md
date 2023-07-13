# Backstage

## Prerequisites

### Python

Pyton 3.8 or above and some plugins are required to run scripts. MacOS doesn't come with it out of the box.

Run `install_python_macos.sh` to install everything needed

### Github token

Generate Github token that has reqd/write access to repos.


## Running the scripts

Create `prerequisites/{system}` and copy `prepare_apps.py` form any other system. Change instances of other system to your system.

Create a bash script `prepare.sh` in that folder:

- for MacOS
```
# export GITHUB_ORG_NAME="superbet-group"
export GITHUB_ORG_NAME="superology-backend"
export GITHUB_TOKEN=""
python3.8 prepare_apps.py
```

- for Linux
```
# export GITHUB_ORG_NAME="superbet-group"
export GITHUB_ORG_NAME="superology-backend"
export GITHUB_TOKEN=""
python3 prepare_apps.py
```

Copy the generated `backstage.apps.json` file into the root of this project (aka. next to `backstage.elixir-libs.json` and `backstage.go-libs.json`)

Open the `catalog.sh` script, add token and organistaion and run the steps one by one.