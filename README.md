# GitHub Projects Operation

## Description
This script exports GitHub Projects information to a json file and imports it to another organization.
The following information is exported.
- Projects
- Project fields
- Project views
- Project items (with repository information and issue/PR number)
    - Draft Issue
    - Issue
    - Pull Request

## Requirements
- Python
    ```bash
    $ pip install -r requirements.txt
    ```

## Sample Scenario
Organization project migration scenario. 
<br>(Assumes that repositories and their contents already exist. Manual steps are required due to API limitations)
- Execute Export (-o all | -o projects & -o fields & -o views & -o items)
- Execute Import -o projects
- Execute Import -o fields
- Add Views & missing fields
- Execute Import -o insert-items
  
---
## Export

### Overview
export.py exports the project information of the specified organization to a json file.

### Usage
    
    ```bash
    $ export GITHUB_TOKEN=your_token
    $ export GITHUB_ORG=your_org_name

    $ python export.py -o all
    or
    $ python export.py -o projects
    $ python export.py -o fields
    $ python export.py -o views
    $ python export.py -o items
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
import.py with projects option generates new projects based on the exported project information.

### Usage
    
    ```bash
    $ export GITHUB_TOKEN_TARGET=your_token
    $ export GITHUB_ORG_TARGET=your_org_name

    $ python import.py -o projects
    ```
### Input - Project Info
- All json files are imported from the "input" folder.
- Json file name is Project ID.
- "projects" folder: Project information in json format

### Log
- import.log
- project_mapping.log

project_mapping.log format;<br>
`project_id -> mapped_project_id`

### Note
Projects are imported based on the Project Name, which may result in duplicate projects. Ensure that the execution is performed on an empty organization.

## Import (Create Fields)

### Overview
import.py with fields creates fields in the existing project based on the exported project information.

### Usage
    
    ```bash
    $ export GITHUB_TOKEN_TARGET=your_token
    $ export GITHUB_ORG_TARGET=your_org_name

    $ python import.py -o fields
    ```
### Input - Project Info
- All json files are imported from the "input" folder.
- Json file name is Project ID.
- "projects_fields" folder: Project information in json format

### Log
- import.log

### Note
- If there is existing field with the same name, it will not be created.
- Iteration type of fields is not supported due to API limitation.

## Import (Insert Items)

### Overview
import.py with items inserts existing items (Issues/PRs) into the existing project based on the exported project information.

### Usage
    
    ```bash
    $ export GITHUB_TOKEN_TARGET=your_token
    $ export GITHUB_ORG_TARGET=your_org_name

    $ python import.py -o items
    ```
### Input - Project Info
- All json files are imported from the "input" folder.
- Json file name is Project ID.
- "projects_items" folder: Project information in json format

### Log
- import.log
- project_item_mapping.log

project_item_mapping.log format;<br>
`repository_name,issue-pr_number, project_item_id -> mapped_project_item_id`

### Note
- If there is no repository or issue/PR in the target organization, the item is not inserted.
- If a draft item with the same name already exists in the target project, it will not be inserted.
- Draft item Ids are not listed in project_item_mapping.log.

## Check Utility

### Overview
Utility to check the information in the source and target projects.

### Type of Check
- check-item-source: Count number of items in the source organization-projects.
- check-item-target: Count number of items in the target organization-projects.

### Usage
    
    ```bash
    $ export GITHUB_TOKEN=your_token
    $ export GITHUB_ORG=your_org_name
    $ export GITHUB_TOKEN_TARGET=your_token
    $ export GITHUB_ORG_TARGET=your_org_name

    $ python check.py -o check-item-source
    or
    $ python check.py -o check-item-target
    ```
### Input
- "projects" folder: Project information in json format (check-item-source/check-item-target)
- "project_mapping.log": Project ID mapping information (check-item-target)

### Log
- check.log
