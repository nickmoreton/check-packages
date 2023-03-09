import os
from pathlib import Path

import click
import requests
import requirements
import tomli
from dotenv import load_dotenv

load_dotenv()


@click.command()
@click.option(
    "--directory-name",
    prompt="The directory name of the repo",
    help="Repo folder name",
)
@click.option(
    "--dependency-file",
    default=lambda: os.getenv("FILE_NAME", ""),
    help="The name of the dependency file",
    prompt="Dependency file name",
)
@click.option(
    "--limit-packages",
    default=lambda: os.getenv("LIMIT_PACKAGES", ""),
    help="Limit the packages to check",
    prompt="Limit packages checked = (begins with comparison)",
)
@click.option(
    "--sites-directory",
    default=lambda: os.getenv("SITES_DIR", ""),
    help="Directory of the repos",
    prompt="Sites directory",
)
def check(directory_name, dependency_file, limit_packages, sites_directory):
    """
    Check a local repo for package dependencies and possible updates

    Parses a dependency file and checks the current version against the latest version on pypi.org
    and outputs a report of the results.

    The dependency file can be either a requirements.txt or a pyproject.toml file.

    Options:
    =================

    limit-packages: option is a comma separated list of package names to check.

    sites-directory: option is the directory where the repos are stored.

    directory-name: option is the name of the folder where the repo is stored.

    dependency-file: option is the name of the dependency file.
    """
    if not directory_name or not dependency_file or not sites_directory:
        click.echo(
            click.style("Missing required arguments", fg="bright_red"),
        )
        return

    click.echo(f"Directory is: {directory_name}")
    click.echo(f"Dependency file is: {dependency_file}")
    click.echo("")
    click.echo("Checking for wagtail dependencies")
    click.echo("=================================")

    limit_packages = limit_packages.split(",")
    sites_directory = Path(sites_directory)

    if dependency_file.endswith(".txt"):
        deps = get_dependencies_txt(
            directory_name, dependency_file, limit_packages, sites_directory
        )
    elif dependency_file.endswith(".toml"):
        deps = get_dependencies_toml(
            directory_name, dependency_file, limit_packages, sites_directory
        )

    deps_tuples = tupleator(deps)

    deps_dict, messages = get_dict(deps_tuples)

    if not deps_dict:
        click.echo("No dependencies found")
        return
    report(deps_dict)

    if messages:
        click.echo("")
        click.echo("Messages")
        click.echo("========")
        for message in messages:
            click.echo(
                click.style(message, fg="cyan"),
            )


def get_dependencies_toml(
    directory_name, dependency_file, limit_packages, sites_directory
):
    deps = []
    with open(sites_directory / directory_name / dependency_file, "rb") as f:
        data = tomli.load(f)
        dependencies = data["tool"]["poetry"]["dependencies"]
        dev_dependencies = data["tool"]["poetry"]["dev-dependencies"]

        for key, value in dependencies.items():
            text = f"{key}={value}"
            if limit_packages:
                for starts in limit_packages:
                    if text.startswith(starts):
                        deps.append(text.lower())
            else:
                deps.append(text.lower())

        for key, value in dev_dependencies.items():
            text = f"{key}={value}"
            if limit_packages:
                for starts in limit_packages:
                    if text.startswith(starts):
                        deps.append(text.lower())
            else:
                deps.append(text.lower())

    return sorted(deps)


def get_dependencies_txt(
    directory_name, dependency_file, limit_packages, sites_directory
):
    deps = []
    with open(sites_directory / directory_name / dependency_file, "r") as f:
        for dep in requirements.parse(f):
            name = dep.name.lower()
            version = "".join(dep.specs[0]) if dep.specs else ""
            text = f"{name}={version}"

            if limit_packages:
                for starts in limit_packages:
                    if text.startswith(starts):
                        deps.append(text.lower())
            else:
                deps.append(text.lower())

    return sorted(deps)


def get_dict(deps_tuples):
    deps_dict = {}
    messages = []
    with click.progressbar(
        deps_tuples,
        label="Checking versions",
    ) as deps_tuples:
        for dep in deps_tuples:
            name = dep[0]
            resp = requests.get(f"https://pypi.org/pypi/{name}/json")
            if resp.status_code != 200:
                messages.append((f"Cannot parse: {resp.status_code} {dep}"))
                continue
            info = resp.json().get("info").get("release_url")
            version = info.split("/")[-2]
            deps_dict[name] = {
                "current_version": dep[1]
                .strip("'")
                .strip("~")
                .strip("^")
                .strip(">=")
                .strip("<=")
                .strip("=="),
                "latest_version": version,
            }

    return deps_dict, messages


def tupleator(deps):
    deps_tuples = []
    for dep in deps:
        parts = dep.split("=", maxsplit=1)
        name = parts[0]
        version = parts[1]
        deps_tuples.append((name, version))
    return deps_tuples


def report(deps_dict):
    warning_color = "yellow"
    critical_color = "bright_red"
    success_color = "green"
    for name, info in deps_dict.items():
        if info["current_version"].startswith("{'git':"):
            click.echo(
                click.style(
                    f"{name}: {info['current_version']} <- {info['latest_version']}",
                    fg=critical_color,
                )
            )
        elif info["current_version"] != info["latest_version"]:
            click.echo(
                click.style(
                    f"{name}: {info['current_version']} <- {info['latest_version']}",
                    fg=warning_color,
                )
            )
        else:
            click.echo(
                click.style(
                    f"{name}: {info['current_version']} <- {info['latest_version']}",
                    fg=success_color,
                )
            ),


if __name__ == "__main__":
    check()
