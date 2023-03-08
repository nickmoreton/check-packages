# Check a local repo for versions of python package dependencies

## Setup

1. Clone this repo
2. Create a virtual environment
3. Install the package requirements

```bash
pip install -r requirements.txt
```

4. Copy the example settings file

```
cp example.settings.py settings.py
```

I settings.py update `BASE_SITES_DIR` and `DEPENDENCIES`

## Run the tool

```bash
python check.py
```

and follow the on screen instructions.

Your should see a colorised report of the dependencies current version and the latest version from pypi.

## Known strange behavior

Git dependencies will show a warning

Dependencies with extra will show a warning
