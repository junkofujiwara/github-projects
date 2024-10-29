'''Import GitHub project'''
import argparse
import json
import logging
import os
from util.github import GitHub

FOLDER_PATH = "projects"
FOLDER_FIELDS_PATH = "projects_fields"
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
            logging.info('Create Project Succeeded - Id:%s Title:%s',
                         updated_project_id,
                         updated_project_title)

    except FileNotFoundError as fnf_error:
        logging.error('File not found - %s %s', file_path, str(fnf_error))
    except Exception as general_error:
        logging.error('Create Project Failed - %s: %s', project_id, str(general_error))

def import_github_project_fields(organization, auth_token):
    '''Import GitHub project fields'''
    github = GitHub(organization, auth_token)
    json_files = get_json_files(FOLDER_FIELDS_PATH)
    project_mapping = read_project_mapping()

    for json_file in json_files:
        project_id = json_file.split('.')[0]
        mapped_project_id = project_mapping.get(project_id)
        create_fields(project_id, github,
                        os.path.join(FOLDER_FIELDS_PATH, json_file),
                        mapped_project_id)

def field_exists(field_name, mapped_project_fields_info):
    '''Check if field exists'''
    return any(field_name == mapped_field.name for mapped_field in mapped_project_fields_info[0])

def create_field(github, mapped_project_id, field):
    '''Create field'''
    field_id = field['id']
    field_name = field['name']
    field_type = field['dataType']
    logging.info('Create Field - Id:%s Name:%s', field_id, field_name)

    if field_type == 'SINGLE_SELECT':
        options = field['options']
        options_names = [{'color': 'GRAY', 'description': '', 'name': option['name']} for option in options]
        mapped_field_id = github.create_field_selection(mapped_project_id, field_type, field_name, options_names)
        logging.info('Create Field Succeeded - Id:%s Name:%s', field_id, field_name)
    elif field_type == 'ITERATION':
        logging.info('Create Field Skipped (Iteration) - Id:%s Name:%s', field_id, field_name)
    else:
        mapped_field_id = github.create_field(mapped_project_id, field_type, field_name)
        logging.info('Create Field Succeeded - Id:%s Name:%s', field_id, field_name)

def create_fields(project_id, github, file_path, mapped_project_id):
    '''Create fields'''
    try:
        logging.info('Create Fields on Project %s', mapped_project_id)
        project_data = load_project_data(file_path)
        if not project_data:
            logging.debug('Fields not found in file %s.', file_path)
            return

        # get current project fields
        mapped_project_fields_info = github.get_single_project(mapped_project_id)

        # create fields
        for project_fields in project_data:
            for field in project_fields:
                if not (isinstance(field, dict) and 'id' in field and 'name' in field and 'dataType' in field):
                    break

                # check if field exists
                if field_exists(field['name'], mapped_project_fields_info):
                    logging.info('Create Field Skipped - Id:%s Name:%s', field['id'], field['name'])
                else:
                    create_field(github, mapped_project_id, field)

    except FileNotFoundError as fnf_error:
        logging.error('File not found - %s %s', file_path, str(fnf_error))
    except Exception as general_error:
        logging.error('Create Fields Failed - %s: %s', project_id, str(general_error))

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
        project_data = load_project_data(file_path)
        if not project_data:
            logging.debug('Item not found in file %s.', file_path)
            return

        mapped_project_fields_info, mapped_project_draft_issue = github.get_single_project(mapped_project_id)

        for item in project_data[0]:
            if 'content' in item:
                process_item(item, github, mapped_project_id, mapped_project_fields_info, mapped_project_draft_issue, mapping_file)

    except FileNotFoundError as fnf_error:
        logging.error('File not found - %s %s', file_path, str(fnf_error))
    except Exception as general_error:
        logging.error('Insert Items Failed - %s: %s', project_id, str(general_error))

def load_project_data(file_path):
    '''Load project data'''
    with open(file_path, 'r', encoding='utf-8') as file:
        project_data = json.load(file)
        logging.debug('Loaded project data from %s', file_path)
        if not project_data or not isinstance(project_data, list) or not project_data[0] or not isinstance(project_data[0], list) or not project_data[0][0]:
            return None
        return project_data

