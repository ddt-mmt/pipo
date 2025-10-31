# pipo

A modern tool to generate `requirements.txt` for a Python project, inspired by `pipreqs`.

`pipo` scans a project directory, analyzes all Python files for their imports, and generates a clean `requirements.txt` file containing only the external dependencies.

## How it Works

The tool uses Python's built-in `ast` (Abstract Syntax Tree) module to safely and accurately parse Python files. It identifies all `import` and `from ... import` statements, filters out standard library modules, and writes the result to a file.

## Installation

To install the tool from the local source code, you can run `pip` from the directory containing the `pipo` folder (e.g., from `/root` if your project is in `/root/pipo`):

```bash
# We recommend installing in "editable" mode for development
pip install -e ./pipo
```

Once installed, `pipo` becomes a global command available in your terminal.

## Global Options

These options can be used with `pipo` or any of its subcommands.

*   `pipo --help` or `pipo -h`
    *   Shows the help message with all available commands and options.

*   `pipo --version` or `pipo -v`
    *   Shows the currently installed version of `pipo`.

## Ringkasan Penggunaan

`pipo` adalah alat serbaguna untuk mengelola dependensi Python, membuat Dockerfile, dan lainnya. Berikut adalah ringkasan cepat perintah-perintah utamanya:

*   **`pipo scan [path]`**: Memindai direktori proyek Python dan menghasilkan `requirements.txt`.
*   **`pipo dockerize [path] [...]`**: Membuat `Dockerfile` dasar untuk proyek Python Anda.
*   **`pipo update`**: Memperbarui alat `pipo` ke versi terbaru.
*   **`pipo uninstall`**: Mencopot pemasangan alat `pipo`.

Untuk detail lebih lanjut tentang setiap perintah, silakan lihat bagian "Commands" di bawah.

## Commands

`pipo` provides several commands to manage your Python projects.

### `pipo scan [path]`

Scans a Python project directory and generates a `requirements.txt` file based on its imports. If `path` is not provided, it scans the current directory.

**Usage:**

```bash
# Scan the current directory
pipo scan

# Scan a specific directory (e.g., your project at /root/my_project)
pipo scan /root/my_project
```

In both cases, the resulting `requirements.txt` file will be created inside the scanned project directory.

### `pipo update`

Updates the `pipo` tool to the latest version by pulling changes from its Git repository and reinstalling it.

**Usage:**

```bash
pipo update
```

### `pipo uninstall`

Uninstalls the `pipo` tool from your system.

**Usage:**

```bash
pipo uninstall
```

### `pipo dockerize [path] [--app-type {flask,django,script}] [--main-file MAIN_FILE] [--port PORT]`

Generates a basic `Dockerfile` for a Python project. If `path` is not provided, it generates the Dockerfile in the current directory.

**Arguments:**

*   `path`: The path to the project directory where the Dockerfile will be generated (defaults to current directory).
*   `--app-type`: Type of Python application (choices: `flask`, `django`, `script`). Default is `flask`.
*   `--main-file`: The main application file (e.g., `app.py`, `manage.py`). Default is `app.py`.
*   `--port`: The port your application listens on. Default is `5000`.

**Usage Examples:**

```bash
# Generate Dockerfile for a Flask app in the current directory (default settings)
pipo dockerize

# Generate Dockerfile for a Django app in a specific project folder
pipo dockerize /path/to/my_django_project --app-type django --main-file manage.py --port 8000

# Generate Dockerfile for a simple Python script
pipo dockerize ./my_script_project --app-type script --main-file run.py


### `pipo init-ci [path] [--platform {github-actions}] [--docker-image-name DOCKER_IMAGE_NAME] [--push-docker-image]`

Generates a basic CI/CD configuration file for the project.

**Arguments:**

*   `path`: The path to the project directory where the CI config will be generated (defaults to current directory).
*   `--platform`: The CI/CD platform for which to generate the configuration (e.g., `github-actions`). Default is `github-actions`.
*   `--docker-image-name`: The name of the Docker image to build and push (e.g., your-docker-username/your-repo). Default is `pipo-app`.
*   `--push-docker-image`: Set this flag to enable pushing the Docker image to a registry. Requires `DOCKER_USERNAME` and `DOCKER_PASSWORD` GitHub Secrets.

**Usage Examples:**

```bash
# Generate GitHub Actions CI config in the current directory
pipo init-ci

# Generate GitHub Actions CI config for a specific project
pipo init-ci /path/to/my_project --platform github-actions

