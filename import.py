'''Import GitHub project information'''
import json
import logging
import os
from util.github import GitHub

FOLDER_PATH = "projects"
MAPPING_FILE_PATH = "project_mapping.log"

def get_json_files(folder_path):
    '''Get JSON files in a folder'''
    return [f for f in os.listdir(folder_path) if f.endswith('.json')]

def import_github_project(organization, auth_token):
    '''Import GitHub project information'''
    github = GitHub(organization, auth_token)
    json_files = get_json_files(FOLDER_PATH)
    owner_id = github.get_ownerid()

    with open(MAPPING_FILE_PATH, 'w', encoding='utf-8') as mapping_file:
        for json_file in json_files:
            process_file(github, owner_id, json_file, mapping_file)

def process_file(github, owner_id, json_file, mapping_file):
    '''Process a file'''
    file_path = os.path.join(FOLDER_PATH, json_file)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            project_data = json.load(file)
            logging.info('import project: %s', file_path)

            # project create & update
            target_project_id = github.create_project(project_data, owner_id)
            source_project_id = project_data['id']
            github.update_project(target_project_id, project_data)
            mapping_file.write(f"{source_project_id} -> {target_project_id}\n")

    except json.JSONDecodeError as json_error:
        logging.error('Failed to decode JSON file %s: %s', file_path, str(json_error))
    except FileNotFoundError as file_not_found_error:
        logging.error('File not found %s: %s', file_path, str(file_not_found_error))
    except KeyError as key_error:
        logging.error('Missing key in project data %s: %s', file_path, str(key_error))
    except Exception as general_error:
        logging.error('Failed to process file %s: %s', file_path, str(general_error))

if __name__ == '__main__':
    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s [%(levelname)s] %(message)s",
        handlers = [
            logging.FileHandler("import.log"),
            logging.StreamHandler()
        ])
    org = os.environ['GITHUB_ORG_TARGET']
    token = os.environ['GITHUB_TOKEN_TARGET']

    if not org:
        raise KeyError("The 'GITHUB_ORG_TARGET' environment variable is missing.")
    if not token:
        raise KeyError("The 'GITHUB_TOKEN_TARGET' environment variable is missing.")

    import_github_project(org, token)
                         