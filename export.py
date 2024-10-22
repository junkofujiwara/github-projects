# export github project information

import json
import logging
import os
from util.github import GitHub

def export_github_project(org, token):
    '''Export GitHub project information'''
    folder_path = "projects"
    folder_path_fields = "projects_fields"
    folder_path_views = "projects_views"
    folder_path_items = "projects_items"

    os.makedirs(folder_path, exist_ok=True)
    os.makedirs(folder_path_fields, exist_ok=True)
    os.makedirs(folder_path_views, exist_ok=True)
    os.makedirs(folder_path_items, exist_ok=True)

    github = GitHub(org, token)
    projects = github.get_projects()
    for project in projects:
        logging.info('Project ID: %s', project.project_id)
        
        file_path = os.path.join(folder_path, f"{project.project_id}.json")
        with open(file_path, 'w') as file:
            json.dump(project.project_meta, file, indent=4)
        file_path_fields = os.path.join(folder_path_fields, f"{project.project_id}.json")
        with open(file_path_fields, 'w') as file:
            json.dump(project.fields, file, indent=4)
        file_path_views = os.path.join(folder_path_views, f"{project.project_id}.json")
        with open(file_path_views, 'w') as file:
            json.dump(project.views, file, indent=4)
        file_path_items = os.path.join(folder_path_items, f"{project.project_id}.json")
        with open(file_path_items, 'w') as file:
            json.dump(project.items, file, indent=4)
        
    return project.fields

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


                                      