```
   / \__
  (    @\_____
  /         O
 /   (_____/  
/_____/   U   
```

# MinPin

MinPin is a command-line tool that automatically adds minimum version pins from the `conda list` and `pip list` output to the unpinned packages in conda YAML files, such as `environment.yml` or `anaconda-project.yml`.

## Features

- Parses `conda list` and `pip list` outputs to retrieve installed package versions.
- Updates YAML files by adding minimum version pins to unpinned packages (and skips already pinned packed).
- Handles both conda and pip dependencies.
- Preserves the original structure and comments of the YAML file.

## Installation

```bash
pip install minpin
```

## Usage
Activate your environment and then run:

```bash
minpin <path/to/environment.yml or anaconda-project.yml>
```

## Example Input/Output

**Input: original `environment.yml`**

```yaml
channels:
  - conda-forge
dependencies:
  - python=3.10 # blah blah
  - numpy # blah
  - pandas>=1.3
  - pip
  - pip:
      - requests
      - flask
```

**Output: Updated `environment.yml`**
```yaml
channels:
  - conda-forge
dependencies:
  - python=3.10 # blah blah
  - numpy>=1.24.0 # auto min pinned 2024-11-18 # blah
  - pandas>=1.3
  - pip
  - pip:
      - requests>=2.28.2 # auto min pinned 2024-11-18
      - flask>=2.2.3 # auto min pinned 2024-11-18
```

