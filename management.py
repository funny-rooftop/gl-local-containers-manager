"""
Author: Alexey Belyaev
Github: github.com/funny-rooftop

Gitlab container registry management tool, which sync local gitlab registry with docker hub.
"""

import subprocess
import yaml
import sys
import requests
import logging

# Function to retrieve Docker images from GitLab Container Registry
def get_gitlab_registry_images(gitlab_url: str, gitlab_token: str, gitlab_project_id: int) -> list[str]:
    headers = {"PRIVATE-TOKEN": gitlab_token}
    url = f"{gitlab_url}/api/v4/projects/{gitlab_project_id}/registry/repositories"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  

        repositories = response.json()

        image_names_with_tags = []
        for repository in repositories:
            tags_url = f"{gitlab_url}/api/v4/projects/{gitlab_project_id}/registry/repositories/{repository['id']}/tags"
            tags_response = requests.get(tags_url, headers=headers)
            tags_response.raise_for_status()

            tags = tags_response.json()
            for tag in tags:
                image_names_with_tags.append(f"{repository['name']}:{tag['name']}")

        for image_name_with_tag in image_names_with_tags:
            print(image_name_with_tag)

        return image_names_with_tags

    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve images from GitLab Container Registry: {e}")
        sys.exit(1)

# Function to download Docker image to local registry
def download_image(name, tag):
    print(f"Downloading image: {name}:{tag}")
    subprocess.run(["docker", "pull", f"{name}:{tag}"])

# Function to upload Docker image to GitLab Container Registry
def upload_to_gitlab_registry(name, tag, registry_url):
    print(f"Uploading image {name}:{tag} to GitLab Container Registry")
    subprocess.run(["docker", "tag", f"{name}:{tag}", f"{registry_url}/{name}:{tag}"])
    subprocess.run(["docker", "push", f"{registry_url}/{name}:{tag}"])

# Function to delete Docker image from local registry
def delete_image(name, tag):
    print(f"Deleting image: {name}:{tag}")
    subprocess.run(["docker", "rmi", f"{name}:{tag}"])

# Function to delete Docker image from GitLab Container Registry
def delete_from_gitlab_registry(gitlab_url: str, gitlab_token: str, gitlab_project_id: int, name: str, tag: str):
    headers = {"PRIVATE-TOKEN": gitlab_token}
    url = f"{gitlab_url}/api/v4/projects/{gitlab_project_id}/registry/repositories"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        repositories = response.json()

        for repository in repositories:
            repository_name = repository["name"]
            if repository_name == name:
                repository_id = repository["id"]
                tags_url = f"{gitlab_url}/api/v4/projects/{gitlab_project_id}/registry/repositories/{repository_id}/tags"
                tags_response = requests.get(tags_url, headers=headers)
                tags_response.raise_for_status()

                tags = tags_response.json()
                for tag_data in tags:
                    if tag_data["name"] == tag:
                        delete_url = f"{gitlab_url}/api/v4/projects/{gitlab_project_id}/registry/repositories/{repository_id}/tags/{tag_data['name']}"
                        delete_response = requests.delete(delete_url, headers=headers)
                        delete_response.raise_for_status()
                        print(f"Tag {repository_name}:{tag} deleted successfully.")
                        return

        print(f"Tag {name}:{tag} not found in GitLab Container Registry.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to delete tag {name}:{tag}: {e}")
        sys.exit(1)

def main(gitlab_url, gitlab_token, gitlab_project_id, registry_url):
    # Load images data from YAML file
    with open("images.yaml", "r") as file:
        images_data = yaml.safe_load(file)

    # Retrieve and show images from GitLab Container Registry
    gitlab_registry_images = get_gitlab_registry_images(gitlab_url, gitlab_token, gitlab_project_id)
    
    print("Images in GitLab Container Registry:")
    for image in gitlab_registry_images:
        print(image)

    images_to_upload = [] 

    # Check images to upload
    for image_data in images_data:
        name = image_data.get("name")
        tags = image_data.get("tags")

        for tag in tags:
            image = f"{name}:{tag}"
            if image not in gitlab_registry_images:
                images_to_upload.append((name, tag)) 

    # Download, upload, and synchronize images
    for name, tag in images_to_upload:
        print(f"Downloading image: {name}:{tag}")
        download_image(name, tag)
        print(f"Uploading image {name}:{tag} to GitLab Container Registry")
        upload_to_gitlab_registry(name, tag, registry_url)

        gitlab_registry_images.append(f"{name}:{tag}")
     
    # Delete images not in YAML file
    for registry_image in gitlab_registry_images:
        name, tag = registry_image.split(":")
        if any(name in image_data.get("name") and tag in image_data.get("tags") for image_data in images_data):
            continue
        print(f"Deleting image {registry_image} from GitLab Container Registry")
        delete_from_gitlab_registry(gitlab_url, gitlab_token, gitlab_project_id, name, tag)

    print("All images have been synchronized with GitLab Container Registry.")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python management.py GITLAB_URL GITLAB_TOKEN GITLAB_PROJECT_ID REGISTRY_URL")
        sys.exit(1)

    gitlab_url = sys.argv[1]
    gitlab_token = sys.argv[2]
    gitlab_project_id = sys.argv[3]
    registry_url = sys.argv[4]
    
    logging.basicConfig(level=logging.DEBUG)

    main(gitlab_url, gitlab_token, gitlab_project_id, registry_url)
