#!/usr/bin/env python3
# -*- coding: utf_8 -*-
'''github.py'''
import requests

class ProjectV2Field:
    '''ProjectV2Field class to store field data'''
    def __init__(self, field_id, name, typename):
        self.id = field_id
        self.name = name
        self.typename = typename

class ProjectV2IterationField(ProjectV2Field):
    '''ProjectV2IterationField class to store iteration field data'''
    def __init__(self, field_id, name, typename, configuration):
        super().__init__(field_id, name, typename)
        self.configuration = configuration

class ProjectV2SingleSelectField(ProjectV2Field):
    '''ProjectV2SingleSelectField class to store single select field data'''
    def __init__(self, field_id, name, typename, options):
        super().__init__(field_id, name, typename)
        self.options = options

class ProjectV2ItemFieldValueCommon:
    '''ProjectV2ItemFieldValueCommon class to store item field value data'''
    def __init__(self, field):
        self.field = field

class ProjectV2ItemFieldTextValue(ProjectV2ItemFieldValueCommon):
    '''ProjectV2ItemFieldTextValue class to store text field value data'''
    def __init__(self, text, field):
        super().__init__(field)
        self.type = 'text'
        self.value = text

class ProjectV2ItemFieldDateValue(ProjectV2ItemFieldValueCommon):
    '''ProjectV2ItemFieldDateValue class to store date field value data'''
    def __init__(self, date, field):
        super().__init__(field)
        self.type = 'date'
        self.value = date

class ProjectV2ItemFieldSingleSelectValue(ProjectV2ItemFieldValueCommon):
    '''ProjectV2ItemFieldSingleSelectValue class to store single select field value data'''
    def __init__(self, name, field):
        super().__init__(field)
        self.type = 'single_select'
        self.value = name

class ProjectV2ItemFieldNumberValue(ProjectV2ItemFieldValueCommon):
    '''ProjectV2ItemFieldNumberValue class to store number field value data'''
    def __init__(self, number, field):
        super().__init__(field)
        self.type = 'number'
        self.value = number

