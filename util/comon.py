#!/usr/bin/env python3
# -*- coding: utf_8 -*-
'''Common utility'''
import os
import json

class Common:
    '''Common utility'''
    FOLDER_PATH = "projects"
    FOLDER_FIELDS_PATH = "projects_fields"
    FOLDER_VIEWS_PATH = "projects_views"
    FOLDER_ITEM_PATH = "projects_items"
    MAPPING_FILE_PATH = "project_mapping.log"
    MAPPING_ITEMS_FILE_PATH = "project_items_mapping.log"

    def get_json_files(folder_path):
        '''Get JSON files in a folder'''
        return [f for f in os.listdir(folder_path) if f.endswith('.json')]

    def write_json_to_file(file_path, data):
        '''Write JSON data to a file'''
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    def project_id_list(folder_path):
        '''Get project ID list from JSON files'''
        json_files = Common.get_json_files(folder_path)
        project_id_list = []
        for json_file in json_files:
            project_id_list.append(json_file.split('.')[0])
        return project_id_list