'''Import GitHub project'''
import argparse
import json
import logging
import os
from util.github import GitHub

FOLDER_PATH = "projects"
FOLDER_ITEM_PATH = "projects_items"
MAPPING_FILE_PATH = "project_mapping.log"
MAPPING_ITEMS_FILE_PATH = "project_items_mapping.log"

def get_json_files(folder_path):
    '''Get JSON files in a folder'''
    return [f for f in os.listdir(folder_path) if f.endswith('.json')]

def read_project_mapping():
    '''Read project mapping file'''
    mapping = {}
    with open(MAPPING_FILE_PATH, 'r', encoding='utf-8') as file:
        for line in file:
            key, value = line.strip().split(' -> ')
            mapping[key] = value
    return mapping

def import_github_project(organization, auth_token):
    '''Import GitHub project'''
    github = GitHub(organization, auth_token)
    json_files = get_json_files(FOLDER_PATH)
    owner_id = github.get_ownerid()

    with open(MAPPING_FILE_PATH, 'w', encoding='utf-8') as mapping_file:
        for json_file in json_files:
            project_id = json_file.split('.')[0]
            create_project(project_id, github, owner_id,
                           os.path.join(FOLDER_PATH, json_file),
                           mapping_file)

def create_project(project_id, github, owner_id, file_path, mapping_file):
    '''Create project'''
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            project_data = json.load(file)
            logging.info('Create Project - %s', project_id)

            # project create & update
            target_project_id = github.create_project(project_data, owner_id)
            source_project_id = project_data['id']
            updated_project_id, updated_project_title = github.update_project(target_project_id, project_data)
            mapping_file.write(f"{source_project_id} -> {target_project_id}\n")
            logging.info('Create Project Succeeded - Id:%s Title:%s', updated_project_id, updated_project_title)

    except FileNotFoundError as fnf_error:
        logging.error('File not found - %s %s', file_path, str(fnf_error))
    except Exception as general_error:
        logging.error('Create Project Failed - %s: %s', project_id, str(general_error))

def import_github_project_items(organization, auth_token):
    '''Import GitHub project items'''
    github = GitHub(organization, auth_token)
    json_files = get_json_files(FOLDER_ITEM_PATH)
    project_mapping = read_project_mapping()

    with open(MAPPING_ITEMS_FILE_PATH, 'w', encoding='utf-8') as mapping_file:
        for json_file in json_files:
            project_id = json_file.split('.')[0]
            mapped_project_id = project_mapping.get(project_id)
            insert_items(project_id, github,
                         os.path.join(FOLDER_ITEM_PATH, json_file),
                         mapped_project_id,
                         mapping_file)

def insert_items(project_id, github, file_path, mapped_project_id, mapping_file):
    '''Insert items'''
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            project_data = json.load(file)
            logging.debug('Insert Items - Source:%s Taregt:%s', project_id, mapped_project_id)

            # items are not in the json file
            if not project_data or not isinstance(project_data, list) or not project_data[0] or not isinstance(project_data[0], list) or not project_data[0][0]:
                logging.debug('Item not found in file %s.', file_path)
                return
            
            # GitHub contents - issue / pull request
            for item in project_data[0]:
                if 'content' in item:
                    content_id, content_number, repository_name = get_content_from_file(item)
                    field_values_list = get_values_from_file(item)
                    logging.info('Insert Items -  Project ID: %s, Content ID: %s, Number: %s, Repository: %s, Fields Count: %s',
                                 mapped_project_id,
                                 content_id,
                                 content_number,
                                 repository_name,
                                 len(field_values_list))

                    # get content with new id
                    github_content = github.get_content(repository_name, content_number)
                    target_content_id = github_content['id']
                    # add item
                    github.add_project_item(mapped_project_id, target_content_id)
                    # add field values
                    for field in field_values_list:
                        if field['typename'] == 'ProjectV2ItemFieldTextValue':
                            logging.debug('text: %s, %s', field['field_name'], field['value'])
                        elif field['typename'] == 'ProjectV2ItemFieldNumberValue':
                            logging.debug('number: %s, %s', field['field_name'], field['value'])
                        elif field['typename'] == 'ProjectV2ItemFieldSingleSelectValue':
                            logging.debug('select: %s, %s', field['field_name'], field['value'])
                            

                    mapping_file.write(f"{repository_name},{content_number},{content_id} -> {target_content_id}\n")
                    logging.info('Insert Items Succeeded - Project ID: %s, Content ID: %s, Number: %s, Repository: %s',
                                 mapped_project_id,
                                 target_content_id,
                                 content_number,
                                 repository_name)

    except FileNotFoundError as fnf_error:
        logging.error('File not found - %s %s', file_path, str(fnf_error))
    except Exception as general_error:
        logging.error('Insert Items Failed - %s: %s', project_id, str(general_error))

def get_content_from_file(item):
    '''Get content from file'''
    if 'content' in item:
        contents = item['content']
        content_id = contents['id']
        content_number = contents['number']
        repository_name = contents['repository']['name']
        return content_id, content_number, repository_name

def get_values_from_file(item):
    ''' Get values from file'''
    if 'fieldValues' in item:
        field_values = item['fieldValues']['nodes']
        field_values_list = []
        for field in field_values:
            if len(field) == 1 and '__typename' in field:
                continue  # Skip nodes that only contain __typename
            typename = field.get('__typename')
            value = field.get('text') or field.get('name')
            field_name = field.get('field', {}).get('name')
            field_values_list.append({
                    'typename': typename,
                    'value': value,
                    'field_name': field_name
                })
        return field_values_list

if __name__ == '__main__':
    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s [%(levelname)s] %(message)s",
        handlers = [
            logging.FileHandler("import.log"),
            logging.StreamHandler()
        ])

    parser = argparse.ArgumentParser(description='Import GitHub project')
    parser.add_argument('-o', '--operation',
                        choices=['create-projects', 'insert-items'],
                        help='Operation to perform (create-projects, insert-items)')
    args = parser.parse_args()

    org = os.environ['GITHUB_ORG_TARGET']
    token = os.environ['GITHUB_TOKEN_TARGET']

    if not org:
        raise KeyError("The 'GITHUB_ORG_TARGET' environment variable is missing.")
    if not token:
        raise KeyError("The 'GITHUB_TOKEN_TARGET' environment variable is missing.")

    if args.operation == 'create-projects':
        import_github_project(org, token)
    elif args.operation == 'insert-items':
        import_github_project_items(org, token)
    else:
        print ('usage: import.py [-h] [-o {create-project,insert-items}]')
                         