class ProjectV2ItemFieldIterationValue(ProjectV2ItemFieldValueCommon):
    '''ProjectV2ItemFieldIterationValue class to store iteration field value data'''
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
                  __typename
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
                      duration
                      startDay
                      completedIterations{
                        startDate
                        id
                        title
                        duration
                      }
                      iterations {
                        startDate
                        id
                        title
                        duration
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
                      color
                      description
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
            response = requests.post(github.endpoint,
                                     json={'query': query, 'variables': variables},
                                     headers=github.headers)
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
                      __typename
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
                      ... on ProjectV2ItemFieldNumberValue{
                        number
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldIterationValue {
                        title
                        startDate
                        duration
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
            response = requests.post(github.endpoint,
                                     json={'query': query, 'variables': variables},
                                     headers=github.headers)
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
                      number
                      layout
                      filter
                      sortByFields(first: 20) {
                          nodes {
                            direction
                            field {
                                ... on ProjectV2Field {
                                  id
                                  name
                                  dataType
                                }
                                ... on ProjectV2IterationField {
                                  id
                                  name
                                  dataType
                                }
                                ... on ProjectV2SingleSelectField {
                                  id
                                  name
                                  dataType
                                }
                              }
                            }
                        }
                      groupByFields(first: 20) {
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
                                }
                                ... on ProjectV2SingleSelectField {
                                  id
                                  name
                                  dataType
                                }
                            }
                        }
                      verticalGroupByFields(first: 20) {
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
                            }
                            ... on ProjectV2SingleSelectField {
                              id
                              name
                              dataType
                            }
                          }
                        }
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
            response = requests.post(github.endpoint,
                                     json={'query': query, 'variables': variables},
                                     headers=github.headers)
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
        response = requests.post(self.endpoint,
                                 json={'query': query, 'variables': variables},
                                 headers=self.headers)
        data = response.json()

        if 'data' not in data:
            raise KeyError(f"The 'data' key is missing in the response. Response content: {data}")

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

    def get_single_project(self, target_project_id):
        '''get_single_project'''
        try:
            project = Project(
                project_id = target_project_id
            )
            project.fetch_fields(self)
            project.fetch_items(self)

            # fields
            fields = []
            for field_data in project.fields[0]:
                typename = field_data.get("__typename")
                if typename == "ProjectV2SingleSelectField":
                    field = ProjectV2SingleSelectField(
                        field_data["id"],
                        field_data["name"],
                        typename,
                        field_data["options"]
                    )
                elif typename == "ProjectV2IterationField":
                    field = ProjectV2IterationField(
                        field_data["id"],
                        field_data["name"],
                        typename,
                        field_data["configuration"]
                    )
                else:
                    field = ProjectV2Field(
                        field_data["id"],
                        field_data["name"],
                        typename
                    )
                fields.append(field)

            # draft items
            items = project.items[0]
            draft_items = [{'id': item['content']['id'], 'title': item['content']['title']}
                           for item in items]

            return fields, draft_items

        except Exception as error:
            raise ValueError(f"Failed to get project fields: {error}") from error

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
        response = requests.post(self.endpoint,
                                 json={'query': query, 'variables': variables},
                                 headers=self.headers)
        data = response.json()
        if 'data' in data and 'createProjectV2' in data['data'] and \
            'projectV2' in data['data']['createProjectV2']:
            project_id = data['data']['createProjectV2']['projectV2']['id']
            return project_id

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
        response = requests.post(self.endpoint,
                                 json={'query': query, 'variables': variables},
                                 headers=self.headers)
        data = response.json()
        if 'data' in data and 'updateProjectV2' in data['data'] and \
            'projectV2' in data['data']['updateProjectV2']:
            project_id = data['data']['updateProjectV2']['projectV2']['id']
            project_title = data['data']['updateProjectV2']['projectV2']['title']
            return project_id, project_title

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
        response = requests.post(self.endpoint,
                                 json={'query': query, 'variables': variables},
                                 headers=self.headers)
        data = response.json()
        return data['data']['organization']['id']

    def create_field(self, project_id, data_type, name):
        '''create_field'''
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
        variables = {
            "projectId": project_id,
            "dataType": data_type,
            "name": name
        }

        response = requests.post(self.endpoint,
                                 json={'query': query, 'variables': variables},
                                 headers=self.headers)
        data = response.json()
        if 'errors' in data:
            raise ValueError(f"Failed to create field: {data}")

        return data['data']['createProjectV2Field']['clientMutationId']

    def create_field_selection(self, project_id, data_type, name, options):
        '''create_field for single selection'''
        query = '''
        mutation($projectId: ID!, $dataType: ProjectV2CustomFieldType!, $name: String!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
          createProjectV2Field(input: {
            projectId: $projectId
            dataType: $dataType
            name: $name
            singleSelectOptions: $options
          }) {
            clientMutationId
          }
        }
        '''
        variables = {
            "projectId": project_id,
            "dataType": data_type,
            "name": name,
            "options": options
        }

        response = requests.post(self.endpoint,
                                 json={'query': query, 'variables': variables},
                                 headers=self.headers)
        data = response.json()
        if 'errors' in data:
            raise ValueError(f"Failed to create field (selection): {data}")

        return data['data']['createProjectV2Field']['clientMutationId']

    def get_content(self, repository, number):
        '''get_content'''
        query = '''
        query($owner: String!, $repository: String!, $number: Int!) {
          repository(owner: $owner, name: $repository) {
            issueOrPullRequest(number: $number) {
             __typename
              ... on Issue {
                id
                number
                title
              }
              ... on PullRequest {
                id
                number
                title
              }
            }
          }
        }
        '''
        variables = {
            "owner": self.org,
            "repository": repository,
            "number": number
        }
        response = requests.post(self.endpoint,
                                 json={'query': query, 'variables': variables},
                                 headers=self.headers)
        data = response.json()
        if 'errors' in data:
            raise ValueError(f"Failed to get contents: {data}")
        return data['data']['repository']['issueOrPullRequest']

    def add_project_item(self, project_id, content_id):
        '''add_item'''
        query = '''
        mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {
            projectId: $projectId
            contentId: $contentId
          }) {
            item {
              id
            }
          }
        }
        '''
        variables = {
            "projectId": project_id,
            "contentId": content_id
        }
        response = requests.post(self.endpoint,
                                 json={'query': query, 'variables': variables},
                                 headers=self.headers)
        data = response.json()
        if 'errors' in data:
            raise ValueError(f"Failed to create item: {data}")
        return data['data']['addProjectV2ItemById']['item']

    def set_item_field_value(self, project_id, item_id, field_id, value, value_type):
        '''set_field_value'''
        value_key = {
            'text': 'text',
            'iteration': 'iterationId',
            'selection': 'singleSelectOptionId',
            'date': 'date',
            'number': 'number'
        }.get(value_type)

        if not value_key:
            raise ValueError(f"Invalid value_type: {value_type}")

        value_type_map = {
            'text': 'String',
            'iteration': 'String',
            'selection': 'String',
            'date': 'Date',
            'number': 'Float'
        }

        query = f'''
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: {value_type_map[value_type]}!) {{
          updateProjectV2ItemFieldValue(input: {{
            projectId: $projectId
            itemId: $itemId
            fieldId: $fieldId
            value: {{ 
                {value_key}: $value       
              }}
          }}) {{
            projectV2Item {{
              id
            }}
          }}
        }}
        '''
        variables = {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "value": value
        }
        response = requests.post(self.endpoint,
                                 json={'query': query, 'variables': variables},
                                 headers=self.headers)
        data = response.json()
        if 'errors' in data:
            raise ValueError(f"Failed to set item field value for {value_type}: {data}")
        return data['data']['updateProjectV2ItemFieldValue']['projectV2Item']['id']

    def set_item_field_value_text(self, project_id, item_id, field_id, value):
        '''set_field_value_text'''
        return self.set_item_field_value(project_id, item_id, field_id, value, 'text')

    def set_item_field_value_iteration(self, project_id, item_id, field_id, value):
        '''set_field_value_iteration'''
        return self.set_item_field_value(project_id, item_id, field_id, value, 'iteration')

    def set_item_field_value_selection(self, project_id, item_id, field_id, value):
        '''set_field_value_selection'''
        return self.set_item_field_value(project_id, item_id, field_id, value, 'selection')

    def set_item_field_value_date(self, project_id, item_id, field_id, value):
        '''set_field_value_date'''
        return self.set_item_field_value(project_id, item_id, field_id, value, 'date')

    def set_item_field_value_number(self, project_id, item_id, field_id, value):
        '''set_field_value_number'''
        return self.set_item_field_value(project_id, item_id, field_id, value, 'number')

    def add_draft_issue(self, project_id, title, body):
        '''add_draft_issue'''
        query = '''
        mutation($projectId: ID!, $title: String!, $body: String) {
          addProjectV2DraftIssue(input: {
            projectId: $projectId
            title: $title
            body: $body
          }) {
            projectItem {
              id
            }
          }
        }
        '''
        variables = {
            "projectId": project_id,
            "title": title,
            "body": body
        }
        response = requests.post(self.endpoint,
                                 json={'query': query, 'variables': variables},
                                 headers=self.headers)
        data = response.json()
        if 'errors' in data:
            raise ValueError(f"Failed to create draft issue: {data}")
        return data['data']['addProjectV2DraftIssue']['projectItem']['id']
