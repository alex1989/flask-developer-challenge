# coding=utf-8
"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""

import requests
from flask import Flask, jsonify, request


# *The* app object
from gistapi.exceptions import RestException, NotFound
from gistapi.services.gist_service import GistService, UserDoesNotExist
from gistapi.validators import clean_post_data

app = Flask(__name__)


@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


@app.route("/api/v1/search", methods=['POST'])
def search():
    """Provides matches for a single pattern across a single users gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    username, pattern = clean_post_data(request.get_json())

    gist_service = GistService(username=username)
    try:
        gists = gist_service.get_gists_by_pattern(pattern, skip_error=True)
        return jsonify({
            'status': 'success',
            'username': username,
            'pattern': pattern,
            'matches': gists,
        })
    except UserDoesNotExist:
        raise NotFound('such user does not exist')


@app.errorhandler(RestException)
def handle_invalid_usage(error):
   response = jsonify(error.to_dict())
   response.status_code = error.status_code
   return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9876)
