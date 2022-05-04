# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Model helper utilities for processing search query and search detail requests.

Search constants and helper functions.
"""
# flake8: noqa Q000,E122,E131
# Disable Q000: Allow query strings to be in double quotation marks that contain single quotation marks.
# Disable E122: allow query strings to be more human readable.
# Disable E131: allow query strings to be more human readable.

GET_DETAIL_DAYS_LIMIT = 7 # Number of days in the past a get details request is allowed.
# Maximum number of days in the past to filter when fetching account search history: set to <= 0 to disable.
GET_HISTORY_DAYS_LIMIT = 14

# Account search history max result set size.
ACCOUNT_SEARCH_HISTORY_MAX_SIZE = 1000
# Maximum number or results returned by search.
SEARCH_RESULTS_MAX_SIZE = 5000

# Result set size limit clause
RESULTS_SIZE_LIMIT_CLAUSE = 'FETCH FIRST :max_results_size ROWS ONLY'

ACCOUNT_SEARCH_HISTORY_DATE_QUERY = f"""
SELECT sc.id, sc.search_ts, sc.api_criteria, sc.total_results_size, sc.returned_results_size,
       sr.callback_url, sr.doc_storage_url,
       json_array_length(sr.api_result) as selected_match_count,
       (SELECT CASE WHEN sc.user_id IS NULL THEN ''
         ELSE (SELECT u.firstname || ' ' || u.lastname FROM users u WHERE u.username = sc.user_id)
         END) AS username
FROM search_requests sc, search_results sr
WHERE sc.id = sr.search_id
  AND sc.account_id = '?'
  AND sc.search_ts > ((now() at time zone 'utc') - interval '{str(GET_HISTORY_DAYS_LIMIT)} days')
  AND sc.search_type IN ('MI', 'MO', 'MS', 'MM')
ORDER BY sc.search_ts DESC
FETCH FIRST {str(ACCOUNT_SEARCH_HISTORY_MAX_SIZE)} ROWS ONLY
"""

ACCOUNT_SEARCH_HISTORY_QUERY = f"""
SELECT sc.id, sc.search_ts, sc.api_criteria, sc.total_results_size, sc.returned_results_size,
       sr.callback_url, sr.doc_storage_url,
       json_array_length(sr.api_result) as selected_match_count,
       (SELECT CASE WHEN sc.user_id IS NULL THEN ''
         ELSE (SELECT u.firstname || ' ' || u.lastname FROM users u WHERE u.username = sc.user_id)
         END) AS username
FROM search_requests sc, search_results sr
WHERE sc.id = sr.search_id
  AND sc.account_id = '?'
  AND sc.search_type IN ('MI', 'MO', 'MS', 'MM')
ORDER BY sc.search_ts DESC
FETCH FIRST {str(ACCOUNT_SEARCH_HISTORY_MAX_SIZE)} ROWS ONLY
"""

ACCOUNT_SEARCH_HISTORY_DATE_QUERY_NEW = f"""
SELECT sc.id, sc.search_ts, sc.api_criteria, sc.total_results_size, sc.returned_results_size, sc.user_id,
       sr.callback_url, sr.doc_storage_url, sr.api_result,
       json_array_length(sr.api_result) as selected_match_count,
       (SELECT CASE WHEN sc.user_id IS NULL THEN ''
         ELSE (SELECT u.firstname || ' ' || u.lastname FROM users u WHERE u.username = sc.user_id)
         END) AS username
FROM search_requests sc, search_results sr
WHERE sc.id = sr.search_id
  AND sc.account_id = '?'
  AND sc.search_type IN ('MI', 'MO', 'MS', 'MM')
  AND sc.search_ts > ((now() at time zone 'utc') - interval '{str(GET_HISTORY_DAYS_LIMIT)} days')
ORDER BY sc.search_ts DESC
FETCH FIRST {str(ACCOUNT_SEARCH_HISTORY_MAX_SIZE)} ROWS ONLY
"""

ACCOUNT_SEARCH_HISTORY_QUERY_NEW = f"""
SELECT sc.id, sc.search_ts, sc.api_criteria, sc.total_results_size, sc.returned_results_size, sc.user_id,
       sr.callback_url, sr.doc_storage_url, sr.api_result,
       json_array_length(sr.api_result) as selected_match_count,
       (SELECT CASE WHEN sc.user_id IS NULL THEN ''
         ELSE (SELECT u.firstname || ' ' || u.lastname FROM users u WHERE u.username = sc.user_id)
         END) AS username
FROM search_requests sc, search_results sr
WHERE sc.id = sr.search_id
  AND sc.account_id = '?'
  AND sc.search_type IN ('MI', 'MO', 'MS', 'MM')
ORDER BY sc.search_ts DESC
FETCH FIRST {str(ACCOUNT_SEARCH_HISTORY_MAX_SIZE)} ROWS ONLY
"""