# Import get_db from the database_utils.py file to make it available when importing from the database package
from .. import database_utils
get_db = database_utils.get_db
engine = database_utils.engine