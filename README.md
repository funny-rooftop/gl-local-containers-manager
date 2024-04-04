
# Local Gitlab container registry manager
##### gl-local-containers-manager
Gitlab container registry management tool, which sync local gitlab registry with docker hub.

### Features
- **Download Images:** Downloads Docker images from a specified Docker registry.
- **Upload Images:** Uploads Docker images to the GitLab Container Registry.
- **Delete Images:** Deletes Docker images from the GitLab Container Registry.
- **YAML Configuration:** Utilizes a YAML file to define the images and tags to be synchronized.

### Prerequisites
Before running the script, ensure you have the following:

-   Python 3.x installed on your system.
-   Docker installed and running.
-   GitLab account and access token with the appropriate permissions to interact with the GitLab Container Registry.
-   Access to the Docker registry you want to synchronize with GitLab Container Registry.

### Usage
- 1. Clone this repository to your local machine.
    ```bash
    `git clone https://github.com/funny_rooftop/gl-local-containers-manager`
    ```
-  2. Navigate to the project directory.
    ```bash
    `cd gl-local-containers-manager`
    ```
-  3. Install the required Python dependencies.
     ```bash
   `pip install -r requirements.txt`
   ```    
-  4. Create a YAML file named `images.yaml` in the project directory to define the images and tags to synchronize. Below is an example format:
    ```yaml
    - name: image
      tags:
        - "tag-1"
        - "tag-2"
        - "tag-3"

    - name: dockerhub-user/image
      tags:
        - "latest"
        - "teg-2"
        - "1.20"
    ```
-   5. Run the script with the required arguments:
     ```bash
    `python management.py GITLAB_URL GITLAB_TOKEN GITLAB_PROJECT_ID REGISTRY_URL`
      ```
      
    Replace `GITLAB_URL`, `GITLAB_TOKEN`, `GITLAB_PROJECT_ID`, and `REGISTRY_URL` with your GitLab URL, GitLab access token, GitLab project ID, and Docker registry URL, respectively.
    
-  6. Follow the prompts to synchronize the Docker images with the GitLab Container Registry.


