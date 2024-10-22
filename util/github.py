#!/usr/bin/env python3
# -*- coding: utf_8 -*-
'''github.py'''
import requests

class ProjectV2Field:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class ProjectV2IterationField(ProjectV2Field):
    def __init__(self, id, name, configuration):
        super().__init__(id, name)
        self.configuration = configuration

class ProjectV2SingleSelectField(ProjectV2Field):
    def __init__(self, id, name, options):
        super().__init__(id, name)
        self.options = options

class ProjectV2ItemFieldValueCommon:
    def __init__(self, field):
        self.field = field

class ProjectV2ItemFieldTextValue(ProjectV2ItemFieldValueCommon):
    def __init__(self, text, field):
        super().__init__(field)
        self.type = 'text'
        self.value = text

class ProjectV2ItemFieldDateValue(ProjectV2ItemFieldValueCommon):
    def __init__(self, date, field):
        super().__init__(field)
        self.type = 'date'
        self.value = date

class ProjectV2ItemFieldSingleSelectValue(ProjectV2ItemFieldValueCommon):
    def __init__(self, name, field):
        super().__init__(field)
        self.type = 'single_select'
        self.value = name

class ProjectV2ItemFieldNumberValue(ProjectV2ItemFieldValueCommon):
    def __init__(self, number, field):
        super().__init__(field)
        self.type = 'number'
        self.value = number

class ProjectV2ItemFieldIterationValue(ProjectV2ItemFieldValueCommon):
    def __init__(self, iteration, field):
        super().__init__(field)
        self.type = 'iteration'
        self.value = iteration

class Project:
    '''Project class to store project data'''
    def __init__(self, project_id):
        self.project_id = project_id
        self.project_meta = []
        self.fields = []
        self.views = []
        self.items = []

    def fetch_fields(self, github):
        '''Fetch fields for the project'''
        query = '''
        query($id: ID!, $cursor: String) {
          node(id: $id) {
            ... on ProjectV2 {
              fields(first: 20, after: $cursor) {
                nodes {
                  ... on ProjectV2Field {
                    id
                    name
                    dataType
                  }
                  ... on ProjectV2IterationField {
                    id
                    name
                    dataType
                    configuration {
                      iterations {
                        startDate
                        id
                      }
                    }
                  }
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                    dataType
                    options {
                      id
                      name
                    }
                  }
                }
                pageInfo {
                  hasNextPage
                  endCursor
                }
              }
            }
          }
        }
        '''
        variables = {
            "id": self.project_id,
            "cursor": None
        }
        
        while True:
            response = requests.post(github.endpoint, json={'query': query, 'variables': variables}, headers=github.headers)
            data = response.json()
            
            self.fields.append(data['data']['node']['fields']['nodes'])
            
            page_info = data['data']['node']['fields']['pageInfo']
            if page_info['hasNextPage']:
                variables['cursor'] = page_info['endCursor']
            else:
                break

    def fetch_items(self, github):
        '''Fetch items for the project'''
        query = '''
          query($id: ID!, $cursor: String) {
          node(id: $id) {
            ... on ProjectV2 {
              items(first: 20, after: $cursor) {
                nodes {
                  id
                  fieldValues(first: 8) {
                    nodes {
                      ... on ProjectV2ItemFieldTextValue {
                        text
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldDateValue {
                        date
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldSingleSelectValue {
                        name
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                    }
                  }
                  content {
                    ... on DraftIssue {
                      id
                      title
                      body
                    }
                    ... on Issue {
                      id
                      number
                      title
                      repository {
                        id
                        name
                      }
                    }
                    ... on PullRequest {
                      id
                      number
                      title
                      repository {
                        id
                        name
                      }
                    }
                  }
                }
                pageInfo {
                  endCursor
                  hasNextPage
                }
              }
            }
          }
        }
        '''
        variables = {
            "id": self.project_id,
            "cursor": None
        }
        
        while True:
              response = requests.post(github.endpoint, json={'query': query, 'variables': variables}, headers=github.headers)
              data = response.json()

              if 'data' not in data:
                raise KeyError(f"'data' key not found in response: {data}")
              
              items_data = data['data']['node']['items']

              self.items.append(items_data['nodes'])
              
              page_info = items_data['pageInfo']
              if page_info['hasNextPage']:
                  variables['cursor'] = page_info['endCursor']
              else:
                  break

    def fetch_views(self, github):
            '''Fetch views for the project'''
            query = '''
            query($id: ID!, $cursor: String) {
              node(id: $id) {
                ... on ProjectV2 {
                  views(first: 20, after: $cursor) {
                    nodes {
                      id
                      name
                      filter
                      fields(first: 20) {
                        nodes {
                          ... on ProjectV2Field {
                              id
                              name
                              dataType
                          }
                          ... on ProjectV2IterationField {
                              id
                              name
                              dataType
                              configuration {
                                iterations {
                                  startDate
                                  id
                                }
                              }
                          }
                          ... on ProjectV2SingleSelectField {
                              id
                              name
                              dataType
                              options {
                                id
                                name
                            }
                          }
                        }
                      }
                    }
                    pageInfo {
                      endCursor
                      hasNextPage
                    }
                  }
                }
              }
            }
            '''
            variables = {
                "id": self.project_id,
                "cursor": None
            }

            while True:
              response = requests.post(github.endpoint, json={'query': query, 'variables': variables}, headers=github.headers)
              data = response.json()

              if 'data' not in data:
                raise KeyError(f"'data' key not found in response: {data}")
              
              views_data = data['data']['node']['views']

              self.views.append(views_data['nodes'])
              
              page_info = views_data['pageInfo']
              if page_info['hasNextPage']:
                  variables['cursor'] = page_info['endCursor']
              else:
                  break

        
