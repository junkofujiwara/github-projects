#!/usr/bin/env python3
# -*- coding: utf_8 -*-
'''githubsession.py'''
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    '''Create session'''
    retry_strategy = Retry(
        total=3,
        status_forcelist=[504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

class GitHubSession:
    '''GitHub Session'''
    def __init__(self, endpoint, headers):
        self.endpoint = endpoint
        self.headers = headers
        self.session = create_session()

    def post(self, query, variables):
        '''Post request'''
        response = self.session.post(
            self.endpoint,
            json={'query': query, 'variables': variables},
            headers=self.headers
        )
        return response.json()
