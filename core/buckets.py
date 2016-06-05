from couchbase.bucket import Bucket
import logging

import couchbase
couchbase.enable_logging()

logging.basicConfig(level=logging.INFO)

match_history = Bucket('couchbase://localhost/match_history')