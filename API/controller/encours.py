import os
from werkzeug.utils import secure_filename
import openpyxl
from datetime import datetime
from db.db  import DB 

class Encours:
    def __init__(self):
        # Dossier où les fichiers seront enregistrés
        self.upload_folder = 'load_file'
        self.db = DB() 
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def upload_file(self, file):
        """
        Cette méthode permet de télécharger un fichier et de l'enregistrer dans le dossier 'load_file'
        """
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(self.upload_folder, filename)
            file.save(filepath)
            return {'message': 'File successfully uploaded', 'filename': filename}
        return {'error': 'Invalid file format'}

    def allowed_file(self, filename):
        """
        Vérifie si l'extension du fichier est autorisée
        """
        ALLOWED_EXTENSIONS = {'xlsx'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def show_files(self): 
        """
        Récupère la liste des fichiers xlsx dans le dossier 'load_file'
        et les retourne sous forme d'objets : {"used": False, "file_name": "nom.xlsx"}
        """
        files = []
        for filename in os.listdir(self.upload_folder):
            if filename.endswith('.xlsx'):
                files.append({
                    "used": False,
                    "file_name": filename
                })
        return files


    def read_xlsx_file(self, filename):
        """
        Lire le fichier xlsx et récupérer son contenu.
        """
        filepath = os.path.join(self.upload_folder, filename)
        workbook = openpyxl.load_workbook(filepath)
        sheet = workbook.active
        data = []
        for row in sheet.iter_rows(values_only=True):
            data.append(row)
        return data
    
    def get_all_dfe_database(self, offset,limit):
        try: 
            conn = self.db.connect()
            cursor = conn.cursor()
            # Offset should be dynamically included in the query
            select_query = f'SELECT * FROM etat_des_encours LIMIT {limit} OFFSET {offset}'
            # select_query = f'SELECT * FROM etat_des_encours'
            
            # Execute the query
            cursor.execute(select_query)
            rows = cursor.fetchall()
 
            return rows

        except Exception as global_e:
            error_msg = f"Erreur {global_e}"
            print("Erreur", global_e)
            return {'error': error_msg} 
    def get_liste_a_traiter(self):
        try: 
            conn = self.db.connect()
            cursor = conn.cursor()
            # Offset should be dynamically included in the query
            select_query = f'SELECT * FROM echange_credit where is_create=false'
            # select_query = f'SELECT * FROM etat_des_encours'
            
            # Execute the query
            cursor.execute(select_query)
            rows = cursor.fetchall()
 
            return rows

        except Exception as global_e:
            error_msg = f"Erreur {global_e}"
            print("Erreur", global_e)
            return {'error': error_msg} 

    def load_file_in_database(self, filename: str):
        """
        Charge un fichier Excel depuis './load_file/{filename}' et insère les données dans la base.
        """
        try:
            # Informations sur le fichier
            print(f"[INFO] Nom du fichier demandé : {filename}")
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            filepath = os.path.join(project_root, 'load_file', filename)
            print(f"[INFO] Chemin complet du fichier : {filepath}")
            
            # Vérification du répertoire courant
            current_dir = os.getcwd()
            print(f"[INFO] Répertoire d'exécution actuel : {current_dir}")
            print(f"[INFO] Répertoire racine du projet : {project_root}")
            print(f"[INFO] Répertoire des fichiers : {os.path.join(project_root, 'load_file')}")
            
            # Liste des fichiers dans le répertoire de chargement
            load_dir = os.path.join(project_root, 'load_file')
            if os.path.exists(load_dir):
                files_in_dir = os.listdir(load_dir)
                print(f"[INFO] Fichiers disponibles dans le répertoire : {files_in_dir}")
            else:
                print(f"[ERREUR] Le répertoire {load_dir} n'existe pas")

            # Vérification de l'existence du fichier
            if not os.path.exists(filepath):
                error_msg = f"[ERREUR] Fichier {filename} introuvable au chemin {filepath}"
                print(error_msg)
                return {'error': error_msg}

            print(f"[INFO] Le fichier existe et sera lu depuis : {filepath}")
            
            # Lecture du fichier avec gestion d'erreur détaillée
            try:
                data = self.read_xlsx_file(filepath)
                if data:
                    print(f"[INFO] Lecture réussie. Nombre de lignes : {len(data)}")
                    print(f"[INFO] Entêtes détectées : {data[0] if data else 'Aucune'}")
                else:
                    error_msg = "[ERREUR] Le fichier a été lu mais ne contient pas de données"
                    print(error_msg)
                    return {'error': error_msg}
            except Exception as read_error:
                error_msg = f"[ERREUR] Lecture du fichier échouée : {str(read_error)}"
                print(error_msg)
                print(f"[DEBUG] Type d'erreur : {type(read_error).__name__}")
                import traceback
                print(f"[DEBUG] Traceback complet : {traceback.format_exc()}")
                return {'error': error_msg}
            
            # Connexion à la base de données
            try:
                print('[INFO] Tentative de connexion à la base de données')
                conn = self.db.connect()
                print('[INFO] Connexion à la base de données établie')
                cursor = conn.cursor()
                print('[INFO] Curseur créé avec succès')
            except Exception as db_error:
                error_msg = f"[ERREUR] Échec de connexion à la base de données : {str(db_error)}"
                print(error_msg)
                import traceback
                print(f"[DEBUG] Traceback complet : {traceback.format_exc()}")
                return {'error': error_msg}

            try:
                headers = data[0]
                table_name = 'etat_des_encours'
                
                    # Vidage de la table
                print(f'[INFO] Vidage de la table {table_name}')
                drop_data_in_table = f'DROP TABLE IF EXISTS `{table_name}`;'
                print(f'[INFO] Requête de vidage : {drop_data_in_table}')
                cursor.execute(drop_data_in_table)
                print('[INFO] Table vidée avec succès')

                # Création de la table
                print(f'[INFO] Création/vérification de la table {table_name}')
                columns = ', '.join([f'`{col}` TEXT' for col in headers])
                
                create_query = f'CREATE TABLE IF NOT EXISTS `{table_name}` ({columns});'
                print(f'[INFO] Requête de création : {create_query}')
                cursor.execute(create_query)
                print('[INFO] Table créée/vérifiée avec succès')
                
            

                # Insertion des données
                print(f'[INFO] Début de l\'insertion des données ({len(data)-1} lignes)')
                for i, row in enumerate(data[1:], 1):
                    try:
                        placeholders = ', '.join(['%s'] * len(row))
                        insert_query = f'INSERT INTO `{table_name}` VALUES ({placeholders})'
                        
                        if i % 100 == 0 or i == 1:
                            print(f'[INFO] Insertion de la ligne {i}/{len(data)-1}')
                            print(f'[DEBUG] Longueur de l\'entête: {len(headers)}, Longueur de la ligne: {len(row)}')
                            if len(headers) != len(row):
                                print(f'[AVERTISSEMENT] La ligne {i} a un nombre différent de colonnes par rapport à l\'entête')
                        
                        cursor.execute(insert_query, row)
                    except Exception as insert_error:
                        error_msg = f"[ERREUR] Échec à l'insertion de la ligne {i} : {str(insert_error)}"
                        print(error_msg)
                        print(f"[DEBUG] Contenu de la ligne problématique : {row}")
                        import traceback
                        print(f"[DEBUG] Traceback : {traceback.format_exc()}")
                        conn.rollback()  # Annulation des modifications
                        return {'error': error_msg}

                # Validation des modifications
                print('[INFO] Validation des modifications (commit)')
                conn.commit()
                print('[INFO] Données insérées avec succès')
                return {'message': 'Success! Data inserted successfully.'}

            except Exception as e:
                error_msg = f"[ERREUR] Exception non gérée : {str(e)}"
                print(error_msg)
                import traceback
                print(f"[DEBUG] Type d'erreur : {type(e).__name__}")
                print(f"[DEBUG] Traceback complet : {traceback.format_exc()}")
                
                # Tentative de rollback en cas d'erreur
                try:
                    conn.rollback()
                    print('[INFO] Rollback effectué')
                except Exception as rollback_error:
                    print(f"[ERREUR] Échec du rollback : {str(rollback_error)}")
                
                return {'error': error_msg}

            finally:
                # Fermeture de la connexion
                try:
                    if 'conn' in locals() and conn:
                        conn.close()
                        print('[INFO] Connexion à la base de données fermée')
                except Exception as close_error:
                    print(f"[ERREUR] Problème lors de la fermeture de la connexion : {str(close_error)}")
        
        except Exception as global_error:
            # Capture les erreurs générales non gérées
            error_msg = f"[ERREUR CRITIQUE] Exception non gérée dans la fonction principale : {str(global_error)}"
            print(error_msg)
            import traceback
            print(f"[DEBUG] Traceback complet : {traceback.format_exc()}")
            return {'error': error_msg}
    def insert_into_echange_credit(self, data): 
        def generate_next_id(cursor):
            cursor.execute("SELECT ID FROM echange_credit ORDER BY ID DESC LIMIT 1")
            last = cursor.fetchone()
            if last and last[0].startswith("SIP"):
                num = int(last[0][3:]) + 1
            else:
                num = 1
            return f"SIP{num:010d}"

        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, "%Y%m%d").date()
            except:
                return None

        try:
            conn = self.db.connect()
            cursor = conn.cursor()

            # Création de la table si elle n'existe pas
            create_table_query = """
            CREATE TABLE IF NOT EXISTS echange_credit (
                ID VARCHAR(20) PRIMARY KEY,
                AGENCE VARCHAR(10),
                AGEC VARCHAR(10),
                COMPTE VARCHAR(20),
                NOM VARCHAR(100),
                CLASST VARCHAR(10),
                CODAPE VARCHAR(10),
                MNTCAHT DECIMAL(18,2),
                CLI_N_A VARCHAR(20),
                NATURE VARCHAR(50),
                TYPECREDIT VARCHAR(50),
                MONTANT DECIMAL(18,2),
                DATECH DATE,
                RANG INT,
                TAUX DECIMAL(5,2),
                DATOUV DATE, 
                group_of VARCHAR(50),
                Date_enreg DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_create BOOLEAN DEFAULT FALSE
            );
            """
            cursor.execute(create_table_query)

            # Champs requis
            required_fields = [
                "Agence", "Agent_de_gestion", "Numero_pret", "Nom_client",
                "arr_status", "Code_Garantie", "Amount", "Secteur_d_activité",
                "Produits", "Total_capital_echus_non_echus", "Date_pret",
                "taux_d_interet", "Date_fin_pret", "linked_appl_id"
            ]
            for field in required_fields:
                if field not in data:
                    return {"error": f"Champ manquant : {field}"}

            # Calcul de CLASST
            arr_status_raw = data.get("arr_status", "")
            classt = {
                "current": "Régulier",
                "arrears": "En Retard"
            }.get(arr_status_raw.lower(), arr_status_raw.upper() if arr_status_raw else "Inconnu")

            # Vérif du compte et calcul de CLI_N_A + RANG
            compte = data["Numero_pret"]
            cursor.execute(
                "SELECT RANG FROM echange_credit WHERE COMPTE = %s ORDER BY Date_enreg DESC LIMIT 1",
                (compte,)
            )
            existing = cursor.fetchone()
            if existing:
                cli_na = 'A'
                rang = existing[0] + 1
            else:
                cli_na = 'N'
                rang = 1

            # Générer ID
            new_id = generate_next_id(cursor)
            type_crd = data['Produits']
            if "AL.AV" in type_crd or "AL.ES" in type_crd:
                type_crd = "CNA"
            else:
                type_crd = "CN"
            # Requête d'insertion
            insert_query = """
            INSERT INTO echange_credit (
                ID, AGENCE, AGEC, COMPTE, NOM, CLASST, CODAPE, MNTCAHT, CLI_N_A,
                NATURE, TYPECREDIT, MONTANT, DATECH, RANG, TAUX, DATOUV, group_of
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            values = (
                new_id,
                data["Agence"],
                data["Agent_de_gestion"],              # AGEC
                compte,
                data["Nom_client"],
                2,
                data["Secteur_d_activité_code"],
                float(data["Chiff_affaire"]),
                cli_na,
                # data["Secteur_d_activité"],
                '',
                type_crd,
                float(data["Amount"]),
                parse_date(data["Date_fin_pret"]),
                rang,
                float(data["taux_d_interet"]),
                parse_date(data["Date_pret"]),
                data["linked_appl_id"]
            )

            cursor.execute(insert_query, values)
            conn.commit()

            print("Ligne insérée avec succès.")
            return {"status": "success", "inserted": 1}

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

        finally:
            if conn:
                conn.close()
