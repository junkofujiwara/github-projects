"""Export GitHub project information"""

import json
import logging
import os
from util.github import GitHub
from util.comon import Common

def export_github_project(organization, auth_token):
    '''Export GitHub project information'''
    os.makedirs(Common.FOLDER_PATH, exist_ok=True)
    os.makedirs(Common.FOLDER_FIELDS_PATH, exist_ok=True)
    os.makedirs(Common.FOLDER_VIEWS_PATH, exist_ok=True)
    os.makedirs(Common.FOLDER_ITEM_PATH, exist_ok=True)

    github = GitHub(organization, auth_token)
    projects = github.get_projects()
    for project in projects:
        logging.info('Project ID: %s', project.project_id)

        file_path = os.path.join(Common.FOLDER_PATH, f"{project.project_id}.json")
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(project.project_meta, file, indent=4)
        file_path_fields = os.path.join(Common.FOLDER_FIELDS_PATH, f"{project.project_id}.json")
        with open(file_path_fields, 'w', encoding='utf-8') as file:
            json.dump(project.fields, file, indent=4)
        file_path_views = os.path.join(Common.FOLDER_VIEWS_PATH, f"{project.project_id}.json")
        with open(file_path_views, 'w', encoding='utf-8') as file:
            json.dump(project.views, file, indent=4)
        file_path_items = os.path.join(Common.FOLDER_ITEM_PATH, f"{project.project_id}.json")
        with open(file_path_items, 'w', encoding='utf-8') as file:
            json.dump(project.items, file, indent=4)

        fields = project.fields

    return fields

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

    export_github_project(org, token)
                    