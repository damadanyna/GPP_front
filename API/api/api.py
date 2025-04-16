from flask import Blueprint, request, jsonify
from controller.encours import Encours
from flask_cors import CORS  # Importer CORS

# Créer un blueprint pour organiser l'API
api_bp = Blueprint('api', __name__)

# Initialiser l'objet Encours
encours = Encours()

# Appliquer CORS sur ce blueprint pour autoriser les requêtes venant de 'http://127.0.0.1:3000'
# CORS(api_bp, origins=["http://127.0.0.1:3000"])
CORS(api_bp, resources={r"/*": {"origins": "*"}})


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

@api_bp.route('/insert_credit_row', methods=['POST'])
def insert_credit_row():
    """
    Reçoit une ligne de crédit du frontend et l'insère dans echange_credit.
    """
    data = request.get_json()

    if not data or 'row_data' not in data:
        return jsonify({'error': 'Aucune donnée reçue'}), 400

    row = data['row_data']

    try:
        result = encours.insert_into_echange_credit(row)
        return jsonify(result), 200 if result.get("status") == "success" else 400

    except Exception as e:
        print(f"Erreur dans /insert_credit_row : {e}")
        return jsonify({'error': str(e)}), 500

 
@api_bp.route('/get_encours', methods=['GET'])
def get_all_dfe_database():
    """
    Route pour récupérer la liste des fichiers XLSX dans le dossier 'load_file',
    avec support d'un paramètre d'offset.
    """
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 100))  
    print (f"offset: {offset}, limit: {limit}")
    try:  # récupère l'offset de l'URL
        data = encours.get_all_dfe_database(offset=offset,limit=limit)
        # Liste des clés
        cles = [
            'Agence', 'identification_client', 'Numero_pret', 'linked_appl_id', 'Date_pret',
            'Date_fin_pret', 'Nom_client', 'Produits', 'Amount', 'Duree_Remboursement',
            'taux_d_interet', 'Nombre_de_jour_retard', 'payment_date', 'Statut_du_client',
            'Capital_Non_appele_ech', 'Capital_Appele_Non_verse', 'Total_capital_echus_non_echus',
            'Total_interet_echus', 'OD Pen', 'OD & PEN', 'Solde du client', 'Agent_de_gestion',
            'Secteur_d_activité', 'Secteur_d_activité_code', '.Agent_de_gestion', 'Code_Garantie',
            'Valeur_garantie', 'arr_status'
        ]
        liste_dictionnaires = [dict(zip(cles, ligne)) for ligne in data]
        return jsonify({'list_of_data': liste_dictionnaires}) 
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
