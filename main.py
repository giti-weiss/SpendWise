from flask import Flask

# קודם כל טוענים מודלים!
import models.import_all

from db_connection import engine
from models.base import Base

# יצירת טבלאות אחרי טעינה
Base.metadata.create_all(bind=engine)

# controllers
from controller.core.categories_controller import categories_blueprint
from controller.core.users_controller import users_blueprint


app = Flask(__name__)
app.register_blueprint(categories_blueprint)
app.register_blueprint(users_blueprint)


@app.route('/')
def home():
    return "Server is running!"


if __name__ == '__main__':
    app.run(debug=True)