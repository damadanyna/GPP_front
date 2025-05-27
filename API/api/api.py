from flask import Blueprint, request, jsonify,send_file
from controller.encours import Encours
from controller.compensation import Compensation
from flask_cors import CORS  # Importer CORS
from werkzeug.utils import secure_filename
import os 
import json 
import zipfile
import uuid


# Créer un blueprint pour organiser l'API
api_bp = Blueprint('api', __name__)

# Initialiser l'objet Encours
encours = Encours()
compensation = Compensation()

# Appliquer CORS sur ce blueprint pour autoriser les requêtes venant de 'http://127.0.0.1:3000'
# CORS(api_bp, origins=["http://127.0.0.1:3000"])
CORS(api_bp, resources={r"/*": {"origins": "*"}})


@api_bp.route('/test', methods=['GET'])
def test_route():
    return jsonify({"message": "API en ligne et fonctionnelle 🚀"}), 200

@api_bp.route('/upload', methods=['POST'])
def upload():
    """
    Endpoint pour uploader un fichier via Postman ou un formulaire.
    Le champ 'app' est utilisé pour déterminer dans quel sous-dossier enregistrer le fichier.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier trouvé'}), 400

    file = request.files['file']
    app_name = request.form.get('app')  # Récupère le paramètre 'app'
    print(app_name)
    result = encours.upload_file(file, app_name)  # Passe le paramètre à la méthode

    return jsonify(result), 200 if 'message' in result else 400

@api_bp.route('/create_table', methods=['POST'])
def create_table():
    """
    Route pour générer une table à partir d'un nom de fichier (string) déjà uploadé,
    dans un sous-dossier correspondant à 'app'.
    """ 
    data = request.get_json()

    if not data or 'filename' not in data or 'app' not in data:
        return jsonify({'error': 'Paramètres manquants : filename et app requis'}), 400

    filename = data['filename']
    app_name = data['app']

    print(f"Création de table pour le fichier : {filename} dans le dossier : {app_name}")

    result = encours.load_file_in_database(filename, app_name)
    return jsonify(result), 200 if 'message' in result else 400


@api_bp.route('/show_files', methods=['GET']) 
def show_files():
    """
    Route pour récupérer la liste des fichiers XLSX dans le dossier 'load_file'.
    """
    app_name = request.args.get('app')  # Récupère le paramètre 'app' de la requête GET
    files = encours.show_files(app=app_name)  # Passe le paramètre à ta fonction
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



@api_bp.route('/insert_cdi_row', methods=['POST'])
def insert_cdi_row():
        
    UPLOAD_FOLDER = "./uploads_files" 

    # Créer le dossier s'il n'existe pas
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER) 
    try:
        # 1. Récupérer les données (JSON string dans le champ row_data)
        if 'row_data' not in request.form:
            return jsonify({'error': 'Données manquantes'}), 400
        
        row_data = request.form['row_data']
        row = json.loads(row_data)  # transformer en dict

        # 2. Sauvegarder les fichiers et stocker les noms dans le row
        for field in ['FILLER2', 'FILLER3', 'RéférencePJ']:
            file = request.files.get(field)
            if file and file.filename:
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)
                print (f"Enregistré le fichier {filename} dans {save_path}")
                # Stocker juste le nom du fichier dans le champ correspondant
                row[field] = filename
            else:
                print(f"Aucun fichier trouvé pour le champ {field}")
                row[field] = None  # ou "" selon ton modèle SQL

        # 3. Insérer dans la base via ta fonction
        result = encours.insert_into_echange_cdi(row)
        return jsonify(result), 200 if result.get("status") == "success" else 400 

    except Exception as e:
        print(f"Erreur dans /insert_cdi_row : {e}")
        return jsonify({'error': str(e)}), 500

 
@api_bp.route('/insert_declaration', methods=['POST'])
def insert_declaration():
        
    UPLOAD_FOLDER = "./uploads_files/declarations_files" 
    # Créer le dossier s'il n'existe pas
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER) 
    try:
        # 1. Récupérer les données (JSON string dans le champ row_data)
        if 'row_data' not in request.form:
            return jsonify({'error': 'Données manquantes'}), 400
        
        row_data = request.form['row_data']
        row = json.loads(row_data)  # transformer en dict

        # 2. Sauvegarder les fichiers et stocker les noms dans le row
        for field in ['pj_ar', 'pj_cnp', 'pj_anr']:
            file = request.files.get(field)
            if file and file.filename:
                filename = secure_filename(file.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)
                print (f"Enregistré le fichier {filename} dans {save_path}")
                # Stocker juste le nom du fichier dans le champ correspondant
                row[field] = filename
            else:
                print(f"Aucun fichier trouvé pour le champ {field}")
                row[field] = None  # ou "" selon ton modèle SQL
 
        # 3. Insérer dans la base via ta fonction
        result = encours.insert_into_declaration(row)
        return jsonify(result), 200 if result.get("status") == "success" else 400  
    except Exception as e:
        print(f"Erreur dans /insert_declaration : {e}")
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
            'Total_interet_echus', 'OD Pen', 'OD & PEN', 'Solde du client', 'Genre',
            'Secteur_d_activité', 'Secteur_d_activité_code', 'Agent_de_gestion', 'Chiff_affaire', 'Code_Garantie',
            'Valeur_garantie', 'arr_status'
        ]
        liste_dictionnaires = [dict(zip(cles, ligne)) for ligne in data]
        return jsonify({'list_of_data': liste_dictionnaires}) 
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
@api_bp.route('/get_chq_in', methods=['GET'])
def get_chq_in():
    """
    Route pour récupérer la liste des fichiers XLSX dans le dossier 'load_file',
    avec support d'un paramètre d'offset.
    """ 
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 100))  
    try:  # récupère l'offset de l'URL
        data = compensation.get_chq_in(offset=offset,limit=limit)
        # Liste des clés
        cles = ['ftid','processdate','recordtype','chequenumber','orderingrib','beneficiaryrib','solde','code_anomalie','anomailie','ANO']
        liste_dictionnaires = [dict(zip(cles, ligne)) for ligne in data]
        return jsonify({'list_of_data': liste_dictionnaires}) 
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/int_compense', methods=['GET'])
def int_compense(): 
    try:  # récupère l'offset de l'URL
        result = compensation.initialize_sql_functions_and_tmp_table()
        print(result)
        return jsonify(result), 200 if result.get("status") == "success" else 400 
    except Exception as e:
        return jsonify({'error': str(e)}), 500

 
@api_bp.route('/import_tables_to_sipem_app', methods=['GET'])
def import_tables_to_sipem_app(): 
    try:  # récupère l'offset de l'URL
        result = compensation.import_tables_to_sipem_app( )
        return jsonify(result), 200 if result.get("status") == "initialisation success" else 400 
    except Exception as e:
        return jsonify({'error': str(e)}), 500

 
@api_bp.route('/get_liste_declarement', methods=['GET'])
def get_liste_declarement():
    """
    Route pour récupérer la liste des fichiers XLSX dans le dossier 'load_file',
    avec support d'un paramètre d'offset.
    """
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 100))  
    print (f"offset: {offset}, limit: {limit}")
    try:  # récupère l'offset de l'URL
        data = encours.get_liste_declarement(offset=offset,limit=limit)
        # Liste des clés
        cles =[
            'id',
            'nom_dossier',
            'numero_dossier',
            'date_creation',
            'filler1',
            'pj_ar',
            'pj_cnp',
            'pj_anr',
            'filler2',
            'filler3',
            'filler4',
            'Date_enreg',
            'is_create'
        ]
        liste_dictionnaires = [dict(zip(cles, ligne)) for ligne in data]
        
        return jsonify({'list_of_data': liste_dictionnaires}) 
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 


@api_bp.route('/get_list_cdi', methods=['GET'])
def get_all_CDI():
    """
    Route pour récupérer la liste des fichiers XLSX dans le dossier 'load_file',
    avec support d'un paramètre d'offset.
    """
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 100))  
    print (f"offset: {offset}, limit: {limit}")
    try:  # récupère l'offset de l'URL
        data = encours.get_all_cdi_database(offset=offset,limit=limit)
        # Liste des clés
        cles = [
            'ID','ID.1', 'ErrorMessage', 'ProcessStatus', 'ProcessDate', 'ValidationStatus',
            'OrderingBank', 'OrderingBranch', 'VoucherNumber', 'RecordType', 'PaymentRef',
            'ChequeType', 'ChequeAmt', 'ChequeNumber', 'OrderingRib', 'OrderingName',
            'OrderingAddr', 'BeneficiaryBank', 'BeneficiaryBranch', 'BeneficiaryRib',
            'BeneficiaryName', 'BeneficiaryAddr', 'DateChqIssue', 'PaymentDetails',
            'RepresentReason', 'ClearanceDate', 'DatePresented', 'SettlementDate',
            'RejectCode', 'CanRcpFile', 'FtId', 'OlbFtId', 'RevOlbFt', 'HoldIntmCdtFt',
            'OVERRIDE', 'RECORD.STATUS', 'CURR.NO', 'INPUTTER', 'DATE.TIME', 'AUTHORISER',
            'CO.CODE', 'DEPT.CODE', 'AUDITOR.CODE', 'AUDIT.DATE.TIME','solde'
        ]

        liste_dictionnaires = [dict(zip(cles, ligne)) for ligne in data]
        return jsonify({'list_of_data': liste_dictionnaires}) 
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/get_liste_a_traiter', methods=['GET'])
def get_liste_a_traiter():
    """
    Route pour récupérer la liste des fichiers XLSX dans le dossier 'load_file',
    avec support d'un paramètre d'offset.
    """ 
    try:  # récupère l'offset de l'URL
        data = encours.get_liste_a_traiter()
        # Liste des clés
        cles =[
            "Id",
            "Agence",
            "Agec",
            "Compte",
            "Nom",
            "Classt",
            "Codape",
            "Mntcaht",
            "Cli_n_a",
            "Nature",
            "Typecredit",
            "Montant",
            "Datech",
            "Rang",
            "Taux",
            "Datouv",
            "Genre",
            "Creating_date",
            "Group_of",
            "Date_enreg"
        ]

        liste_dictionnaires = [dict(zip(cles, ligne)) for ligne in data]
        return jsonify({'list_of_data': liste_dictionnaires}) 
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/get_liste_cdi', methods=['GET'])
def get_liste_cdi():
    """
    Route pour récupérer la liste des fichiers XLSX dans le dossier 'load_file',
    avec support d'un paramètre d'offset.
    """ 
    try:  # récupère l'offset de l'URL
        data = encours.get_liste_cdi()
        # Liste des clés
        cles =[
        "id",
        "code_etablissement",
        "code_agence",
        "ordering_rib",
        "identification_tiers",
        "identification_contrevenants",
        "type_moyen_paiement",
        "numero_moyen_paiement",
        "montant_moyen_paiement",
        "date_emission",
        "date_presentation",
        "date_echeance",
        "identification_beneficiaire",
        "nom_beneficiaire",
        "nom_banque_presentateur",
        "motif_refus",
        "solde_compte_rejet",
        "sens_solde",
        "reference_effet_impaye",
        "reference_lettre_injonction",
        "date_lettre_injonction",
        "reference_envoi_lettre_injonction",
        "date_envoi_lettre_injonction",
        "existence_pj",
        "date_pj",
        "reference_pj",
        "filler2",
        "filler3",
        "filler4",
        "filler5",
        "Creating_date",
        "group_of",
        "Date_enreg",
        "is_create"
        ]

        liste_dictionnaires = [dict(zip(cles, ligne)) for ligne in data]
        return jsonify({'list_of_data': liste_dictionnaires}) 
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/get_liste_faites', methods=['GET'])
def get_liste_faites():
    """
    Route pour récupérer la liste des fichiers XLSX dans le dossier 'load_file',
    avec support d'un paramètre d'offset.
    """ 
    try:  # récupère l'offset de l'URL
        data = encours.get_liste_faites()
        # Liste des clés
        cles =[
            "Id",
            "Agence",
            "Agec",
            "Compte",
            "Nom",
            "Classt",
            "Codape",
            "Mntcaht",
            "Cli_n_a",
            "Nature",
            "Typecredit",
            "Montant",
            "Datech",
            "Rang",
            "Taux",
            "Datouv",
            "Genre",
            "Creating_date",
            "Group_of",
            "Date_enreg"
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

@api_bp.route('/update_is_create', methods=['POST'])
def update_is_create():
    """
    Route pour mettre à jour les lignes où is_create = false
    et assigner un group_of aléatoire.
    """
    try:
        result = encours.update_group_and_flag()
        return jsonify(result), 200 if result.get("status") == "success" else 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 


  
@api_bp.route('/upload-and-compress', methods=['POST'])
def upload_and_compress_txt():
    UPLOAD_FOLDER = './uploads_files/ziped_files'
    DECLARATION_FOLDER = './uploads_files/declarations_files'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier reçu'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400

    if not file.filename.endswith('.txt'):
        return jsonify({'error': 'Le fichier doit être au format .txt'}), 400

    # Récupérer les noms de fichiers depuis le formulaire
    pj_anr = request.form.get('pj_anr')
    pj_ar = request.form.get('pj_ar')
    pj_cnp = request.form.get('pj_cnp')

    # Construire les chemins complets
    files_to_add = []
    for fname in [pj_anr, pj_ar, pj_cnp]:
        if fname:
            path = os.path.join(DECLARATION_FOLDER, fname)
            if os.path.exists(path):
                files_to_add.append(path)
            else:
                print(f"Fichier non trouvé : {path}")

    try:
        unique_id = str(uuid.uuid4())
        txt_filename = f"{unique_id}.txt"
        txt_path = os.path.join(UPLOAD_FOLDER, txt_filename)
        file.save(txt_path)

        zip_filename = f"{unique_id}.zip"
        zip_path = os.path.join(UPLOAD_FOLDER, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(txt_path, arcname=file.filename)  # Fichier .txt
            for other_file in files_to_add:
                zipf.write(other_file, arcname=os.path.basename(other_file))  # Ajouter avec nom original

        return send_file(zip_path, as_attachment=True, download_name=zip_filename, mimetype='application/zip')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        try:
            if os.path.exists(txt_path):
                os.remove(txt_path)
            if os.path.exists(zip_path):
                os.remove(zip_path)
        except Exception as cleanup_err:
            print(f"Erreur de nettoyage : {cleanup_err}")
