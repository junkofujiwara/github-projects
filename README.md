# GitHub Projects Operation

## Description
This script exports GitHub Projects information to a json file and imports it to another organization.
The following information is exported.
- Projects
- Project fields
- Project views
- Project items (with repository information and issue/PR number)
    - Issue
    - Pull Request
Import project script only generates a new project. It does not import fields, views, issues, pull requests, or other project items.

## Requirements
- Python
    ```bash
    $ pip install -r requirements.txt
    ```

## Export

### Overview
export.py exports the project information of the specified organization to a json file.

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
- "projects_items" folder: Project items information in json format

### Log
export.log

## Import (Create Project)

### Overview
import.py with create-projects option generates a new project based on the exported project information.

### Usage
    
    ```bash
    $ export GITHUB_TOKEN_TARGET=your_token
    $ export GITHUB_ORG_TARGET=your_org_name

    $ python import.py -o create-projects
    ```
### Input - Project Info
- All json files are imported from the "input" folder.
- Json file name is Project ID.
- "projects" folder: Project information in json format

### Log
- import.log
- project_mapping.log

### Note
Projects are imported based on the Project Name, which may result in duplicate projects. Ensure that the execution is performed on an empty organization.

## Import (Insert Items)

### Overview
import.py with insert-items inserts existing items (Issues/PRs) into the existing project based on the exported project information.

### Usage
    
    ```bash
    $ export GITHUB_TOKEN_TARGET=your_token
    $ export GITHUB_ORG_TARGET=your_org_name

    $ python import.py -o insert-items
    ```
### Input - Project Info
- All json files are imported from the "input" folder.
- Json file name is Project ID.
- "projects_items" folder: Project information in json format

### Log
import.log
project_item_mapping.log

