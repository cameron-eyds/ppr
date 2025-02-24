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
"""This class is a wrapper for document storage API calls."""
import datetime
from abc import ABC, abstractmethod
from enum import Enum

from google.cloud import storage

from ppr_api.callback.auth.token_service import GoogleStorageTokenService
from ppr_api.callback.utils.exceptions import StorageException
from ppr_api.utils.logging import logger

HTTP_DELETE = "delete"
HTTP_GET = "get"
HTTP_POST = "post"
CONTENT_TYPE_PDF = "application/pdf"


class DocumentTypes(str, Enum):
    """Render an Enum of storage document types."""

    SEARCH_RESULTS = "SEARCH_RESULTS"
    VERIFICATION_MAIL = "VERIFICATION_MAIL"
    REGISTRATION = "REGISTRATION"
    MAIL_DEFAULT = "MAIL_DEFAULT"


class StorageService(ABC):  # pylint: disable=too-few-public-methods
    """Storage Service abstract class for all implementations."""

    @classmethod
    @abstractmethod
    def get_document(cls, name: str, doc_type: str = None):
        """Fetch the uniquely named document from storage as binary data."""

    @classmethod
    @abstractmethod
    def save_document(cls, name: str, raw_data, doc_type: str = None):
        """Save or replace the named document in storage with the binary data as the file contents."""


class GoogleStorageService(StorageService):  # pylint: disable=too-few-public-methods
    """Google Cloud Storage implmentation.

    Maintain document storage with Google Cloud Storage API calls.
    """

    # Google cloud storage configuration.
    GCP_BUCKET_ID = None
    GCP_BUCKET_ID_VERIFICATION = None
    GCP_BUCKET_ID_REGISTRATION = None
    GCP_BUCKET_ID_MAIL = None

    @staticmethod
    def init_app(app):
        """Set up the service"""
        GoogleStorageService.GCP_BUCKET_ID = app.config.get("GCP_CS_BUCKET_ID")
        GoogleStorageService.GCP_BUCKET_ID_VERIFICATION = app.config.get("GCP_CS_BUCKET_ID_VERIFICATION")
        GoogleStorageService.GCP_BUCKET_ID_REGISTRATION = app.config.get("GCP_CS_BUCKET_ID_REGISTRATION")
        GoogleStorageService.GCP_BUCKET_ID_MAIL = app.config.get("GCP_CS_BUCKET_ID_MAIL")

    @classmethod
    def get_document(cls, name: str, doc_type: str = None):
        """Fetch the uniquely named document from cloud storage as binary data."""
        try:
            logger.info(f"Fetching doc type={doc_type}, name={name}.")
            return cls.__call_cs_api(HTTP_GET, name, None, doc_type)
        except StorageException as storage_err:
            raise storage_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            logger.error(f"get_document failed for doc type={doc_type}, name={name}.")
            logger.error(str(err))
            raise StorageException("GET document failed for doc type={doc_type}, name={name}.") from err

    @classmethod
    def get_document_link(cls, name: str, doc_type: str = None, available_days: int = 1):
        """Fetch the uniquely named document from cloud storage as a time-limited download link."""
        try:
            logger.info(f"Fetching doc type={doc_type}, name={name}.")
            return cls.__call_cs_api_link(name, None, doc_type, available_days)
        except StorageException as storage_err:
            raise storage_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            logger.error(f"get_document failed for doc type={doc_type}, name={name}.")
            logger.error(str(err))
            raise StorageException(f"GET document failed for doc type={doc_type}, name={name}.") from err

    @classmethod
    def delete_document(cls, name: str, doc_type: str = None):
        """Delete the uniquely named document from cloud storage (unit testing only)."""
        try:
            logger.info(f"Deleting doc type={doc_type}, name={name}.")
            return cls.__call_cs_api(HTTP_DELETE, name, None, doc_type)
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            logger.error(f"get_document failed for doc type {doc_type}, name {name}.")
            logger.error(str(err))
        return None

    @classmethod
    def save_document(cls, name: str, raw_data, doc_type: str = None):
        """Save or replace the named document in cloud storage with the binary data as the file contents."""
        try:
            logger.info(f"Saving doc type={doc_type}, name={name}.")
            return cls.__call_cs_api(HTTP_POST, name, raw_data, doc_type)
        except StorageException as storage_err:
            raise storage_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            logger.error(f"save_document failed for doc type={doc_type}, name={name}.")
            logger.error(str(err))
            raise StorageException(f"POST document failed for doc type={doc_type}, name={name}.") from err

    @classmethod
    def save_document_link(cls, name: str, raw_data, doc_type: str = None, available_days: int = 1):
        """Save a document to a cloud storage bucket with the binary data as the file contents. Return a link."""
        try:
            # bucket_id = cls.__get_bucket_id(doc_type)
            logger.info(f"Saving doc type={doc_type}, name={name}.")
            return cls.__call_cs_api_link(name, raw_data, doc_type, available_days)
        except StorageException as storage_err:
            raise storage_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            logger.error(f"save_document failed for doc type={doc_type}, name={name}.")
            logger.error(str(err))
            raise StorageException(f"POST document failed for doc type={doc_type}, name={name}.") from err

    @classmethod
    def __get_bucket_id(cls, doc_type: str = None):
        """Map the document type to a bucket ID. The default is GCP_BUCKET_ID."""
        if not doc_type or doc_type == DocumentTypes.SEARCH_RESULTS:
            return cls.GCP_BUCKET_ID
        if doc_type == DocumentTypes.REGISTRATION:
            return cls.GCP_BUCKET_ID_REGISTRATION
        if doc_type == DocumentTypes.MAIL_DEFAULT:
            return cls.GCP_BUCKET_ID_MAIL
        if doc_type == DocumentTypes.VERIFICATION_MAIL:
            return cls.GCP_BUCKET_ID_VERIFICATION
        return cls.GCP_BUCKET_ID

    @classmethod
    def __call_cs_api(  # pylint: disable=too-many-arguments; just 1 more
        cls,
        method: str,
        name: str,
        data=None,
        doc_type: str = None,
    ):
        """Call the Cloud Storage API."""
        credentials = GoogleStorageTokenService.get_credentials()
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(cls.__get_bucket_id(doc_type))
        blob = bucket.blob(name)
        if method == HTTP_POST:
            media_type: str = CONTENT_TYPE_PDF
            blob.upload_from_string(data=data, content_type=media_type)
            return blob.time_created
        if method == HTTP_GET:
            contents = blob.download_as_bytes()
            return contents
        if method == HTTP_DELETE:
            blob.delete()
            return None
        return None

    @classmethod
    def __call_cs_api_link(cls, name: str, data=None, doc_type: str = None, available_days: int = 1):
        """Call the Cloud Storage API, returning a time-limited download link."""
        credentials = GoogleStorageTokenService.get_credentials()
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(cls.__get_bucket_id(doc_type))
        blob = bucket.blob(name)
        if data:
            media_type: str = CONTENT_TYPE_PDF
            blob.upload_from_string(data=data, content_type=media_type)
        url = blob.generate_signed_url(
            version="v4", expiration=datetime.timedelta(days=available_days, hours=0, minutes=0), method="GET"
        )
        return url
