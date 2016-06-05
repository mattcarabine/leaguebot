from couchbase.bucket import Bucket
import logging
import os

import couchbase
couchbase.enable_logging()

logging.basicConfig(level=logging.INFO)

match_history = Bucket('couchbase://{}/{}'.format(
    os.environ.get('DB_HOST', 'localhost'),
    os.environ.get('DB_BUCKET_MATCH_HISTORY', 'match_history')
))