from databases import Database
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "bot.db")
database = Database('sqlite:///' + db_path)
