from app.models import DatabaseEnvironment
from launcher import create_window

DatabaseEnvironment.update_db_connection()
create_window()
