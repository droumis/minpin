```
   / \__
  (    @\_____
  /         O
 /   (_____/  
/_____/   U   
```

# Min Pin

Min Pin is a command-line tool that automatically adds minimum version pins to unpinned packages in conda-friendly YAML files, such as `environment.yml` or `anaconda-project.yml`.

## Features

- Parses `conda list` and `pip list` to retrieve installed package versions.
- Updates YAML files by adding minimum version pins to unpinned packages.
- Handles both conda and pip dependencies.
- Preserves the original structure and comments of the YAML file.

## Installation

```bash
pip install minpin
```

## Usage

```bash
minpin ./environment.yml
```

Optionally, specify a conda list output file which you can create with `conda list > conda_list.txt`:

```bash
minpin anaconda-project.yml --conda-list conda_list.txt
```

## Example

**Input: original `environment.yml`**

```yaml
channels:
  - conda-forge
dependencies:
  - python=3.10
  - numpy
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
  - python=3.10
  - numpy>=1.24.0 # auto min pinned 2024-11-18
  - pandas>=1.3.3 # auto min pinned 2024-11-18
  - pip
  - pip:
      - requests>=2.28.2 # auto min pinned 2024-11-18
      - flask>=2.2.3 # auto min pinned 2024-11-18
```

