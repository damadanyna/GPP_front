import os
from werkzeug.utils import secure_filename
import openpyxl
from datetime import datetime
import random
import string
from db.db  import DB
import pandas as pd
import re 
import csv
import json
import sys 
import tempfile
import shutil
from werkzeug.utils import secure_filename

import logging
import time

class Encours:
    def __init__(self):
        # Dossier où les fichiers seront enregistrés
        self.upload_folder = 'load_file'
        self.db = DB() 
        
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
        
 
    
    def upload_file(self, file, app_name, folder_name=None):
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Construction du chemin dossier
            if folder_name:
                folder = os.path.join(app_name, folder_name) if app_name else folder_name
            else:
                folder = app_name
            
            folder_path = os.path.join(self.upload_folder, folder) if folder else self.upload_folder
            os.makedirs(folder_path, exist_ok=True)

            filepath = os.path.join(folder_path, filename)
            file.save(filepath)

            return {
                'message': 'File successfully uploaded',
                'filename': filename,
                'path': filepath
            }

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

    def upload_file_manual_in_detail(self, file, app_name, folder_name=None, current=None, total=None):
        
    # Configurer le logging
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        logger.info(f"=== DÉBUT UPLOAD: {file.filename if file else 'None'} ===")
        
        if not file or not self.allowed_file(file.filename):
            logger.error(f"Fichier invalide: {file}")
            yield {"status": "error", "file": str(file), "message": "Format invalide"}
            return

        filename = secure_filename(file.filename)
        logger.info(f"Nom sécurisé: {filename}")
        
        # Construire le chemin de destination
        if folder_name:
            folder = os.path.join(app_name, folder_name) if app_name else folder_name
        else:
            folder = app_name
        folder_path = os.path.join(self.upload_folder, folder) if folder else self.upload_folder
        os.makedirs(folder_path, exist_ok=True)
        logger.info(f"Dossier créé: {folder_path}")

        final_filepath = os.path.join(folder_path, filename)
        backup_filepath = None
        logger.info(f"Chemin final: {final_filepath}")
        
        try:
            # Créer un backup si le fichier existe déjà
            if os.path.exists(final_filepath):
                backup_filepath = final_filepath + '.backup'
                shutil.copy2(final_filepath, backup_filepath)
                logger.info(f"Backup créé: {backup_filepath}")
            
            chunk_size = 1024 * 1024  # 1 MB
            total_size = 0
            chunk_count = 0

            # Récupérer la taille attendue du fichier
            total_expected_size = 0
            try:
                file.stream.seek(0, 2)
                total_expected_size = file.stream.tell()
                file.stream.seek(0)
                logger.info(f"Taille attendue: {total_expected_size} octets")
            except Exception as e:
                logger.warning(f"Impossible de déterminer la taille: {e}")
                yield {
                    "status": "warning", 
                    "file": filename,
                    "message": f"Impossible de déterminer la taille du fichier: {str(e)}"
                }

            # Ouvrir le fichier de destination
            logger.info("Ouverture du fichier de destination...")
            with open(final_filepath, 'wb') as f:
                logger.info("Fichier ouvert, début de la lecture...")
                
                while True:
                    try:
                        # Ajouter un timeout sur la lecture
                        start_time = time.time()
                        chunk = file.stream.read(chunk_size)
                        read_time = time.time() - start_time
                        
                        if not chunk:
                            logger.info(f"Fin de lecture après {chunk_count} chunks")
                            break
                        
                        chunk_count += 1
                        logger.debug(f"Chunk {chunk_count}: {len(chunk)} octets lus en {read_time:.2f}s")
                        
                        # Détecter une lecture anormalement lente (connexion coupée)
                        if read_time > 30:  # Plus de 30 secondes pour lire 1MB
                            logger.warning(f"Lecture très lente détectée: {read_time:.2f}s")
                            yield {
                                "status": "warning",
                                "file": filename,
                                "message": f"Connexion lente détectée ({read_time:.1f}s pour {len(chunk)} octets)"
                            }
                        
                        # Écrire le chunk
                        start_write = time.time()
                        bytes_written = f.write(chunk)
                        write_time = time.time() - start_write
                        
                        if bytes_written != len(chunk):
                            error_msg = f"Erreur d'écriture: {bytes_written} octets écrits au lieu de {len(chunk)}"
                            logger.error(error_msg)
                            raise IOError(error_msg)
                        
                        logger.debug(f"Chunk {chunk_count}: {bytes_written} octets écrits en {write_time:.3f}s")
                        
                        # Forcer l'écriture sur disque tous les 10 chunks
                        if chunk_count % 10 == 0:
                            f.flush()
                            logger.debug(f"Flush effectué après {chunk_count} chunks")
                        
                        total_size += len(chunk)

                        yield {
                            "status": "progress",
                            "file": filename,
                            "current": current,
                            "total": total,
                            "received_mb": round(total_size / (1024 * 1024), 2),
                            "total_mb": round(total_expected_size / (1024 * 1024), 2) if total_expected_size else None,
                            "percentage_file": round((total_size / total_expected_size) * 100, 2) if total_expected_size else None,
                            "message": f"[Serveur] Reçu {total_size / (1024 * 1024):.2f} MB... (chunk {chunk_count})",
                            "chunk_count": chunk_count,
                            "read_time": round(read_time, 2),
                            "write_time": round(write_time, 3)
                        }
                        
                    except Exception as e:
                        logger.error(f"Erreur sur chunk {chunk_count}: {e}")
                        
                        # Restaurer le backup en cas d'erreur
                        if backup_filepath and os.path.exists(backup_filepath):
                            logger.info("Restauration du backup...")
                            f.close()  # Fermer le fichier avant de le remplacer
                            shutil.move(backup_filepath, final_filepath)
                            backup_filepath = None
                        
                        yield {
                            "status": "error",
                            "file": filename,
                            "message": f"Erreur durant le transfert (chunk {chunk_count}): {str(e)}"
                        }
                        return

                # Synchronisation finale
                logger.info("Synchronisation finale...")
                f.flush()
                os.fsync(f.fileno())
                logger.info("Synchronisation terminée")

            # Vérification de l'intégrité
            logger.info(f"Vérification: {total_size} reçus / {total_expected_size} attendus")
            if total_expected_size > 0 and total_size != total_expected_size:
                logger.error(f"Transfert incomplet: {total_size} != {total_expected_size}")
                
                # Restaurer le backup
                if backup_filepath and os.path.exists(backup_filepath):
                    logger.info("Restauration du backup pour transfert incomplet")
                    shutil.move(backup_filepath, final_filepath)
                    backup_filepath = None
                
                yield {
                    "status": "error",
                    "file": filename,
                    "message": f"Transfert incomplet: {total_size} octets reçus au lieu de {total_expected_size}"
                }
                return

            # Vérifier que le fichier existe et a la bonne taille
            if os.path.exists(final_filepath):
                actual_size = os.path.getsize(final_filepath)
                logger.info(f"Fichier final: {actual_size} octets sur disque")
                
                if actual_size != total_size:
                    logger.error(f"Taille sur disque incorrecte: {actual_size} != {total_size}")
                    yield {
                        "status": "error",
                        "file": filename,
                        "message": f"Erreur: taille sur disque ({actual_size}) différente de celle reçue ({total_size})"
                    }
                    return
            else:
                logger.error("Le fichier final n'existe pas!")
                yield {
                    "status": "error",
                    "file": filename,
                    "message": "Erreur: le fichier n'a pas été créé sur le serveur"
                }
                return

            # Succès - supprimer le backup
            if backup_filepath and os.path.exists(backup_filepath):
                os.remove(backup_filepath)
                logger.info("Backup supprimé")

            logger.info(f"=== SUCCÈS: {filename} ({total_size} octets, {chunk_count} chunks) ===")
            yield {
                "status": "success",
                "file": filename,
                "received_mb": round(total_size / (1024 * 1024), 2),
                "chunk_count": chunk_count,
                "message": f"✅ Fichier {filename} transféré avec succès ({total_size / (1024 * 1024):.2f} MB, {chunk_count} chunks)"
            }

        except Exception as e:
            logger.error(f"Erreur générale: {e}", exc_info=True)
            
            # Restaurer le backup en cas d'erreur générale
            if backup_filepath and os.path.exists(backup_filepath):
                try:
                    logger.info("Restauration du backup (erreur générale)")
                    shutil.move(backup_filepath, final_filepath)
                except Exception as restore_error:
                    logger.error(f"Erreur lors de la restauration: {restore_error}")
            
            yield {
                "status": "error",
                "file": filename,
                "message": f"Erreur lors de l'upload: {str(e)}"
            }
        
        finally:
            # Nettoyer le backup s'il reste
            if backup_filepath and os.path.exists(backup_filepath):
                try:
                    os.remove(backup_filepath)
                    logger.info("Backup nettoyé dans finally")
                except Exception as cleanup_error:
                    logger.error(f"Erreur nettoyage backup: {cleanup_error}")
            
            logger.info(f"=== FIN UPLOAD: {filename} ===")
    def upload_multiple_files(self, files, app_name, folder_name=None):
        total = len(files)
        for i, file in enumerate(files, 1):
            try:
                # Itérer sur le générateur et yield chaque dictionnaire produit
                for progress in self.upload_file_manual_in_detail(file, app_name, folder_name, i, total):
                    yield progress
            except Exception as e:
                yield {
                    "status": "error",
                    "file": file.filename if hasattr(file, "filename") else str(file),
                    "current": i,
                    "total": total,
                    "percentage": round((i / total) * 100, 2),
                    "message": f"[ERREUR] Échec du téléchargement de {file} : {str(e)}"
                }




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
        Renvoie une structure arborescente des sous-dossiers de `upload_folder/app`
        compatible avec Vuetify <v-treeview>, sans inclure le dossier racine.
        """
        import os

        base_folder = os.path.join(self.upload_folder, app) if app else self.upload_folder

        if not os.path.exists(base_folder):
            return []

        tree = []

        for root, dirs, files in os.walk(base_folder):
            # On saute la racine : on ne veut afficher que les sous-dossiers
            if root == base_folder:
                continue

            relative_path = os.path.relpath(root, base_folder).replace("\\", "/")
            path_parts = relative_path.split('/') if relative_path != '.' else []

            # Liste des fichiers CSV
            csv_files = [
                {"title": f, "file": True}
                for f in files
                if f.lower().endswith('.csv')
            ]

            if not csv_files:
                continue  # On ignore les dossiers sans fichiers CSV

            # Construction arborescente
            current_level = tree
            for part in path_parts:
                folder = next((item for item in current_level if item["title"] == part and not item.get("file")), None)
                if not folder:
                    folder = {"title": part, "children": []}
                    current_level.append(folder)
                current_level = folder["children"]

            current_level.extend(csv_files)

        return tree


 
    
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
    
    
    
    # def load_file_csv_in_database(self, filename: str, app_name: str,folder:str):
         
    #         folder_path = os.path.join(project_root, 'load_file', app_name,folder)
        
    def load_file_csv_in_database(self, filename: str, app_name: str, folder: str):
        """
        Charge un fichier CSV depuis './load_file/{filename}' avec séparateur '^' 
        et insère les données dans la base avec progression en temps réel.
        """
        
        def progress_generator():
            table_name = self.nettoyer_nom_fichier(filename)  
            try:
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                folder_path = os.path.join(project_root, 'load_file', app_name, folder)
                
                # Recherche du fichier dans le répertoire
                if not os.path.exists(folder_path):
                    yield json.dumps({"status": "error", "message": f"[ERREUR] Le répertoire {folder_path} n'existe pas",
                        "task": "Le répertoire {folder_path} n'existe pas"})
                    return  
                
                # Liste tous les fichiers du répertoire
                files_in_dir = os.listdir(folder_path)
                yield json.dumps({"status": "info", "message": f"[INFO] Fichiers disponibles dans le répertoire : {files_in_dir}"})
                
                # Recherche du fichier (exact ou partiel)
                found_file = None
                for file in files_in_dir:
                    if file == filename or file.startswith(filename.split('.')[0]):
                        found_file = file
                        break
                
                if not found_file:
                    yield json.dumps({"status": "error", "message": f"[ERREUR] Fichier {filename} introuvable dans {folder_path}",
                                      "task": " Fichier {filename} introuvable dans"})
                    return  
                
                filepath = os.path.join(folder_path, found_file)
                yield json.dumps({"status": "info", "message": f"[INFO] Fichier trouvé : {found_file}"})
                yield json.dumps({"status": "info", "message": f"[INFO] Chemin complet du fichier : {filepath}"})
                
                # Lecture du fichier CSV avec séparateur '^'
                try:
                    data = []
                    yield json.dumps({"status": "info", "message": "[INFO] Début de la lecture du fichier CSV..."
                                      ,  "task": "Début de la lecture du fichier CSV."})
                    
                    with open(filepath, 'r', encoding='utf-8', newline='') as csvfile:
                        # Utilisation du séparateur '^'
                        csv_reader = csv.reader(csvfile, delimiter='^')
                        is_header = True
                        row_count = 0
                        
                        for row in csv_reader:
                            if is_header:
                                # Traitement spécial pour l'en-tête (première ligne)
                                cleaned_row = []
                                for i, cell in enumerate(row):
                                    # Nettoyage, remplacement des points par underscores et mise en minuscules
                                    cleaned_cell = cell.strip().replace('.', '_').lower()
                                    
                                    # Si la cellule est vide après nettoyage, créer un nom par défaut
                                    if not cleaned_cell or cleaned_cell == '':
                                        cleaned_cell = f'colonne_{i+1}'
                                    
                                    # Vérifier que le nom ne contient que des caractères valides
                                    # Remplacer les caractères spéciaux par des underscores
                                    cleaned_cell = ''.join(c if c.isalnum() or c == '_' else '_' for c in cleaned_cell)
                                    
                                    # S'assurer que le nom ne commence pas par un chiffre
                                    if cleaned_cell and cleaned_cell[0].isdigit():
                                        cleaned_cell = f'col_{cleaned_cell}'
                                    
                                    cleaned_row.append(cleaned_cell)
                                is_header = False
                            else:
                                # Nettoyage standard pour les données
                                cleaned_row = [cell.strip() for cell in row]
                                row_count += 1
                                
                                # Progression de lecture toutes les 1000 lignes
                                if row_count % 1000 == 0:
                                    yield json.dumps({
                                        "status": "reading", 
                                        # "progress": row_count, 
                                        "task": "Lecture encours",
                                        "row_count":row_count
                                    })
                                    yield json.dumps({
                                        "status": "info", 
                                        "message": f"[INFO] Lecture en cours. Ligne : {row_count}"
                                    })
                            
                            data.append(cleaned_row)
                    
                    if data:
                        yield json.dumps({
                            "status": "info", 
                            "message": f"[INFO] Lecture réussie. Nombre de lignes : {len(data)}"
                        })
                        yield json.dumps({
                            "status": "info", 
                            "message": f"[INFO] Entêtes détectées : {data[0] if data else 'Aucune'}"
                        })
                    else:
                        yield json.dumps({"status": "error", "message": "[ERREUR] Le fichier a été lu mais ne contient pas de données"})
                        return {"status": "error", "message": "[ERREUR] Le fichier a été lu mais ne contient pas de données"}
                        
                except Exception as read_error:
                    yield json.dumps({
                        "status": "error", 
                        "message": f"[ERREUR] Lecture du fichier CSV échouée : {str(read_error)}"
                    })
                    return {
                        "status": "error", 
                        "message": f"[ERREUR] Lecture du fichier CSV échouée : {str(read_error)}"
                    }
                
                # Connexion à la base de données
                try:
                    yield json.dumps({"status": "info", "message": "[INFO] Tentative de connexion à la base de données"})
                    conn = self.db.connect()
                    yield json.dumps({"status": "info", "message": "[INFO] Connexion à la base de données établie"})
                    cursor = conn.cursor()
                    yield json.dumps({"status": "info", "message": "[INFO] Curseur créé avec succès"})
                except Exception as db_error:
                    yield json.dumps({
                        "status": "error", 
                        "message": f"[ERREUR] Échec de connexion à la base de données : {str(db_error)}"
                    })
                    return {
                        "status": "error", 
                        "message": f"[ERREUR] Échec de connexion à la base de données : {str(db_error)}"
                    }

                try:
                    headers = data[0]
                    
                    # Vérification supplémentaire des en-têtes
                    yield json.dumps({
                        "status": "debug", 
                        "message": f"[DEBUG] En-têtes avant traitement : {headers}"
                    })
                    
                    # Vérifier qu'aucun en-tête n'est vide
                    for i, header in enumerate(headers):
                        if not header or header.strip() == '':
                            headers[i] = f'colonne_{i+1}'
                            yield json.dumps({
                                "status": "warning", 
                                "message": f"[WARNING] En-tête vide détecté à la position {i}, remplacé par 'colonne_{i+1}'"
                            })
                    
                    # Vérifier les doublons dans les en-têtes
                    seen_headers = {}
                    for i, header in enumerate(headers):
                        if header in seen_headers:
                            counter = 1
                            original_header = header
                            while f"{original_header}_{counter}" in seen_headers:
                                counter += 1
                            headers[i] = f"{original_header}_{counter}"
                            yield json.dumps({
                                "status": "warning", 
                                "message": f"[WARNING] En-tête dupliqué '{original_header}' renommé en '{headers[i]}'"
                            })
                        seen_headers[headers[i]] = i
                    
                    yield json.dumps({
                        "status": "debug", 
                        "message": f"[DEBUG] En-têtes après nettoyage : {headers}" ,
                        "task": "En-têtes après nettoyage"
                    })
                    
                    # Vidage de la table
                    yield json.dumps({"status": "info", "message": f"[INFO] Suppression de la table existante {table_name}...","task":"Suppression de la table existante" })
                    drop_data_in_table = f'DROP TABLE IF EXISTS `{table_name}`;'
                    cursor.execute(drop_data_in_table)

                    # === APPLICATION JUSTE AVANT LA CRÉATION DE LA TABLE ===
                    yield json.dumps({"status": "info", "message": "[INFO] Traitement des colonnes dupliquées..."})
                    headers, data_rows = self.merge_duplicate_columns(headers, data[1:])
                    
                    # Création de la table avec les colonnes nettoyées
                    columns = ', '.join([f'`{col}` TEXT' for col in headers])
                    yield json.dumps({
                        "status": "info", 
                        "message": f"[INFO] Colonnes de la table : {len(headers)} colonnes"
                    })
                    
                    create_query = f'CREATE TABLE IF NOT EXISTS `{table_name}` ({columns});'
                    cursor.execute(create_query)
                    yield json.dumps({"status": "info", "message": f"[INFO] Table `{table_name}` créée avec succès"})
                
                    # Insertion des données avec progression INSTANTANÉE
                    total_rows = len(data_rows)
                    yield json.dumps({
                        "status": "start_insert", 
                        "task": "Debut de l'insertion",
                        "total_rows": total_rows,
                        "message": f"[INFO] Début de l'insertion de {total_rows} lignes..."
                    })
                    
                    for i, row in enumerate(data_rows, 1):
                        try:
                            # S'assurer que la ligne a le bon nombre de colonnes
                            while len(row) < len(headers):
                                row.append('')  # Ajouter des valeurs vides si nécessaire
                            
                            # Tronquer si trop de colonnes
                            if len(row) > len(headers):
                                row = row[:len(headers)]
                            
                            placeholders = ', '.join(['%s'] * len(headers))
                            insert_query = f'INSERT INTO `{table_name}` VALUES ({placeholders})'
                            
                            # PROGRESSION INSTANTANÉE toutes les 100 lignes
                            if i % 100 == 0 or i == 1:
                                progress_data = {
                                    "status": "inserting",
                                    "current": i,
                                    "total": total_rows,
                                    "percentage": round((i / total_rows) * 100, 2),
                                    "row_count":i,
                                    "task": "insertion",
                                    "message": f"[INFO] Insertion de la ligne {i}/{total_rows}",
                                    "debug": f"[DEBUG] Longueur de l'entête: {len(headers)}, Longueur de la ligne: {len(row)}"
                                }
                                yield json.dumps(progress_data)
                                
                                # CRUCIAL: Forcer l'envoi immédiat
                                sys.stdout.flush()
                            
                            cursor.execute(insert_query, row)
                            
                        except Exception as insert_error:
                            yield json.dumps({
                                "status": "error",
                                "message": f"[ERREUR] Échec à l'insertion de la ligne {i} : {str(insert_error)}",
                                "row_content": str(row[:5])  # Premiers éléments pour debug
                            })
                            conn.rollback()  # Annulation des modifications
                            return 
                     
                            

                    # Validation des modifications
                    yield json.dumps({"status": "info", "message": "[INFO] Validation des modifications (commit)..."})
                    conn.commit()
                    
                    # Message final de succès
                    final_message = {
                        "status": "success",
                        "total_inserted": total_rows,
                        "table_name": table_name,
                        "message": f"[SUCCESS] {total_rows} lignes insérées avec succès dans la table `{table_name}`"
                    }
                    yield json.dumps(final_message)

                except Exception as e:
                    yield json.dumps({
                        "status": "error",
                        "message": f"[ERREUR] Exception non gérée : {str(e)}"
                    })
                    
                    # Tentative de rollback en cas d'erreur
                    try:
                        conn.rollback()
                        yield json.dumps({"status": "info", "message": "[INFO] Rollback effectué"})
                    except Exception as rollback_error:
                        yield json.dumps({
                            "status": "error", 
                            "message": f"[ERREUR] Échec du rollback : {str(rollback_error)}"
                        })

                finally:
                    # Fermeture de la connexion
                    try:
                        if 'conn' in locals() and conn:
                            conn.close()
                            yield json.dumps({"status": "info", "message": "[INFO] Connexion à la base de données fermée"})
                    except Exception as close_error:
                        yield json.dumps({
                            "status": "error", 
                            "message": f"[ERREUR] Problème lors de la fermeture de la connexion : {str(close_error)}"
                        })
            
            except Exception as global_error:
                # Capture les erreurs générales non gérées
                yield json.dumps({
                    "status": "critical_error",
                    "message": f"[ERREUR CRITIQUE] Exception non gérée dans la fonction principale : {str(global_error)}"
                })
                return {
                    "status": "critical_error",
                    "message": f"[ERREUR CRITIQUE] Exception non gérée dans la fonction principale : {str(global_error)}"
                }
            yield json.dumps({
                "fait": "true",
                "message": "insertion fait"
            })
        return progress_generator()

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
    
