import os
import sys
import json
import time
import requests
import argparse

def find_package_json_files(root_dir):
    matches = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == "package.json":
                matches.append(os.path.join(dirpath, filename))
    return matches

def load_and_merge_json(file_paths):
    merged = []
    for path in file_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                merged.append({
                    "path": path,
                    "content": data
                })
        except Exception as e:
            print(f"Failed to read {path}: {e}")
    return merged

def load_json_file_direct(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON file: {e}")
        sys.exit(1)

def extract_dependencies(merged_packages):
    dep_names = set()
    for pkg in merged_packages:
        content = pkg.get("content", {}) if isinstance(pkg, dict) else pkg
        deps = content.get("dependencies", {})
        dev_deps = content.get("devDependencies", {})
        all_deps = {**deps, **dev_deps}
        for dep, version in all_deps.items():
            if not dep.startswith("@") and not str(version).startswith("npm:"):
                dep_names.add(dep)
    return sorted(dep_names)

def write_dependencies_file(dep_names, output_file="dependencies.txt"):
    with open(output_file, 'w', encoding='utf-8') as f:
        for name in dep_names:
            f.write(f"{name}\n")
    print(f"✅ {len(dep_names)} unique dependencies written to {output_file}")

def check_dependencies(dep_file, delay=0.5, output_file="not_found_dependencies.txt"):
    with open(dep_file, 'r', encoding='utf-8') as f:
        dependencies = [line.strip() for line in f if line.strip()]

    not_found = []
    total = len(dependencies)

    for i, dep in enumerate(dependencies, 1):
        print(f"[{i}/{total}] Checking: {dep}")
        url = f"https://registry.npmjs.com/{dep}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 404:
                print(f"[+] ❌ Not found: {dep}. Possible dependency confusion")
                not_found.append(dep)
        except requests.RequestException as e:
            print(f"⚠️ Error checking {dep}: {e}")
        time.sleep(delay)

    if not_found:
        with open(output_file, 'w', encoding='utf-8') as f:
            for dep in not_found:
                f.write(dep + '\n')
        print(f"\n🚨 Saved {len(not_found)} missing dependencies to {output_file}")
    else:
        print("\n✅ All dependencies were found in the npm registry.")

def main():
    parser = argparse.ArgumentParser(description="Dependency extraction and validation tool")
    parser.add_argument('--dir-path', type=str, help="Path to directory to search for package.json files")
    parser.add_argument('--json-file', type=str, help="Path to a single package.json file")
    parser.add_argument('--delay', type=float, default=0.5, help="Delay between HTTP requests in seconds (default: 0.5)")
    args = parser.parse_args()

    if not args.dir_path and not args.json_file:
        parser.error("You must provide either --dir-path or --json-file")
    if args.dir_path and args.json_file:
        parser.error("Please use only one of --dir-path or --json-file")

    if args.dir_path:
        print(f"🔍 Searching for package.json files in: {args.dir_path}")
        package_files = find_package_json_files(args.dir_path)
        if not package_files:
            print("No package.json files found.")
            sys.exit(0)
        merged_data = load_and_merge_json(package_files)

    else:
        print(f"📄 Using single package.json file: {args.json_file}")
        json_data = load_json_file_direct(args.json_file)
        merged_data = [{"content": json_data}]  # Wrap in list to match interface

    print("📦 Extracting dependencies...")
    dependencies = extract_dependencies(merged_data)

    print("📝 Writing dependencies.txt...")
    write_dependencies_file(dependencies, "dependencies.txt")

    print("🌐 Checking dependencies against npm registry...")
    check_dependencies("dependencies.txt", delay=args.delay)


if __name__ == "__main__":
    main()
