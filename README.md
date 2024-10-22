# GitHub Project Operation

## Requirements
- Python
    ```bash
    $ pip install -r requirements.txt
    ```

## Export

### Usage
    
    ```bash
    $ export GITHUB_TOKEN=your_token
    $ export GITHUB_ORG=your_org_name

    $ python export.py
    ```

### Output - Project Info
All json files are exported to the "output" folder.
Json file name is Project ID.
- "projects" folder: Project information in json format
- "projects_fields" folder: Project fields information in json format
- "projects_views" folder: Project views information in json format
- "project_items" folder: Project items information in json format

### Log
export.log

## Import
### Usage
    
    ```bash
    $ export GITHUB_TOKEN_TARGET=your_token
    $ export GITHUB_ORG_TARGET=your_org_name

    $ python import.py
    ```
### Input - Project Info
All json files are imported from the "input" folder.
Json file name is Project ID.
- "projects" folder: Project information in json format

### Log
import.log

### Note
Projects are imported based on the Project Name, which may result in duplicate projects. Ensure that the execution is performed on an empty organization.
