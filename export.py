"""Export GitHub project information"""

import json
import logging
import os
from util.github import GitHub
from util.comon import Common

def create_directories():
    '''Create necessary directories'''
    os.makedirs(Common.FOLDER_PATH, exist_ok=True)
    os.makedirs(Common.FOLDER_FIELDS_PATH, exist_ok=True)
    os.makedirs(Common.FOLDER_VIEWS_PATH, exist_ok=True)
    os.makedirs(Common.FOLDER_ITEM_PATH, exist_ok=True)

def export_github_project(organization, auth_token):
    '''Export GitHub project information'''

    github = GitHub(organization, auth_token)
    include_items = False
    projects = github.get_projects(include_items)
    
    for project in projects:
        logging.info('Project ID: %s', project.project_id)

        Common.write_json_to_file(os.path.join(Common.FOLDER_PATH, f"{project.project_id}.json"), project.project_meta)
        Common.write_json_to_file(os.path.join(Common.FOLDER_FIELDS_PATH, f"{project.project_id}.json"), project.fields)
        Common.write_json_to_file(os.path.join(Common.FOLDER_VIEWS_PATH, f"{project.project_id}.json"), project.views)
        
        if include_items:
            Common.write_json_to_file(os.path.join(Common.FOLDER_ITEM_PATH, f"{project.project_id}.json"), project.items)

    # Export project items separately
    if not include_items:
        json_files = Common.get_json_files(Common.FOLDER_PATH)
        for json_file in json_files:
            project_id = json_file.split('.')[0]
            project = github.get_single_project(project_id)
            Common.write_json_to_file(os.path.join(Common.FOLDER_ITEM_PATH, f"{project_id}.json"), project.items)

    return len(projects)

if __name__ == '__main__':
    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s [%(levelname)s] %(message)s",
        handlers = [
            logging.FileHandler("export.log"),
            logging.StreamHandler()
        ])
    org = os.environ['GITHUB_ORG']
    token = os.environ['GITHUB_TOKEN']

    if not org:
        raise KeyError("The 'GITHUB_ORG' environment variable is missing.")
    if not token:
        raise KeyError("The 'GITHUB_TOKEN' environment variable is missing.")

    create_directories()
    count = export_github_project(org, token)
    logging.info('Exported %d projects', count)
                    