def process_item(item, github, mapped_project_id, mapped_project_fields_info, mapped_project_draft_issue, mapping_file):
    '''Process item'''
    content_type, content_id, content_number, repository_name = get_content_from_file(item)

    if content_type == "DI":
        process_draft_issue(content_number, mapped_project_id, content_id, mapped_project_draft_issue, github, repository_name)
    else:
        process_issue_or_pr(item, github, mapped_project_id, content_id, content_number, repository_name, mapped_project_fields_info, mapping_file)

def process_draft_issue(title, mapped_project_id, content_id, mapped_project_draft_issue, github, repository_name):
    '''Process draft issue'''
    logging.info('Insert Draft Issue - Project ID: %s, Content ID: %s, Title: %s', mapped_project_id, content_id, title)
    draft_exists = any(title in item['title'] for item in mapped_project_draft_issue)
    if draft_exists:
        logging.info('Insert Draft Issue Skipped - Project ID: %s, Content ID: %s, Title: %s', mapped_project_id, content_id, title)
    else:
        github.add_draft_issue(mapped_project_id, title, repository_name)
        logging.info('Insert Draft Issue Succeeded - Project ID: %s, Content ID: %s, Title: %s', mapped_project_id, content_id, title)

def process_issue_or_pr(item, github, mapped_project_id, content_id, content_number, repository_name, mapped_project_fields_info, mapping_file):
    '''Process issue or PR'''
    field_values_list = get_values_from_file(item)
    logging.info('Insert Items - Project ID: %s, Content ID: %s, Number: %s, Repository: %s, Fields Count: %s',
                 mapped_project_id, content_id, content_number, repository_name, len(field_values_list))

    github_content = github.get_content(repository_name, content_number)
    target_content_id = github_content['id']

    project_item = github.add_project_item(mapped_project_id, target_content_id)
    mapping_file.write(f"{repository_name},{content_number},{content_id} -> {target_content_id}\n")
    logging.info('Insert Items Succeeded - Project ID: %s, Content ID: %s, Number: %s, Repository: %s',
                 mapped_project_id, target_content_id, content_number, repository_name)

    set_field_values(github, mapped_project_id, project_item['id'], field_values_list, mapped_project_fields_info)

def find_field_id_by_name(field, mapped_project_fields_info):
    '''Find field id by name'''
    field_name = field['field_name']
    field_value = field['value']

    for mapped_field in mapped_project_fields_info:
        if mapped_field.name == field_name:
            field_id, mapped_field_value_id = get_field_id_and_value_id(mapped_field, field_value)
            if mapped_field_value_id is None and field_id is not None and (
                mapped_field.typename in ("ProjectV2SingleSelectField", "ProjectV2IterationField")):
                logging.warning("Option IDs are not found for field %s, value %s", field_name,field_value)
            return field_id, mapped_field_value_id

    logging.warning("Field not found in target project %s", field_name)
    return None, None

def get_field_id_and_value_id(mapped_field, field_value):
    '''Get field id and value id'''
    field_id = mapped_field.id
    mapped_field_value_id = None

    if mapped_field.typename == "ProjectV2SingleSelectField":
        mapped_field_value_id = find_value_id_in_options(mapped_field.options, field_value)
    elif mapped_field.typename == "ProjectV2IterationField":
        mapped_field_value_id = find_value_id_in_iterations(mapped_field.configuration, field_value)

    return field_id, mapped_field_value_id

def find_value_id_in_options(options, field_value):
    '''Find value id in options'''
    for value in options:
        if 'name' in value and value['name'] == field_value:
            return value['id']
    return None

def find_value_id_in_iterations(configuration, field_value):
    '''Find value id in iterations'''
    for iteration_type in ['completedIterations', 'iterations']:
        for value in configuration.get(iteration_type, []):
            if 'title' in value and value['title'] == field_value:
                return value['id']
    return None

