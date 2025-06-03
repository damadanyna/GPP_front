import os
from werkzeug.utils import secure_filename
import openpyxl
from datetime import datetime
import random
import string
from db.db  import DB
import pandas as pd
import re 

class Encours:
    def __init__(self):
        # Dossier où les fichiers seront enregistrés
        self.upload_folder = 'load_file'
        self.db = DB() 
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    # def upload_file(self, file, app_name):
    #     """
    #     Cette méthode permet de télécharger un fichier et de l'enregistrer dans le dossier 'load_file/app'
    #     si un 'app' est fourni, sinon dans 'load_file'.
    #     """
    #     if file and self.allowed_file(file.filename):
    #         filename = secure_filename(file.filename)

    #         # Détermine le chemin du dossier où enregistrer le fichier, selon l'app (ou le dossier par défaut)
    #         folder_path = os.path.join(self.upload_folder, app_name) if app_name else self.upload_folder

    #         # Créer le dossier s'il n'existe pas
    #         os.makedirs(folder_path, exist_ok=True)

    #         filepath = os.path.join(folder_path, filename)
    #         file.save(filepath)

    #         return {'message': 'File successfully uploaded', 'filename': filename}
        
    #     return {'error': 'Invalid file format'}
    
    def upload_file(self, file, app_name): 
        if file and self.allowed_file(file.filename): 
            filename = secure_filename(file.filename)
            folder_path = os.path.join(self.upload_folder, app_name) if app_name else self.upload_folder
            os.makedirs(folder_path, exist_ok=True)
            filepath = os.path.join(folder_path, filename)  
            file.save(filepath)
            return {'message': 'File successfully uploaded', 'filename': filename, 'path': filepath}
 
        return {'error': 'Invalid file format'}
    
    def allowed_file(self, filename):
        """
        Vérifie si l'extension du fichier est autorisée
        """
        ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
        if '.' in filename:
            ext = filename.rsplit('.', 1)[1].lower()
            print("Extension détectée:", ext)
            return ext in ALLOWED_EXTENSIONS
        return False

    def upload_multiple_files(self, files, app_name):
        results = []
        for file in files:
            result = self.upload_file(file, app_name) 
            results.append(result)
        return results


    def show_files(self, app=None): 
        """
        Récupère la liste des fichiers xlsx dans le sous-dossier 'load_file/app'
        et les retourne sous forme d'objets : {"used": False, "file_name": "nom.xlsx"}
        """
        files = []
        
        # Construction du chemin vers le sous-dossier, en utilisant 'app' s'il est fourni
        folder_path = os.path.join(self.upload_folder, app) if app else self.upload_folder

        # Vérifie que le dossier existe
        if not os.path.exists(folder_path):
            return []  # Ou éventuellement retourner une erreur personnalisée

        for filename in os.listdir(folder_path):
            if filename.endswith('.xlsx') or filename.endswith('.XLSX'):
                files.append({
                    "used": False,
                    "file_name": filename
                })
        
        return files
 
    def show_CDI_files(self, app=None): 
        """
        Récupère la liste des fichiers xlsx dans le sous-dossier 'load_file/app'
        et les retourne sous forme d'objets : {"used": False, "file_name": "nom.xlsx"}
        """
        files = []
        
        # Construction du chemin vers le sous-dossier, en utilisant 'app' s'il est fourni
        folder_path = os.path.join(self.upload_folder, app) if app else self.upload_folder

        # Vérifie que le dossier existe
        if not os.path.exists(folder_path):
            return []  # Ou éventuellement retourner une erreur personnalisée

        for filename in os.listdir(folder_path):
            if filename.endswith('.csv') or filename.endswith('.CSV'):
                files.append({
                    "used": False,
                    "file_name": filename
                })
        
        return files
 
    
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
        

    def get_all_cdi_database(self, offset,limit):
        try: 
            conn = self.db.connect()
            cursor = conn.cursor()
            # Offset should be dynamically included in the query
            select_query =f'''SELECT reject.*,
                                (SELECT get_sold_dav(type_sysdate, open_balance, credit_mvmt, debit_mvmt) FROM eb_cont_bal_mcbc_live_full WHERE type_sysdate IS NOT NULL
                                    AND id= (IFNULL(
                                        (SELECT id FROM tmp_rib_indexed WHERE tmp_rib_indexed.rib = reject.OrderingRib),
                                        (SELECT id FROM tmp_rib_indexed WHERE tmp_rib_indexed.rib2 = reject.OrderingRib)
                                    )) ) as solde
                                FROM eb_chq_in  as reject where RejectCode !=""'''
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
    def  get_liste_declarement(self, offset,limit):    
        try: 
            conn = self.db.connect()
            cursor = conn.cursor()
            # Offset should be dynamically included in the query
            select_query = f'SELECT * FROM pj_documents  LIMIT {limit} OFFSET {offset}'
            # select_query = f'SELECT * FROM etat_des_encours'
            
            # Execute the query
            cursor.execute(select_query)
            rows = cursor.fetchall() 
            return rows

        except Exception as global_e:
            error_msg = f"Erreur {global_e}"
            print("Erreur", global_e)
            return {'error': error_msg} 
    def get_liste_cdi(self):
        try: 
            conn = self.db.connect()
            cursor = conn.cursor()
            # Offset should be dynamically included in the query
            select_query = f'SELECT * FROM cdi_encours'
            # select_query = f'SELECT * FROM etat_des_encours'
            
            # Execute the query
            cursor.execute(select_query)
            rows = cursor.fetchall()
        
            return rows

        except Exception as global_e:
            error_msg = f"Erreur {global_e}"
            print("Erreur", global_e)
            return {'error': error_msg} 
        
 
    def get_liste_faites(self):
        try: 
            conn = self.db.connect()
            cursor = conn.cursor()
            # Offset should be dynamically included in the query
            select_query = f'SELECT * FROM echange_credit where is_create=true'  
            # Execute the query
            cursor.execute(select_query)
            rows = cursor.fetchall() 
            return rows 
        except Exception as global_e:
            error_msg = f"Erreur {global_e}"
            print("Erreur", global_e)
            return {'error': error_msg} 
        
 


    def update_group_and_flag(self): 
        def random_string(length=12):
            return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        try:
            conn = self.db.connect()
            cursor = conn.cursor()

            # Génère une seule chaîne aléatoire pour tous les enregistrements mis à jour
            group_value = random_string()

            update_query = """
            UPDATE echange_credit
            SET is_create = true,
                group_of = %s,
                creating_date=%s
            WHERE is_create = false
            """

            cursor.execute(update_query, (group_value,datetime.now()))
            conn.commit()

            print(f"{cursor.rowcount} ligne(s) mise(s) à jour.")
            return {"status": "success", "updated": cursor.rowcount, "group_of": group_value}

        except Exception as e:
            print(f"Erreur lors de la mise à jour : {e}")
            return {"error": str(e)}

        finally:
            if conn:
                conn.close()

    def merge_duplicate_columns(self, headers, data):
        from collections import defaultdict
        column_indices = defaultdict(list)

        for idx, col in enumerate(headers):
            column_indices[col].append(idx)

        unique_headers = list(column_indices.keys())
        merged_data = []
        for row in data[1:]:
            merged_row = []
            for col in unique_headers:
                indices = column_indices[col]
                merged_values = [str(row[i]).strip() for i in indices if i < len(row) and row[i] not in [None, '']]
                merged_row.append(','.join(merged_values))
            merged_data.append(merged_row)

        return unique_headers, merged_data
    
    def nettoyer_nom_fichier(self,filename):
        # Enlever l'extension
        nom_sans_ext = os.path.splitext(filename)[0]
        
        # Remplacer les ponctuations par '_'
        nom_remplace = re.sub(f"[{re.escape(string.punctuation)}]", "_", nom_sans_ext)
        
        # Enlever les chiffres
        nom_sans_chiffres = re.sub(r"\d+", "", nom_remplace)
        
        # Tout en minuscules
        nom_final = nom_sans_chiffres.lower()
        
        # Nettoyage double underscore éventuel
        nom_final = re.sub(r"_+", "_", nom_final).strip("_")
        
        return nom_final
    
    def load_file_in_database(self, filename: str,app_name: str):
        """
        Charge un fichier Excel depuis './load_file/{filename}' et insère les données dans la base.
        """
        reportico_valid_file_name=[
            "account_mcbc_live_full",
            "eb_chq_in_rcp_dtl_mcbc_live_full",
            "aa_bill_details_mcbc_live_full",
            "eb_cont_bal_mcbc_live_full",
            "alternate_account_mcbc_live_full", 
            "chq_rcp_a_valider" 
        ]
        table_name= self.nettoyer_nom_fichier(filename)
        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            folder_path = os.path.join(project_root, 'load_file', app_name)
            filepath = os.path.join(folder_path, filename)
            # Informations sur le fichier 
            # print(f"[INFO] Chemin complet du fichier : {filepath}")
            
            # Vérification du répertoire courant
            current_dir = os.getcwd() 
            
            # Liste des fichiers dans le répertoire de chargement
            load_dir = os.path.join(project_root, 'load_file')
            if os.path.exists(load_dir):
                files_in_dir = os.listdir(load_dir)
                # print(f"[INFO] Fichiers disponibles dans le répertoire : {files_in_dir}")
            else: 
                return {"status": "error","message":f"[ERREUR] Le répertoire {load_dir} n'existe pas"}

            # Vérification de l'existence du fichier
            if not os.path.exists(filepath):
                error_msg = f"[ERREUR] Fichier {filename} introuvable au chemin {filepath}"
                # print(error_msg)
                return {'error': error_msg}

            # print(f"[INFO] Le fichier existe et sera lu depuis : {filepath}")
            
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
                if app_name == 'cdi':
                    table_name = 'eb_chq_in'
                elif app_name == 'gpp':
                    table_name = 'etat_des_encours'
                elif app_name == 'reportico':
                    if not table_name in reportico_valid_file_name:
                        return {"status": "error","message":f"[ERREUR] Nom de fichier invalide {table_name}"} 
                    # Vidage de la table
                drop_data_in_table = f'DROP TABLE IF EXISTS `{table_name}`;'
                cursor.execute(drop_data_in_table)
 
                # === APPLICATION JUSTE AVANT LA CRÉATION DE LA TABLE ===
                headers, data_rows = self.merge_duplicate_columns(headers, data)
                data = [headers] + data_rows
                
                # Création de la table
                columns = ', '.join([f'`{col}` TEXT' for col in headers])
                create_query = f'CREATE TABLE IF NOT EXISTS `{table_name}` ({columns});'
                cursor.execute(create_query)
            
                # Insertion des données
                for i, row in enumerate(data[1:], 1):
                    try:
                        placeholders = ', '.join(['%s'] * len(row))
                        insert_query = f'INSERT INTO `{table_name}` VALUES ({placeholders})'
                        
                        if i % 100 == 0 or i == 1:
                            print(f'[INFO] Insertion de la ligne {i}/{len(data)-1}')
                            print(f'[DEBUG] Longueur de l\'entête: {len(headers)}, Longueur de la ligne: {len(row)}')
                            if len(headers) != len(row): 
                                return {"status": "error","message":f'[AVERTISSEMENT] La ligne {i} a un nombre différent de colonnes par rapport à l\'entête'}
                        cursor.execute(insert_query, row)
                    except Exception as insert_error:
                        error_msg = f"[ERREUR] Échec à l'insertion de la ligne {i} : {str(insert_error)}"
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
        
        
    def clean_filename(filename):
    # Enlever l'extension
        name = os.path.splitext(filename)[0]
        # Remplacer les symboles par _
        name = re.sub(r'[^a-zA-Z0-9]', '_', name)
        # Supprimer les chiffres
        name = re.sub(r'\d+', '', name)
        # Nettoyer les underscores multiples (_ inutile)
        name = re.sub(r'_+', '_', name)
        # Supprimer un éventuel underscore au début/fin
        return name.strip('_')
    
    def read_xlsx_file(self, filepath: str):
        df = pd.read_excel(filepath, dtype=str, engine='openpyxl')

        # Supprimer les colonnes ayant des noms dupliqués, ne garder que la première occurrence
        df = df.loc[:, ~df.columns.duplicated(keep='first')]

        # Convertir le DataFrame en liste
        data = [df.columns.tolist()] + df.fillna('').values.tolist()
        return data


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
                GENRE VARCHAR(10),
                Creating_date DATETIME,
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
            
            if data["Chiff_affaire"]  == ' ' or data["Chiff_affaire"]  is None:
                data["Chiff_affaire"] =0 
            print('type_crd', data["Chiff_affaire"])
            if "AL.AV" in type_crd or "AL.ES" in type_crd:
                type_crd = "CNA"
            else:
                type_crd = "CA"
            # Requête d'insertion
            insert_query = """
            INSERT INTO echange_credit (
                ID, AGENCE, AGEC, COMPTE, NOM, CLASST, CODAPE, MNTCAHT, CLI_N_A,
                NATURE, TYPECREDIT, MONTANT, DATECH, RANG, TAUX, DATOUV,GENRE,creating_date, group_of
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s
            )
            """
            values = (
                new_id,
                data["Agence"],
                "EI",              # AGEC
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
                data["Genre"],
                '',
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

    def insert_into_echange_cdi(self, data):   
        
        print("Code de l'établissement:" ,data["Référence de la pièce justificative (PJ)"])
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
            CREATE TABLE IF NOT EXISTS cdi_encours (
                id INT AUTO_INCREMENT PRIMARY KEY,
                code_etablissement VARCHAR(20),
                code_agence VARCHAR(20),
                ordering_rib VARCHAR(34),
                identification_tiers TEXT,
                identification_contrevenants TEXT,
                type_moyen_paiement VARCHAR(50),
                numero_moyen_paiement VARCHAR(50),
                montant_moyen_paiement DECIMAL(15, 2),
                date_emission text,
                date_presentation text,
                date_echeance text,
                identification_beneficiaire VARCHAR(100),
                nom_beneficiaire VARCHAR(100),
                nom_banque_presentateur VARCHAR(100),
                motif_refus TEXT,
                solde_compte_rejet DECIMAL(15, 2),
                sens_solde VARCHAR(10),
                reference_effet_impaye VARCHAR(50),
                reference_lettre_injonction VARCHAR(50),
                date_lettre_injonction text,
                reference_envoi_lettre_injonction VARCHAR(50),
                date_envoi_lettre_injonction text,
                existence_pj BOOLEAN,
                date_pj text,
                reference_pj VARCHAR(100),
                filler2 VARCHAR(100),
                filler3 VARCHAR(100),
                filler4 TEXT,
                filler5 TEXT,
                Creating_date DATETIME,
                group_of VARCHAR(50),
                Date_enreg DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_create VARCHAR(50)
            );

            """
            cursor.execute(create_table_query)

            
            # Requête d'insertion
            insert_query = """
            INSERT INTO cdi_encours (
               code_etablissement,code_agence,ordering_rib,identification_tiers,identification_contrevenants,
              type_moyen_paiement,numero_moyen_paiement,montant_moyen_paiement,date_emission,date_presentation,
              date_echeance,identification_beneficiaire,nom_beneficiaire,nom_banque_presentateur,motif_refus,solde_compte_rejet,
              sens_solde,reference_effet_impaye,reference_lettre_injonction,date_lettre_injonction,reference_envoi_lettre_injonction,
              date_envoi_lettre_injonction,existence_pj,date_pj,reference_pj,filler2,filler3,filler4,filler5,Creating_date,group_of,is_create
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );

            """
             
            values = ( 
                    data["Code de l'établissement"],                          # code_etablissement
                    data["Code de l'Agence"],                                 # code_agence
                    data["OrderingRib"],                                      # ordering_rib
                    data["Identification de(s) tiers contrevenant(s)"],       # identification_tiers
                    data["Identification du 1er, 2è, … contrevenants mandataires signataires"],  # identification_contrevenants
                    data["Type du moyen de paiement"],                        # type_moyen_paiement
                    data["Numéro du moyen de paiement"],                      # numero_moyen_paiement
                    data["Montant du moyen de paiement"],                       # montant_moyen_paiement
                    data["Date d’émission"],                      # date_emission
                    data["Date de présentation"],                 # date_presentation
                    data["Date d’échéance"],                      # date_echeance
                    data["Identification du bénéficiaire"],                   # identification_beneficiaire
                    data["Nom du bénéficiaire"],                              # nom_beneficiaire
                    data["Nom de la Banque présentateur "],                   # nom_banque_presentateur
                    data["Motif du refus"],                                   # motif_refus
                    data["Solde du compte au moment de rejet"],     # solde_compte_rejet
                    data["Sens du solde"],                                    # sens_solde
                    data["Référence de l’effet impayé"],                      # reference_effet_impaye
                    data["Référence de la lettre d’injonction (LI)"],         # reference_lettre_injonction
                    data["Date d’établissement de la lettre d’injonction"],  # date_lettre_injonction
                    data["Référence envoi de la lettre d’injonction"],        # reference_envoi_lettre_injonction
                    data["Date d’envoi de la lettre d’injonction"],  # date_envoi_lettre_injonction
                    data["Existence de la pièce justificative (PJ)"],  # existence_pj
                    data["Date de la pièce justificative"],       # date_pj
                    data["Référence de la pièce justificative (PJ)"],         # reference_pj
                    data["FILLER2"],                                          # filler2
                    data["FILLER3"],                                          # filler3
                    data["FILLER4"],                                          # filler4
                    data["FILLER5"],                                          # filler5
                    datetime.now(),                                           # Creating_date
                    '',                    # group_of (clé à définir dans le dict si utile)
                    False       
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


    def insert_into_declaration(self, data):  
        print(data)
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
                CREATE TABLE IF NOT EXISTS  pj_documents (
                    ID INT AUTO_INCREMENT PRIMARY KEY,
                    nom_dossier VARCHAR(100),        
                    numero_dossier VARCHAR(50),        
                    date_creation VARCHAR(50),                
                    filler1 TEXT,                      
                    pj_ar VARCHAR(255),                
                    pj_cnp VARCHAR(255),               
                    pj_anr VARCHAR(255),               
                    filler2 TEXT,                      
                    filler3 TEXT,                      
                    filler4 TEXT,
                    Date_enreg DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_create VARCHAR(50)                      
                );  """
            cursor.execute(create_table_query) 
            # Requête d'insertion
            insert_query = """
            INSERT INTO pj_documents (
                nom_dossier,
                numero_dossier,
                date_creation,
                filler1,
                pj_ar,
                pj_cnp,
                pj_anr,
                filler2,
                filler3,
                filler4,
                Date_enreg,
                is_create
            ) VALUES (
                %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            );   """
            values = ( 
                    data["nom_dossier"],
                    data["numero_dossier"],
                    data["date_creation"],
                    data["filler1"],
                    data["pj_ar"],
                    data["pj_cnp"],
                    data["pj_anr"],
                    data["filler2"],
                    data["filler3"],
                    data["filler4"], 
                    datetime.now(),                                           # Creating_date
                    '',         
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
                
    def run_initialisation_sql(self):
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            create_table_query ="""
                CREATE TABLE IF NOT EXISTS init_status (
                    name VARCHAR(255) PRIMARY KEY,  
                    status VARCHAR(20) NOT NULL,   
                    message TEXT,                  
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                );"""

            cursor.execute(create_table_query)
            
            steps = [ 
                     
                {
                    "name": "drop_table_tmp_rib_indexed",
                    "sql": """
                        drop table if exists tmp_rib_indexed ;
                    """
                },
                {
                    "name": "create_find_matching_positions",
                    "sql": """
                        CREATE FUNCTION IF NOT EXISTS find_matching_positions(type_sysdate TEXT, prefixes TEXT)
                        RETURNS TEXT
                        DETERMINISTIC
                        BEGIN
                            DECLARE token TEXT;
                            DECLARE remaining TEXT;
                            DECLARE result TEXT DEFAULT '';
                            DECLARE position INT DEFAULT 0;
                            DECLARE sep_pos INT;

                            SET remaining = type_sysdate;

                            WHILE LENGTH(remaining) > 0 DO
                                SET sep_pos = LOCATE('|', remaining);
                                IF sep_pos = 0 THEN
                                    SET token = remaining;
                                    SET remaining = '';
                                ELSE
                                    SET token = LEFT(remaining, sep_pos - 1);
                                    SET remaining = SUBSTRING(remaining, sep_pos + 1);
                                END IF;

                                IF FIND_IN_SET(token, prefixes) > 0 THEN
                                    SET result = CONCAT(result, ',', position);
                                END IF;

                                SET position = position + 1;
                            END WHILE;

                            RETURN result;
                        END
                    """
                },
                {
                    "name": "create_get_capital_non_appele",
                    "sql": """ 
                            CREATE FUNCTION get_capital_non_appele(type_sysdate TEXT, open_balance TEXT, credit_mvmt TEXT, debit_mvmt TEXT)
                            RETURNS DECIMAL(20,2)
                            DETERMINISTIC
                            BEGIN
                                DECLARE pos TEXT;
                                SET pos = find_matching_positions(type_sysdate, 'CURACCOUNT,DUEACCOUNT');
                                RETURN
                                    IFNULL(sum_values_at_positions_(open_balance, pos), 0) +
                                    IFNULL(sum_values_at_positions_(credit_mvmt, pos), 0) +
                                    IFNULL(sum_values_at_positions_(debit_mvmt, pos), 0);
                            END
                    """
                },
                {
                    "name": "create_get_capital_appele",
                    "sql": """ 
                            CREATE FUNCTION get_capital_appele(type_sysdate TEXT, open_balance TEXT, credit_mvmt TEXT, debit_mvmt TEXT)
                            RETURNS DECIMAL(20,2)
                            DETERMINISTIC
                            BEGIN
                                DECLARE pos TEXT;
                                SET pos = find_matching_positions(type_sysdate, 'PA1ACCOUNT,PA2ACCOUNT,PA3ACCOUNT,PA4ACCOUNT');
                                RETURN
                                    IFNULL(sum_values_at_positions_(open_balance, pos), 0) +
                                    IFNULL(sum_values_at_positions_(credit_mvmt, pos), 0) +
                                    IFNULL(sum_values_at_positions_(debit_mvmt, pos), 0);
                            END
                    """
                },
                {
                    "name": "create_sum_values_at_positions",
                    "sql": """
                        CREATE FUNCTION IF NOT EXISTS sum_values_at_positions_(values_str TEXT, positions_str TEXT)
                        RETURNS DECIMAL(20,2)
                        DETERMINISTIC
                        BEGIN
                            DECLARE total DECIMAL(20,2) DEFAULT 0;
                            DECLARE current_index INT DEFAULT 0;
                            DECLARE val TEXT;
                            DECLARE sep_pos INT;

                            SET values_str = CONCAT(values_str, '|');
                            SET sep_pos = LOCATE('|', values_str);

                            WHILE sep_pos > 0 DO
                                SET val = SUBSTRING(values_str, 1, sep_pos - 1);

                                IF LOCATE(CONCAT(',', current_index, ','), CONCAT(',', positions_str, ',')) > 0 THEN
                                    IF val IS NOT NULL AND val != '' THEN
                                        SET total = total + CAST(val AS DECIMAL(20,2));
                                    END IF;
                                END IF;

                                SET values_str = SUBSTRING(values_str, sep_pos + 1);
                                SET sep_pos = LOCATE('|', values_str);
                                SET current_index = current_index + 1;
                            END WHILE;

                            RETURN total;
                        END
                    """
                },
                {
                    "name": "create_get_capital_total",
                    "sql": """
                        CREATE FUNCTION IF NOT EXISTS get_capital_TOTAL(type_sysdate TEXT, open_balance TEXT, credit_mvmt TEXT, debit_mvmt TEXT)
                        RETURNS DECIMAL(20,2)
                        DETERMINISTIC
                        BEGIN 
                            DECLARE pos TEXT;
                            DECLARE total DECIMAL(20,2);

                            SET pos = find_matching_positions(type_sysdate, 'CURACCOUNT,DUEACCOUNT,PA1ACCOUNT,PA2ACCOUNT,PA3ACCOUNT,PA4ACCOUNT');

                            SET total = 
                                IFNULL(sum_values_at_positions_(open_balance, pos), 0) +
                                IFNULL(sum_values_at_positions_(credit_mvmt, pos), 0) +
                                IFNULL(sum_values_at_positions_(debit_mvmt, pos), 0);

                            RETURN total;
                        END
                    """
                },
                {
                    "name": "create_get_sold_dav",
                    "sql": """
                        CREATE FUNCTION get_sold_dav(type_sysdate TEXT, open_balance TEXT, credit_mvmt TEXT, debit_mvmt TEXT)
                        RETURNS DECIMAL(20,2)
                        DETERMINISTIC
                        BEGIN
                            DECLARE pos TEXT;
                            SET pos = find_matching_positions(type_sysdate, 'CURACCOUNT');
                            RETURN
                                IFNULL(sum_values_at_positions_(open_balance, pos), 0) +
                                IFNULL(sum_values_at_positions_(credit_mvmt, pos), 0) +
                                IFNULL(sum_values_at_positions_(debit_mvmt, pos), 0);
                        END
                    """
                },
                {
                    "name": "create_tmp_rib_indexed_table",
                    "sql": """
                        CREATE TABLE IF NOT EXISTS tmp_rib_indexed (
                            id VARCHAR(255),
                            rib VARCHAR(50),
                            rib2 VARCHAR(50),
                            INDEX (rib)
                        );
                    """
                },
                {
                    "name": "insert_tmp_rib_indexed",
                    "sql": """
                        INSERT INTO tmp_rib_indexed (id, rib, rib2)
                        SELECT 
                            id,
                            SUBSTRING_INDEX(SUBSTRING_INDEX(alt_acct_id, '|', -1), '|', 1) AS rib,
                            SUBSTRING_INDEX(SUBSTRING_INDEX(alt_acct_id, '|', -2), '|', 1) AS rib2
                        FROM 
                            account_mcbc_live_full
                    """
                },
                {
                    "name": "index_rib",
                    "sql": "CREATE INDEX IF NOT EXISTS idx_tmp_rib_rib ON tmp_rib_indexed(rib)"
                },
                {
                    "name": "idx_tmp_rib_rib2",
                    "sql": "CREATE INDEX IF NOT EXISTS idx_tmp_rib_rib2 ON tmp_rib_indexed(rib2)"
                },
                {
                    "name": "idx_eb_cont_bal_id_sysdate",
                    "sql": "CREATE INDEX IF NOT EXISTS idx_eb_cont_bal_id_sysdate ON eb_cont_bal_mcbc_live_full(id)"
                },
                {
                    "name": "idx_eb_chq_orderingrib",
                    "sql": "CREATE INDEX IF NOT EXISTS idx_eb_chq_orderingrib ON eb_chq_in_rcp_dtl_mcbc_live_full(orderingrib)"
                }
            ]

            status_report = []

            cursor.execute("DELETE FROM init_status")
            for step in steps:
                name = step["name"] 

                cursor.execute("SELECT status FROM init_status WHERE name = %s", (name,))
                existing = cursor.fetchone()
                if existing and existing[0] == "done":
                    status_report.append({"name": name, "status": "skipped"})
                    continue

                try: 
                    cursor.execute(step["sql"])
                    cursor.execute(
                        "REPLACE INTO init_status (name, status, message) VALUES (%s, %s, %s)",
                        (name, "done", "OK")
                    )
                    status_report.append({"name": name, "status": "done"})
                except Exception as e:
                    cursor.execute(
                        "REPLACE INTO init_status (name, status, message) VALUES (%s, %s, %s)",
                        (name, "error", str(e))
                    )
                    status_report.append({"name": name, "status": "error", "message": str(e)})

            conn.commit()
            return status_report

        except Exception as e:
            return [{"name": "init_sql", "status": "fatal", "message": str(e)}]
