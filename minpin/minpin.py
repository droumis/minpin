import argparse
import re
import subprocess
from datetime import datetime

def get_conda_list(conda_list_file=None):
    """
    Retrieves the output of `conda list` and returns it as a dictionary of package versions.
    """
    package_versions = {}
    if conda_list_file is None:
        print("No conda list file provided; generating 'conda list' output...")
        result = subprocess.run(['conda', 'list'], stdout=subprocess.PIPE, text=True, check=True)
        conda_list_lines = result.stdout.splitlines()
    else:
        with open(conda_list_file, 'r') as f:
            conda_list_lines = f.readlines()
    for line in conda_list_lines:
        if not line.strip() or line.startswith("#"):
            continue
        parts = re.split(r"\s+", line.strip())
        if len(parts) >= 2:
            name, version = parts[0], parts[1]
            package_versions[name.lower()] = version
    return package_versions

def get_pip_list():
    """
    Retrieves the output of `pip list` and returns it as a dictionary of package versions.
    """
    package_versions = {}
    result = subprocess.run(['pip', 'list', '--format=freeze'], stdout=subprocess.PIPE, text=True, check=True)
    pip_list_lines = result.stdout.strip().split('\n')
    for line in pip_list_lines:
        if '==' in line:
            name, version = line.strip().split('==')
            package_versions[name.lower()] = version
    return package_versions

def pin_package(package_line, package_versions, today):
    """
    Add a minimum pin to the package if unpinned.
    """
    # Split off any inline comment
    if '#' in package_line:
        package_spec, comment = package_line.split('#', 1)
        comment = '#' + comment
    else:
        package_spec = package_line
        comment = ''

    package_spec = package_spec.strip()
    comment = comment.strip()

    # Match package names with optional extras and version specifiers
    match = re.match(r'^([a-zA-Z0-9_\-\[\]]+)([=<>!~]{1,2}.*)?$', package_spec)
    if match:
        name_with_extras, pin = match.groups()
        base_name = name_with_extras.split('[')[0].lower()
        if base_name in package_versions:
            version = package_versions[base_name]
            if not pin:
                # Add pin
                new_line = f"{name_with_extras}>={version}"
                new_comment = f"# auto min pinned {today}"
                if comment:
                    new_comment += f" {comment}"
                return new_line + ' ' + new_comment, "Pinned"
            elif version not in pin:
                # Version mismatch
                return package_line, f"Mismatch (existing pin: {pin}, current: {version})"
            else:
                # Already pinned correctly
                return package_line, "Already pinned"
        else:
            return package_line, "Skipped (not found in conda/pip list)"
    else:
        return package_line, "Skipped (invalid format)"

def update_yaml_file(yaml_file, package_versions):
    """
    Updates the YAML file by adding minimum version pins to unpinned packages.
    """
    today = datetime.now().strftime('%Y-%m-%d')

    with open(yaml_file, 'r') as f:
        lines = f.readlines()

    in_packages_section = False
    in_pip_section = False
    updated_lines = []
    changes = []

    for idx, line in enumerate(lines):
        stripped_line = line.strip()

        # Check if we are entering the packages or dependencies section
        if stripped_line.startswith('packages:') or stripped_line.startswith('dependencies:'):
            in_packages_section = True
            in_pip_section = False
            updated_lines.append(line)
            continue

        # Check if we are entering a pip subsection
        if in_packages_section and ('- pip' in stripped_line or stripped_line == 'pip:'):
            in_pip_section = True
            updated_lines.append(line)
            continue

        # Check if we are leaving the packages section
        if in_packages_section and not line.startswith((' ', '-', '\t')) and not stripped_line.startswith('#'):
            in_packages_section = False
            in_pip_section = False

        # Process package lines
        if (in_packages_section or in_pip_section) and stripped_line.startswith('- '):
            pkg_line = line.lstrip('- ').rstrip('\n')
            pinned_line, status = pin_package(pkg_line, package_versions, today)
            changes.append((pkg_line.strip(), status))
            indent = line[:line.index('-')]
            updated_lines.append(f"{indent}- {pinned_line}\n")
            continue

        updated_lines.append(line)

    with open(yaml_file, 'w') as f:
        f.writelines(updated_lines)

    # Print the summary
    print("\n=== Summary of Changes ===")
    print(f"{'Package':<60} {'Status'}")
    print("-" * 80)
    for pkg, status in changes:
        print(f"{pkg:<60} {status}")

def main(args=None):
    import argparse

    parser = argparse.ArgumentParser(description="Add minimum pins to unpinned packages in a YAML file.")
    parser.add_argument('yaml_file', help="Path to the YAML file (anaconda-project.yml or environment.yml).")
    parser.add_argument('--conda-list', help="Path to a saved 'conda list' output file.")
    parsed_args = parser.parse_args(args)

    package_versions = get_conda_list(parsed_args.conda_list)
    pip_package_versions = get_pip_list()
    package_versions.update(pip_package_versions)
    update_yaml_file(parsed_args.yaml_file, package_versions)

if __name__ == "__main__":
    main()