def set_field_values(github, mapped_project_id, item_id, field_values_list, mapped_project_fields_info):
    '''Set field values'''
    try:
        field_ids = []
        for field in field_values_list:
            try:
                field_name = field['field_name']
                if field_name == 'Title': # skip Title field
                    continue
                logging.info('Update Field Value: %s, %s', field_name, field['value'])

                # map field ids
                field_id, field_mapped_value_id = find_field_id_by_name(field, mapped_project_fields_info)
                if field_id is None:
                    continue

                logging.info('Update Field Value: %s, %s, target field id %s, mapped id %s',
                             field_name,
                             field['value'],
                             field_id,
                             field_mapped_value_id)

                typename = field['typename']
                field_value = field['value']
                if typename == 'ProjectV2ItemFieldTextValue':
                    logging.debug('Updating Field Value (Text): %s, %s', field_name, field_value)
                    github.set_item_field_value_text(mapped_project_id, item_id, field_id, field_value)
                    logging.info('Update Field Value Succeeded (Text) - %s, %s', field_name, field_value)
                elif typename == 'ProjectV2ItemFieldNumberValue':
                    logging.debug('Updating Field Value (Number): %s, %s', field_name, field_value)
                    github.set_item_field_value_number(mapped_project_id, item_id, field_id, field_value)
                    logging.info('Update Field Value Succeeded (Number) - %s, %s', field_name, field_value)
                elif typename == 'ProjectV2ItemFieldSingleSelectValue':
                    logging.debug('Updating Field Value (SingleSelect): %s, %s', field_name, field_mapped_value_id)
                    github.set_item_field_value_selection(mapped_project_id, item_id, field_id, field_mapped_value_id)
                    logging.info('Update Field Value Succeeded (SingleSelect) - %s, %s', field_name, field_mapped_value_id)
                elif typename == 'ProjectV2ItemFieldDateValue':
                    logging.debug('Updating Field Value (Date): %s, %s', field_name, field_value)
                    github.set_item_field_value_date(mapped_project_id, item_id, field_id, field_value)
                    logging.info('Update Field Value Succeeded (Date) - %s, %s', field_name, field_value)
                elif typename == 'ProjectV2ItemFieldIterationValue':
                    logging.debug('Updating Field Value (Iteration): %s, %s', field_name, field_mapped_value_id)
                    github.set_item_field_value_iteration(mapped_project_id, item_id, field_id, field_mapped_value_id)
                    logging.info('Update Field Value Succeeded (Iteration) - %s, %s', field_name, field_mapped_value_id)
                field_ids.append(field_id)
            except Exception as field_error:
                logging.error('Update Field Value Failed - %s, field name %s: %s', item_id, field_name, str(field_error))

    except Exception as general_error:
        logging.error('Update Field Value Failed - %s: %s', item_id, str(general_error))
    return field_ids

def get_content_from_file(item):
    '''Get content from file'''
    if 'content' in item:
        contents = item['content']
        content_id = contents['id']
        is_draft = content_id.startswith("DI_")

        content_title = contents.get('title', '') if is_draft else None
        content_body = contents.get('body', '') if is_draft else None
        content_number = contents.get('number') if not is_draft else None
        repository_name = contents['repository']['name'] if not is_draft else None

        return ("DI", content_id, content_title, content_body) if is_draft else ("I", content_id, content_number, repository_name)

    return (None, None, None, None)

def get_values_from_file(item):
    ''' Get values from file'''
    if 'fieldValues' in item:
        field_values = item['fieldValues']['nodes']
        field_values_list = []
        for field in field_values:
            if len(field) == 1 and '__typename' in field:
                continue  # Skip nodes that only contain __typename
            typename = field.get('__typename')
            value = None
            if typename == "ProjectV2ItemFieldTextValue":
                value = field.get('text')
            elif typename == "ProjectV2ItemFieldSingleSelectValue":
                value = field.get('name')
            elif typename == "ProjectV2ItemFieldIterationValue":
                value = field.get('title')
            elif typename == "ProjectV2ItemFieldNumberValue":
                value = field.get('number')
            elif typename == "ProjectV2ItemFieldDateValue":
                value = field.get('date')
            field_name = field.get('field', {}).get('name')

            # warning
            if value is None:
                logging.warning("Value is not found for field %s", field_name)

            field_values_list.append({
                    'typename': typename,
                    'value': value,
                    'field_name': field_name
                })

        return field_values_list
    return []

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
                        choices=['create-projects', 'create-fields', 'insert-items'],
                        help='Operation to perform (create-projects, create-fields, insert-items)')
    args = parser.parse_args()

    org = os.environ['GITHUB_ORG_TARGET']
    token = os.environ['GITHUB_TOKEN_TARGET']

    if not org:
        raise KeyError("The 'GITHUB_ORG_TARGET' environment variable is missing.")
    if not token:
        raise KeyError("The 'GITHUB_TOKEN_TARGET' environment variable is missing.")

    if args.operation == 'create-projects':
        import_github_project(org, token)
    elif args.operation == 'create-fields':
        import_github_project_fields(org, token)
    elif args.operation == 'insert-items':
        import_github_project_items(org, token)
    else:
        print ('usage: import.py [-h] [-o {create-projects, create-fields, insert-items}]')
                         