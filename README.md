# Check a local repo for used python packages

Parses a dependency file and checks the current defined version against the latest version on pypi.org and outputs a report of the results.
    
The dependency file can be either a `requirements.txt` or a `pyproject.toml` file.

## Setup

Clone this repo

```bash
git clone git@github.com:nickmoreton/check-packages.git
```

Make a copy of the .env.example file and update the values.

```
cp .env.example .env
```

Create a virtual environment and install the package requirements

```bash
pip install -r requirements.txt
```


## Running the tool

```bash
python check.py
```

and follow the on screen instructions.

Options: *You can add default values for some of the options in the .env file*
- `directory-name` -  is the name of the folder where the repo is stored.
- `dependency-file` -  is the name of the dependency file.
- `sites-directory` -  is the parent directory where the repos are stored.
- `limit-packages` -  is a comma separated list of package names to check (starts with comparison).

You should see a report of the dependencies current version and the latest version available from pypi.

The report has colour:
- Green: the package is defined to use the latest version available
- Yellow: the package is defined to use a version which is not the latest version available
- Red: the package is using a repo import rather than a PyPI package
