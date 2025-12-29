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

def bump_version(part):
    """Reads pyproject.toml, increments version, and writes it back."""
    if not os.path.exists("pyproject.toml"):
        print("❌ Error: pyproject.toml not found in current directory.")
        sys.exit(1)

    with open("pyproject.toml", "r") as f:
        content = f.read()

    # Regex to find version = "x.y.z"
    version_pattern = r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"'
    match = re.search(version_pattern, content)
    
    if not match:
        print("❌ Error: Could not find a valid version string in pyproject.toml.")
        sys.exit(1)

    major, minor, patch = map(int, match.groups())

    # Increment the version
    if part == "major":
        major += 1; minor = 0; patch = 0
    elif part == "minor":
        minor += 1; patch = 0
    elif part == "patch":
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    
    # Replace the old version with the new one
    new_content = re.sub(version_pattern, f'version = "{new_version}"', content)
    
    with open("pyproject.toml", "w") as f:
        f.write(new_content)
    
    return new_version

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ["major", "minor", "patch"]:
        print("Usage: python release.py [major|minor|patch]")
        sys.exit(1)

    bump_type = sys.argv[1]

    # 1. Bump the version in pyproject.toml
    new_version = bump_version(bump_type)
    print(f"✅ Version bumped to {new_version}")

    # 2. Git Workflow
    try:
        print("🚀 Starting Git workflow...")
        run_command("git add pyproject.toml")
        run_command(f'git commit -m "chore: release version {new_version}"')
        run_command(f"git tag v{new_version}")
        
        print("📤 Pushing to GitHub (main branch and tags)...")
        run_command("git push origin main")
        run_command("git push origin --tags")
        
        print(f"\n🎉 Successfully released v{new_version}!")
        print("GitHub Actions will now take over to publish to Nexus.")
        
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()