from flask import Flask
from controller.encours import Encours
from api.api import api_bp

app = Flask(__name__)

# Initialiser la classe Encours
encours = Encours()

# Enregistrer les routes de l'API
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=8081)
    
    # flask --app app run --port=8081
    flask run --host=0.0.0.0

