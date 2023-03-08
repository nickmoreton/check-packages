import click
import requests

from settings import LIMIT_DEPENDENCIES, SITES_DIRECTORY


@click.command()
@click.option(
    "--directory-name", prompt="The folder name of the repo", help="Repo folder name"
)
@click.option(
    "--dependency-file",
    default="pyproject.toml",
    help="The name of the dependency file",
    prompt="Dependency file name",
)
def check(directory_name, dependency_file):
    """Check a repo for a wagtail dependencies"""
    click.echo(f"Directory is: {directory_name}")
    click.echo(f"Dependency file is: {dependency_file}")
    click.echo("")
    click.echo("Checking for wagtail dependencies")
    click.echo("=================================")

    deps = get_dependencies(directory_name, dependency_file)

    deps_tuples = tupleator(deps)

    deps_dict, errors = get_dict(deps_tuples)

    if not deps_dict:
        click.echo("No dependencies found")
        return
    report(deps_dict)

    if errors:
        click.echo("")
        click.echo("Errors")
        click.echo("======")
        for error in errors:
            click.echo(click.style(error, fg="red"))


def get_dict(deps_tuples):
    deps_dict = {}
    errors = []
    with click.progressbar(deps_tuples, label="Checking versions") as deps_tuples:
        for dep in deps_tuples:
            name = dep[0]
            resp = requests.get(f"https://pypi.org/pypi/{name}/json")
            if resp.status_code != 200:
                errors.append((f"Cannot parse: {resp.status_code} {dep}"))
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

    return deps_dict, errors


def tupleator(deps):
    deps_tuples = []
    for dep in deps:
        parts = dep.split("=", maxsplit=1)
        name = parts[0].strip().strip('"')
        version = parts[1].strip().strip('"')
        deps_tuples.append((name, version))
    return deps_tuples


def get_dependencies(directory_name, dependency_file):
    deps = []
    with open(SITES_DIRECTORY / directory_name / dependency_file) as f:
        for line in f:
            text = line.strip()
            if (
                not text.startswith("#") and not text.startswith("-e") and text
            ):  # avoid parsing comments
                for dependency in LIMIT_DEPENDENCIES:
                    if dependency in text:
                        deps.append(
                            text.replace("==", "=")
                        )  # when used in a requirements file
    deps.sort()
    return deps


def report(deps_dict):
    warning_color = "yellow"
    critical_color = "red"
    for name, info in deps_dict.items():
        if info["current_version"].startswith("{git = "):
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
                f"{name}: {info['current_version']} <- {info['latest_version']}",
            ),


if __name__ == "__main__":
    check()