# Generate GitHub Actions CI config with a custom Docker image name and enable push
pipo init-ci --docker-image-name your-docker-username/your-app --push-docker-image
```

### `pipo kube [path] [-i IMAGE] [-a APP_NAME] [-p PORT] [-s SERVICE_TYPE] [-n NAMESPACE] [-g] [--host HOST] [--path-ingress PATH_INGRESS] [--ingress-class INGRESS_CLASS]`

This command is interactive by default, guiding you through the process of generating Kubernetes `deployment.yaml`, `service.yaml`, and optionally `ingress.yaml` files for a Python application. It can also be run non-interactively by providing all arguments.

**Arguments:**

*   `path`: The path to the project directory where the YAML files will be generated (defaults to current directory).
*   `-i`, `--image`: The Docker image to deploy (e.g., `your-docker-username/your-app:v1`). **Required if not running interactively.**
*   `-a`, `--app-name`: The name for the application. Defaults to being derived from the image name.
*   `-p`, `--port`: The application container port. Default is `8080`.
*   `-s`, `--service-type`: The Service type (choices: `NodePort`, `LoadBalancer`, `ClusterIP`). Default is `NodePort`.
*   `-n`, `--namespace`: The Kubernetes Namespace to deploy to. Default is `default`.
*   `-g`, `--ingress`: Set this flag to generate an Ingress YAML file. If set, `--host` will be prompted if not provided.
*   `--host`: The Ingress hostname (e.g., `your-app.example.com`). Required if `--ingress` is used and not running interactively.
*   `--path-ingress`: The Ingress path (e.g., `/` or `/api`). Default is `/`.
*   `--ingress-class`: The Ingress Class to use (e.g., `nginx`, `traefik`). Default is `nginx`.

**Usage Examples:**

```bash
# Run interactively (will prompt for all details)
pipo kube

# Generate YAMLs with minimal arguments (will prompt for namespace, ingress details)
pipo kube -i your-docker-username/your-app:v1 -p 5000

# Generate YAMLs with all arguments provided, including Ingress
pipo kube -i your-docker-username/your-app:v1 -p 5000 -n your-namespace -g --host your-app.example.com --path-ingress / --ingress-class nginx

# Generate YAMLs for a specific project directory
pipo kube /path/to/my_project -i your-docker-username/your-app:latest
```

### `pipo security-scan [path]`

Scans the `requirements.txt` file for known vulnerabilities using the `safety` tool. If `requirements.txt` is not found, it will attempt to run `pipo scan` first.

**Arguments:**

*   `path`: The path to the Python project directory (defaults to current directory).

**Usage Examples:**

```bash
# Scan the current directory for vulnerabilities
pipo security-scan

# Scan a specific project directory
pipo security-scan /path/to/my_project
```

### `pipo helm-chart [chart_name] [path]`

Generates a basic Helm chart structure for a Kubernetes application.

**Arguments:**

*   `chart_name`: The name of the Helm chart to create.
*   `path`: The path where the Helm chart will be generated (defaults to current directory).

**Usage Examples:**

```bash
# Generate a Helm chart named 'my-app-chart' in the current directory
pipo helm-chart my-app-chart

# Generate a Helm chart named 'another-app' in a specific directory
pipo helm-chart another-app /path/to/charts
```

### `pipo sast [path]`

Performs Static Application Security Testing (SAST) on the Python project directory using the [Bandit](https://bandit.readthedocs.io/en/latest/) tool.

**Arguments:**

*   `path`: The path to the Python project directory to scan (defaults to current directory).

**Usage Examples:**

```bash
# Perform SAST scan on the current directory
pipo sast

# Perform SAST scan on a specific project directory
pipo sast /path/to/my_project
```

### `pipo gitops-manifest [path] [--app-name APP_NAME] [--repo-url REPO_URL] [--path-in-repo PATH_IN_REPO] [--target-revision TARGET_REVISION] [--namespace NAMESPACE] [--tool {argocd,fluxcd}]`

Generates a basic GitOps manifest (e.g., Argo CD Application or Flux CD Kustomization).

**Arguments:**

*   `path`: The path to the project directory where the GitOps manifest will be generated (defaults to current directory).
*   `--app-name`: The name of the application for the GitOps manifest. Default is derived or prompted.
*   `--repo-url`: The URL of the Git repository containing the Kubernetes manifests.
*   `--path-in-repo`: The path within the repository to the Kubernetes manifests (defaults to '.').
*   `--target-revision`: The target Git revision (branch, tag, or commit SHA). Default is HEAD.
*   `--namespace`: The Kubernetes Namespace where the application will be deployed. Default is default.
*   `--tool`: The GitOps tool to generate manifest for (argocd or fluxcd). Default is argocd.

**Usage Examples:**

```bash
# Generate an Argo CD Application manifest interactively
pipo gitops-manifest

# Generate a Flux CD Kustomization manifest for a specific repo and path
pipo gitops-manifest --tool fluxcd --app-name my-flux-app --repo-url https://github.com/my-org/my-k8s-repo.git --path-in-repo ./deploy/prod --target-revision main --namespace production
```

## Mendapatkan Bantuan
```
