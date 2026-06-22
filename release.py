#!/usr/bin/env python3
import sys
import os
import re
import subprocess

def run_command(command):
    """Executes a shell command and returns the output."""
    print(f"Executing: {command}")
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip()

def bump_init_version(init_file_path, part):
    """Reads __init__.py, increments the version string, and writes it back."""
    if not os.path.exists(init_file_path):
        print(f"❌ Error: {init_file_path} not found.")
        sys.exit(1)

    with open(init_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to precisely catch __version__ = "x.y.z"
    version_pattern = r'__version__\s*=\s*"(\d+)\.(\d+)\.(\d+)"'
    match = re.search(version_pattern, content)

    if not match:
        print(f"❌ Error: Could not find a valid __version__ string in {init_file_path}.")
        sys.exit(1)

    major, minor, patch = map(int, match.groups())

    # Increment the version based on selection
    if part == "major":
        major += 1; minor = 0; patch = 0
    elif part == "minor":
        minor += 1; patch = 0
    elif part == "patch":
        patch += 1

    new_version = f"{major}.{minor}.{patch}"

    # Replace the old version with the new one
    new_content = re.sub(version_pattern, f'__version__ = "{new_version}"', content)

    with open(init_file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return new_version

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ["major", "minor", "patch"]:
        print("Usage: python release.py [major|minor|patch]")
        sys.exit(1)

    bump_type = sys.argv[1]
    init_path = "cangling/__init__.py"

    # 1. Bump the version directly in cangling/__init__.py
    new_version = bump_init_version(init_path, bump_type)
    print(f"🔄 Source code version bumped to {new_version}")

    # 2. Git Workflow
    try:
        print("🚀 Starting Git workflow...")
        # Since pyproject.toml reads dynamically, we only need to track the __init__.py modification!
        run_command(f"git add {init_path}")
        run_command(f'git commit -m "chore: release version {new_version}"')
        run_command(f"git tag v{new_version}")

        print("📤 Pushing changes to GitHub (main branch and tags)...")
        run_command("git push origin main")
        run_command("git push origin --tags")

        print(f"\n🎉 Successfully released v{new_version}!")
        print("GitHub Actions will now take over to publish to Nexus/PyPI.")
        
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()