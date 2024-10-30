'''Check GitHub Project'''
import argparse
import logging
import os
from util.github import GitHub
from util.comon import Common

def get_json_files(folder_path):
    '''Get JSON files in a folder'''
    return [f for f in os.listdir(folder_path) if f.endswith('.json')]

def read_project_mapping():
    '''Read project mapping file'''
    mapping = {}
    with open(Common.MAPPING_FILE_PATH, 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split(' -> ')
            mapping[key] = value
    return mapping

def check_project_item_counts(organization, auth_token, project_type):
    '''Check project items'''
    github = GitHub(organization, auth_token)
    json_files = get_json_files(Common.FOLDER_PATH)
    for json_file in json_files:
        project_id = json_file.split('.')[0]
        if project_type == 'target':
            project_mapping = read_project_mapping()
            mapped_project_id = project_mapping.get(project_id)
            project_id = mapped_project_id
        logging.info('Check: Org %s, Project ID: %s', organization, project_id)
        count = github.get_project_items_count(project_id)
        logging.info('Check Completed: Org %s, Project ID: %s, Item Count: %s',
                     organization, project_id, count)

if __name__ == '__main__':
    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s [%(levelname)s] %(message)s",
        handlers = [
            logging.FileHandler("check.log"),
            logging.StreamHandler()
        ])

    parser = argparse.ArgumentParser(description='Check GitHub project')
    parser.add_argument('-o', '--operation',
                        choices=['check-item-source', 'check-item-target'],
                        help='Operation to perform (check-item-source, check-item-target)')
    args = parser.parse_args()

    org = os.environ['GITHUB_ORG']
    token = os.environ['GITHUB_TOKEN']
    org_target = os.environ['GITHUB_ORG_TARGET']
    token_target = os.environ['GITHUB_TOKEN_TARGET']

    if not org:
        raise KeyError("The 'GITHUB_ORG' environment variable is missing.")
    if not token:
        raise KeyError("The 'GITHUB_TOKEN' environment variable is missing.")
    if not org_target:
        raise KeyError("The 'GITHUB_ORG_TARGET' environment variable is missing.")
    if not token_target:
        raise KeyError("The 'GITHUB_TOKEN_TARGET' environment variable is missing.")

    if args.operation == 'check-item-source':
        check_project_item_counts(org, token, project_type='source')
    elif args.operation == 'check-item-target':
        check_project_item_counts(org_target, token_target, project_type='target')
    else:
        print ('usage: import.py [-h] [-o {check-item-source, check-item-target}]')
