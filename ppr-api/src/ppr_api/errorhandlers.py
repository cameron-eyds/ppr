# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Core error handlers and custom exceptions.

Following best practices from:
http://flask.pocoo.org/docs/1.0/errorhandling/
http://flask.pocoo.org/docs/1.0/patterns/apierrors/
"""
import sys

from flask import jsonify
from flask_pydantic.exceptions import ValidationError
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RoutingException

from ppr_api.utils.logging import logger


def init_app(app):
    """Initialize the error handlers for the Flask app instance."""
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(HTTPException, handle_http_error)
    app.register_error_handler(Exception, handle_uncaught_error)


def handle_http_error(error):
    """Handle HTTPExceptions.

    Include the error description and corresponding status code, known to be
    available on the werkzeug HTTPExceptions.
    """
    # As werkzeug's routing exceptions also inherit from HTTPException,
    # check for those and allow them to return with redirect responses.
    if isinstance(error, RoutingException):
        return error

    logger.error(f"Http exception {error.description}")
    response = jsonify({"errors": error.description})
    response.status_code = error.code
    return response


def handle_uncaught_error(error: Exception):  # pylint: disable=unused-argument
    """Handle any uncaught exceptions.

    Since the handler suppresses the actual exception, log it explicitly to
    ensure it's logged and recorded in Sentry.
    """
    logger.error(f"Uncaught exception {sys.exc_info()}")
    response = jsonify({"errors": "Internal server error"})
    response.status_code = 500
    return response


def handle_validation_error(error):
    """Handle pydantic validation error."""
    logger.error(f"Validation Error {error.body_params}")
    response = jsonify({"errors": f"Validation Error {error.body_params}"})
    response.status_code = 400
    return response
