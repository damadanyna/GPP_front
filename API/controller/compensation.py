import os
from werkzeug.utils import secure_filename
import openpyxl
from datetime import datetime
import random
import string
from db.db  import DB
from db.db2  import DB2
import pandas as pd
import re
 

class Compensation:
    def __init__(self):
        # Dossier où les fichiers seront enregistrés
        self.upload_folder = 'load_file'
        self.db = DB() 
        self.db2 = DB2() 
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    def initialize_sql_functions_and_tmp_table(self):
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
 
            cursor.execute("DROP  TABLE IF EXISTS tmp_rib_indexed;")
            cursor.execute("""
                CREATE  TABLE tmp_rib_indexed (
                    id VARCHAR(255),
                    rib VARCHAR(50),
                    rib2 VARCHAR(50),
                    INDEX (rib)
                );
            """)
            cursor.execute("""
                INSERT INTO tmp_rib_indexed (id, rib, rib2)
                SELECT 
                    id,
                    SUBSTRING_INDEX(SUBSTRING_INDEX(alt_acct_id, '|', -1), '|', 1) AS rib,
                    SUBSTRING_INDEX(SUBSTRING_INDEX(alt_acct_id, '|', -2), '|', 1) AS rib2
                FROM account_mcbc_live_full;
            """)

            print("Création des fonctions SQL...")
            functions = [

                # 1. find_matching_positions
                """
                CREATE FUNCTION find_matching_positions(type_sysdate TEXT, prefixes TEXT)
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
                """,

                # 2. sum_values_at_positions_
                """
                CREATE FUNCTION sum_values_at_positions_(values_str TEXT, positions_str TEXT)
                RETURNS DECIMAL(20,2)
                DETERMINISTIC
                BEGIN
                    DECLARE total DECIMAL(20,2) DEFAULT 0;
                    DECLARE current_index INT DEFAULT 0;
                    DECLARE pos INT;
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
                """,

                # 3. get_capital_non_appele
                """
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
                """,

                # 4. get_capital_appele
                """
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
                """,

                # 5. get_sold_dav
                """
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
                """,

                # 6. get_capital_TOTAL
                """
                CREATE FUNCTION get_capital_TOTAL(type_sysdate TEXT, open_balance TEXT, credit_mvmt TEXT, debit_mvmt TEXT)
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
                """,
                """
                CREATE FUNCTION somme(a INT, b INT)
                RETURNS INT
                DETERMINISTIC
                BEGIN
                    RETURN a + b;
                END
                    """
            ]

            for fn_sql in functions:
                fn_name = self.extract_function_name(fn_sql)  # naïf mais suffisant ici
                try:
                    cursor.execute(f"DROP FUNCTION IF EXISTS {fn_name};")
                    cursor.execute(fn_sql)
                    print(f"Fonction `{fn_name}` créée avec succès.")
                except Exception as e:
                    print(f"Erreur lors de la création de la fonction `{fn_name}` : {e}")

            conn.commit()
            print("Initialisation complète réussie.")
            
            return {"status": "success","message":"✅ Initialisation complète réussie"}

        except Exception as e:
            print("Erreur globale lors de l'initialisation :", e)
            

    def get_chq_in(self, offset,limit):
        
        try:
            
            conn = self.db.connect()
            cursor = conn.cursor()
            # Offset should be dynamically included in the query
            select_query = f""" 
                SELECT 
                chq.processdate,
                    chq.recordtype,
                    chq.chequenumber,
                    chq.orderingrib,
                    chq.beneficiaryrib,  
                    (SELECT get_sold_dav(type_sysdate, open_balance, credit_mvmt, debit_mvmt) FROM eb_cont_bal_mcbc_live_full WHERE type_sysdate IS NOT NULL
                    AND id= (IFNULL(
                        (SELECT id FROM tmp_rib_indexed WHERE tmp_rib_indexed.rib = orderingrib),
                        (SELECT id FROM tmp_rib_indexed WHERE tmp_rib_indexed.rib2 = orderingrib)
                )) ) as solde,
                    '' as code_anomalie,
                    `chq_rcp`.`Alerte` as anomailie,
                    CASE 
                        WHEN `chq_rcp`.`Alerte` = '' THEN 'O'
                        ELSE 'N'
                    END AS ANO
                FROM chq_rcp_a_valider as chq_rcp
                INNER JOIN  eb_chq_in_rcp_dtl_mcbc_live_full as chq 
                ON `chq_rcp`.`Reference Transaction` = chq.ftid LIMIT {limit} OFFSET {offset};  
            """
            cursor.execute(select_query) 
            rows = cursor.fetchall() 
            return rows
        except Exception as global_e:
            error_msg = f"Erreur {global_e}"
            print("Erreur", global_e)
            return {'error': error_msg}
         
        
        # try:
        #     conn = self.db.connect()
        #     cursor = conn.cursor()
        #     # Offset should be dynamically included in the query
        #     select_query = f"""
        #     SELECT 
        #         chq.processdate,
        #         chq.recordtype,
        #         chq.chequenumber,
        #         chq.orderingrib,
        #         chq.beneficiaryrib, 
        #         (SELECT get_sold_dav(type_sysdate, open_balance, credit_mvmt, debit_mvmt) FROM eb_cont_bal_mcbc_live_full WHERE type_sysdate IS NOT NULL
        #         AND id= (IFNULL(
        #             (SELECT id FROM tmp_rib_indexed WHERE tmp_rib_indexed.rib = chq.orderingrib),
        #             (SELECT id FROM tmp_rib_indexed WHERE tmp_rib_indexed.rib2 = chq.orderingrib)
        #         )) ) as solde,
        #         '' as code_anomalie,
        #         '' as anomailie,
        #         '' as ANO
        #     FROM 
        #         eb_chq_in_rcp_dtl_mcbc_live_full as chq limit 10;
        #     """ 
        #     # Il faut exécuter la requête avant de récupérer les résultats
        #     cursor.execute(select_query) 
        #     rows = cursor.fetchall()
        #     print("Rows",rows)
        #     return rows
        # except Exception as global_e:
        #     error_msg = f"Erreur {global_e}"
        #     print("Erreur", global_e)
        #     return {'error': error_msg}
        
       
    
    def import_tables_to_sipem_app(self):
        tables = [
            "account_mcbc_live_full",
            "eb_chq_in_rcp_dtl_mcbc_live_full",
            "aa_bill_details_mcbc_live_full",
            "eb_cont_bal_mcbc_live_full",
            "alternate_account_mcbc_live_full"
        ]
        try:
            conn = self.db.connect()
            cursor = conn.cursor()

            for table in tables:
                full_src = f"dfe.{table}"
                full_dest = f"sipem_app.{table}"
                print(f"Importation de {full_src} vers {full_dest}...")

                cursor.execute(f"DROP TABLE IF EXISTS {full_dest};")
                cursor.execute(f"""
                    CREATE TABLE {full_dest} AS
                    SELECT * FROM {full_src};
                """)
                print(f"✔️  {table} importée avec succès.")

            conn.commit()
            
            print("✅ Toutes les tables ont été importées.")
            return {"status": "success","message":"✅ Toutes les tables ont été importées"}
        except Exception as e:
            print("❌ Erreur lors de l'importation :", e)

        finally:
            if conn:
                conn.close()
    def extract_function_name(self,fn_sql):
        match = re.search(r'CREATE\s+FUNCTION\s+([^\s(]+)', fn_sql, re.IGNORECASE)
        return match.group(1) if match else None