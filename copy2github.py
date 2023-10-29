from getpass import getpass
import os
import requests
import subprocess
import sys
import yaml

def get_github_token():
    config_path = os.getenv("PERSONAL_CONFIG")
    if config_path:
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            github_token = config.get("Github Key")
            if github_token:
                return github_token
        except FileNotFoundError:
            print(f"Config file not found at {config_path}")
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")

    return getpass("Enter your GitHub token: ")


def is_git_repo(path):
    return os.path.isdir(os.path.join(path, ".git"))


def github_repo_exists(token, repo_name):
    url = f"https://api.github.com/repos/<username>/{repo_name}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)
    return response.status_code == 200


def create_github_repo(token, name, description=""):
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "name": name,
        "description": description,
        "private": False,
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        print(f"Repository {name} created successfully on GitHub.")
        return response.json()["clone_url"]
    else:
        print(f"Failed to create repository {name}. Status code: {response.status_code}")
        print("Response:", response.json())
        return None


def push_local_repo_to_github(repo_path, github_url):
    os.chdir(repo_path)
    if not os.path.exists(".git"):
        subprocess.run(["git", "init"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Initial commit"])
    subprocess.run(["git", "branch", "-M", "main"])
    subprocess.run(["git", "remote", "add", "origin", github_url])
    subprocess.run(["git", "push", "-u", "origin", "main"])

def main():
    if len(sys.argv) != 2:
        print("Usage: python copy2github.py <source code base dir>")
        print("Can read 'Github Key' from env var PERSONAL_CONFIG")
        sys.exit(1)

    github_token = get_github_token()
    directory = sys.argv[1]
    if directory == ".":
        directory = os.getcwd()

    for project in os.listdir(directory):
        project_path = os.path.join(directory, project)
        if os.path.isdir(project_path):
            if is_git_repo(project_path) and github_repo_exists(github_token, project):
                print(f"\n{project} has already been processed. Skipping.")
            else:
                print(f"\nProcessing {project}...")
                github_url = create_github_repo(github_token, project)
                if github_url:
                    push_local_repo_to_github(project_path, github_url)
                else:
                    print(f"Failed to process {project}. It might already exist on GitHub.")

if __name__ == "__main__":
    main()

