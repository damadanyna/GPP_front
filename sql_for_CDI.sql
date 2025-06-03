DELIMITER 

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

        -- Vérifier tous les préfixes
        IF FIND_IN_SET(token, prefixes) > 0 OR
           EXISTS (
               SELECT 1
               FROM (SELECT REPLACE(prefixes, ',', '\',\'') AS pfx_list) AS t
               WHERE token LIKE CONCAT(SUBSTRING_INDEX(prefixes, ',', 1), '%')
                  OR token LIKE CONCAT(SUBSTRING_INDEX(SUBSTRING_INDEX(prefixes, ',', 2), ',', -1), '%')
                  OR token LIKE CONCAT(SUBSTRING_INDEX(SUBSTRING_INDEX(prefixes, ',', 3), ',', -1), '%')
                  OR token LIKE CONCAT(SUBSTRING_INDEX(SUBSTRING_INDEX(prefixes, ',', 4), ',', -1), '%')
           )
        THEN
            SET result = CONCAT(result, ',', position);
        END IF;

        SET position = position + 1;
    END WHILE;

    RETURN result;
END

DELIMITER ;

 
DELIMITER 

CREATE FUNCTION sum_values_at_positions_(values_str TEXT, positions_str TEXT)
RETURNS DECIMAL(20,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(20,2) DEFAULT 0;
    DECLARE current_index INT DEFAULT 0;
    DECLARE pos INT;
    DECLARE val TEXT;
    DECLARE sep_pos INT;

    -- Ajout d’un délimiteur final pour simplifier l’analyse
    SET values_str = CONCAT(values_str, '|');
    SET sep_pos = LOCATE('|', values_str);

    WHILE sep_pos > 0 DO
        SET val = SUBSTRING(values_str, 1, sep_pos - 1);

        -- Vérifie si la position actuelle est présente dans positions_str
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
 
DELIMITER ;

 

 

DELIMITER 

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
 
 

DELIMITER ;


DELIMITER 

CREATE FUNCTION get_capital_TOTAL(
    type_sysdate TEXT,
    open_balance TEXT,
    credit_mvmt TEXT,
    debit_mvmt TEXT
)
RETURNS DECIMAL(20,2)
DETERMINISTIC
BEGIN 
    DECLARE pos TEXT;
    DECLARE total DECIMAL(20,2);

    -- Trouver les positions des catégories à agréger
    SET pos = find_matching_positions(type_sysdate, 'CURACCOUNT,DUEACCOUNT,PA1ACCOUNT,PA2ACCOUNT,PA3ACCOUNT,PA4ACCOUNT');

    -- Additionner les valeurs correspondantes
    SET total = 
        IFNULL(sum_values_at_positions_(open_balance, pos), 0) +
        IFNULL(sum_values_at_positions_(credit_mvmt, pos), 0) +
        IFNULL(sum_values_at_positions_(debit_mvmt, pos), 0);

    RETURN total;
END

DELIMITER ;

drop table if EXISTS tmp_rib_indexed;
-- 1. Créer la table temporaire avec transformation
CREATE  TABLE tmp_rib_indexed (
    id VARCHAR(255),
    rib VARCHAR(50),
    rib2 VARCHAR(50),
    INDEX (rib)
);

-- 2. Insérer les données transformées
INSERT INTO tmp_rib_indexed (id, rib, rib2)
SELECT 
    id,
    SUBSTRING_INDEX(SUBSTRING_INDEX(alt_acct_id, '|', -1), '|', 1) AS rib,
    SUBSTRING_INDEX(SUBSTRING_INDEX(alt_acct_id, '|', -2), '|', 1) AS rib2
FROM 
    account_mcbc_live_full;


DELIMITER 

 
DELIMITER ;

-- DROP TEMPORARY TABLE IF EXISTS tmp_rib_indexed;
 
 
-- SELECT 
--     chq.processdate,
--     chq.recordtype,
--     chq.chequenumber,
--     chq.orderingrib,
--     chq.beneficiaryrib, 
--     (SELECT get_sold_dav(type_sysdate, open_balance, credit_mvmt, debit_mvmt) FROM eb_cont_bal_mcbc_live_full WHERE type_sysdate IS NOT NULL
--     AND id= (IFNULL(
--         (SELECT id FROM tmp_rib_indexed WHERE tmp_rib_indexed.rib = chq.orderingrib),
--         (SELECT id FROM tmp_rib_indexed WHERE tmp_rib_indexed.rib2 = chq.orderingrib)
--     )) ) as solde,
--     '' as code_anomalie,
--     '' as anomailie,
--     '' as ANO
-- FROM 
--     eb_chq_in_rcp_dtl_mcbc_live_full as chq;



-- Index sur tmp_rib_indexed
CREATE INDEX idx_tmp_rib_rib ON tmp_rib_indexed(rib);
CREATE INDEX idx_tmp_rib_rib2 ON tmp_rib_indexed(rib2);
-- Index sur eb_cont_bal_mcbc_live_full
CREATE INDEX idx_eb_cont_bal_id_sysdate ON eb_cont_bal_mcbc_live_full(id);
-- Index sur eb_chq_in_rcp_dtl_mcbc_live_full
CREATE INDEX idx_eb_chq_orderingrib ON eb_chq_in_rcp_dtl_mcbc_live_full(orderingrib);
 