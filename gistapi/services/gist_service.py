from typing import Dict, List, Literal, Pattern

import requests
import re


class UserDoesNotExist(Exception):
    """Exception happens if we get 404 error"""


class PermissionDenied(Exception):
    """Exception happens if we get 403 error"""


class GistDoesNotExist(Exception):
    """Exception happens if we get 404 during gist fetching."""


class GistService:

    def __init__(self, username: str, per_page: int = 30):
        self.username = username
        self.per_page = per_page
        self.cached_list = None
        self.cached_gists = {}

    def _make_request(self, url: str, method: Literal['GET', 'POST'] = 'GET', **params: Dict) -> requests.Response:
        if method == 'GET':
            return requests.get(url, params=params, headers={'Accept': 'application/vnd.github.v3+json'})
        raise NotImplemented()

    def _retrieve_list(self, **params) -> List[Dict]:
        response = self._make_request(
            f'https://api.github.com/users/{self.username}/gists',
            method='GET',
            **params,
        )
        if response.status_code == requests.codes.ok:
            return response.json()
        if response.status_code == 404:
            raise UserDoesNotExist()
        if response.status_code == 403:
            raise PermissionDenied()
        response.raise_for_status()

    def _retrieve_gist(self, gist_id: str) -> Dict:
        response = self._make_request(f'https://api.github.com/gists/{gist_id}')
        if response.status_code == requests.codes.ok:
            return response.json()
        if response.status_code == 403:
            raise PermissionDenied()
        if response.status_code == 404:
            raise GistDoesNotExist()
        response.raise_for_status()

    def get_list(self, skip_error: bool = False, reset_cache: bool = False) -> List:
        if reset_cache:
            self.cached_list = None

        if self.cached_list is not None:
            return self.cached_list

        page = 1
        self.cached_list = []
        try:
            data = self._retrieve_list(page=page, per_page=self.per_page)
            while len(data):
                self.cached_list.append(data)
                yield from data
                page += 1
                data = self._retrieve_list(page=page, per_page=self.per_page)
        except PermissionDenied:
            if not skip_error:
                raise
        return self.cached_list

    def get_gist(self, gist_id: str, reset_cache: bool = False) -> Dict:
        if reset_cache:
            self.cached_gists.pop(gist_id, None)
        if gist_id in self.cached_gists:
            return self.cached_gists[gist_id]
        return self._retrieve_gist(gist_id=gist_id)

    def get_gists_by_pattern(self, pattern: Pattern[str], skip_error: bool = False) -> List[Dict]:
        compiled_pattern = re.compile(pattern)
        matched_gists = []
        for gist in self.get_list(skip_error=skip_error):
            try:
                gist_data = self.get_gist(gist_id=gist['id'])
            except PermissionDenied:
                continue
            for filename, filedata in gist_data.get('files', {}).items():
                if compiled_pattern.match(filedata['content']):
                    matched_gists.append(f'https://gist.github.com/{self.username}/{gist["id"]}')
                    break
        return matched_gists
