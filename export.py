"""Export GitHub project information"""
import argparse
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

def export_github_projects(organization, auth_token, include_all):
    '''Export GitHub project information'''

    github = GitHub(organization, auth_token)
    projects = github.get_projects(include_all)

    for project in projects:
        logging.info('Project ID: %s', project.project_id)
        Common.write_json_to_file(os.path.join(Common.FOLDER_PATH,
                                               f"{project.project_id}.json"), project.project_meta)
        if include_all:
            Common.write_json_to_file(os.path.join(Common.FOLDER_FIELDS_PATH,
                                                   f"{project.project_id}.json"), project.fields)
            Common.write_json_to_file(os.path.join(Common.FOLDER_VIEWS_PATH,
                                                   f"{project.project_id}.json"), project.views)
            Common.write_json_to_file(os.path.join(Common.FOLDER_ITEM_PATH,
                                                   f"{project.project_id}.json"), project.items)

def export_github_project_data(organization, auth_token, data_type, folder_path):
    '''Export GitHub project data based on type'''

    # check if Project folder exists
    if not os.path.exists(Common.FOLDER_PATH):
        logging.error("Folder %s does not exist", Common.FOLDER_PATH)
        return

    # get project items from the project id from json files
    github = GitHub(organization, auth_token)
    project_ids = Common.project_id_list(Common.FOLDER_PATH)
    for project_id in project_ids:
        if data_type == 'fields':
            project = github.fetch_project_fields(project_id)
            data = project.fields
        elif data_type == 'views':
            project = github.fetch_project_views(project_id)
            data = project.views
        elif data_type == 'items':
            project = github.fetch_project_items(project_id)
            data = project.items
        else:
            raise ValueError(f"Unknown data type: {data_type}")

        Common.write_json_to_file(os.path.join(folder_path, f"{project_id}.json"), data)

def export_github_project_fields(organization, auth_token):
    '''Export GitHub project fields'''
    export_github_project_data(organization, auth_token, 'fields', Common.FOLDER_FIELDS_PATH)

def export_github_project_views(organization, auth_token):
    '''Export GitHub project views'''
    export_github_project_data(organization, auth_token, 'views', Common.FOLDER_VIEWS_PATH)

def export_github_project_items(organization, auth_token):
    '''Export GitHub project items'''
    export_github_project_data(organization, auth_token, 'items', Common.FOLDER_ITEM_PATH)

if __name__ == '__main__':
    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s [%(levelname)s] %(message)s",
        handlers = [
            logging.FileHandler("export.log"),
            logging.StreamHandler()
        ])

    parser = argparse.ArgumentParser(description='Export GitHub project data.')
    parser.add_argument('-o', '--operation',
                        choices=['all', 'projects', 'fields', 'views', 'items'],
                        required=True, help='Operation to perform')
    args = parser.parse_args()

    org = os.environ['GITHUB_ORG']
    token = os.environ['GITHUB_TOKEN']

    if not org:
        raise KeyError("The 'GITHUB_ORG' environment variable is missing.")
    if not token:
        raise KeyError("The 'GITHUB_TOKEN' environment variable is missing.")

    create_directories()

    if args.operation == 'all':
        export_github_projects(org, token, True)
    elif args.operation == 'projects':
        export_github_projects(org, token, False)
    elif args.operation == 'fields':
        export_github_project_fields(org, token)
    elif args.operation == 'views':
        export_github_project_views(org, token)
    elif args.operation == 'items':
        export_github_project_items(org, token)
    else:
        print("usage: export.py [-h] -o {all,projects,fields,views,items}")
