from flask import Blueprint, request, jsonify
from controller.encours import Encours
from flask_cors import CORS  # Importer CORS

# Créer un blueprint pour organiser l'API
api_bp = Blueprint('api', __name__)

# Initialiser l'objet Encours
encours = Encours()

# Appliquer CORS sur ce blueprint pour autoriser les requêtes venant de 'http://127.0.0.1:3000'
CORS(api_bp, origins=["http://127.0.0.1:3000"])

@api_bp.route('/test', methods=['GET'])
def test_route():
    return jsonify({"message": "API en ligne et fonctionnelle 🚀"}), 200

@api_bp.route('/upload', methods=['POST'])
def upload():
    """
    Endpoint pour uploader un fichier via Postman
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier trouvé'}), 400
    
    file = request.files['file']
    result = encours.upload_file(file)
    return jsonify(result), 200 if 'message' in result else 400
@api_bp.route('/create_table', methods=['POST'])
def create_table():
    """
    Route pour générer une table à partir d'un nom de fichier (string) déjà uploadé.
    """ 
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'Aucun nom de fichier fourni'}), 400

    print(data['filename'])
    # return jsonify(data['filename']) 
    filename = data['filename']
    result = encours.load_file_in_database(filename)
    return jsonify(result), 200 if 'message' in result else 400

@api_bp.route('/show_files', methods=['GET'])
def show_files():
    """
    Route pour récupérer la liste des fichiers XLSX dans le dossier 'load_file'.
    """
    files = encours.show_files()
    return jsonify({'files': files})

 
@api_bp.route('/get_encours', methods=['GET'])
def get_all_dfe_database():
    """
    Route pour récupérer la liste des fichiers XLSX dans le dossier 'load_file',
    avec support d'un paramètre d'offset.
    """
    try:
        offset = request.args.get('offset', default=0, type=int)  # récupère l'offset de l'URL
        files = encours.get_all_dfe_database(offset=offset)
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/read_file/<filename>', methods=['GET'])
def read_file(filename):
    """
    Route pour lire le contenu d'un fichier XLSX.
    """
    if filename not in encours.show_files():
        return jsonify({'error': 'File not found'}), 404
    data = encours.read_xlsx_file(filename)
    return jsonify({'data': data})