class GitHub:
    '''GitHub class'''
    def __init__(self, org, token):
        self.endpoint = 'https://api.github.com/graphql'
        self.org = org
        self.token = token
        self.headers={'Authorization': f'bearer {self.token}',
                      'Accept': 'application/vnd.github.v3+json'}

    def get_projects(self):
        '''get_projects'''
        query = '''
        query($organization: String!) {
          organization(login: $organization) {
            projectsV2(first: 100) {
              nodes {
                id
                title
                shortDescription
                closed
                public
                readme
              }
              pageInfo {
                hasNextPage
                endCursor
              }
            }
          }
        }
        '''
        variables = {
            "organization": f'{self.org}'
        }
        response = requests.post(self.endpoint, json={'query': query, 'variables': variables}, headers=self.headers)
        data = response.json()

        if 'data' not in data:
            raise KeyError("The 'data' key is missing in the response. Response content: {}".format(data))
        
        projects = []
        for node in data['data']['organization']['projectsV2']['nodes']:
            project = Project(
                project_id = node['id']
            )
            project.project_meta = node
            project.fetch_fields(self)
            project.fetch_views(self)
            project.fetch_items(self)
            projects.append(project)
        
        return projects
    
    def create_project(self, project, owner_id):
        '''create_project'''
        query = '''
        mutation($title: String!, $ownerId: ID!) {
          createProjectV2(input: {
            title: $title
            ownerId: $ownerId
          }) {
            projectV2 {
              id
              title
            }
          }
        }
        '''
        variables = {
            "title": project['title'],
            "ownerId": owner_id
        }
        response = requests.post(self.endpoint, json={'query': query, 'variables': variables}, headers=self.headers)
        data = response.json()
        if 'data' in data and 'createProjectV2' in data['data'] and 'projectV2' in data['data']['createProjectV2']:
          project_id = data['data']['createProjectV2']['projectV2']['id']
          return project_id
        else:
          raise ValueError(f"Failed to create project: {data}")
    
    def update_project(self, project_id, project):
        '''update_project'''
        query = '''
        mutation($id: ID!, $title: String!, $closed: Boolean, $public: Boolean, $readme: String, $shortDescription: String) {
          updateProjectV2(input: {
            projectId: $id
            title: $title
            closed: $closed
            public: $public
            readme: $readme
            shortDescription: $shortDescription
          }) {
            projectV2 {
              id
              title
              closed
              public
              readme
              shortDescription
            }
          }
        }
        '''
        variables = {
            "id": project_id,
            "title": project['title'],
            "closed": project.get('closed'),
            "public": project.get('public'),
            "readme": project.get('readme'),
            "shortDescription": project.get('shortDescription')
        }
        response = requests.post(self.endpoint, json={'query': query, 'variables': variables}, headers=self.headers)
        data = response.json()
        if 'data' in data and 'updateProjectV2' in data['data'] and 'projectV2' in data['data']['updateProjectV2']:
          project_id = data['data']['updateProjectV2']['projectV2']['id']
          return project_id
        else:
          raise ValueError(f"Failed to update project: {data}")
        
    def get_ownerid(self):
        '''get_ownerid'''
        query = '''
        query($login: String!) {
          organization(login: $login) {
            id
            name
          }
        }
        '''
        variables = {
            "login": self.org
        }
        response = requests.post(self.endpoint, json={'query': query, 'variables': variables}, headers=self.headers)
        data = response.json()
        return data['data']['organization']['id']
    
    def create_fields(self, project_id, fields):
        '''create_fields'''
        query = '''
        mutation($projectId: ID!, $dataType: ProjectV2CustomFieldType!, $name: String!) {
          createProjectV2Field(input: {
            projectId: $projectId
            dataType: $dataType
            name: $name
          }) {
            clientMutationId
          }
        }
        '''

        data_type = fields.get('dataType')
        if not data_type:
          raise ValueError("Field 'dataType' is missing or invalid in the provided fields data")

        variables = {
            "projectId": project_id,
            "dataType": fields['dataType'],
            "name": fields['name']
        }
        response = requests.post(self.endpoint, json={'query': query, 'variables': variables}, headers=self.headers)
        data = response.json()
        if 'errors' in data:
            raise ValueError(f"Failed to create fields: {data}")
        
        
