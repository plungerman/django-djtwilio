SELECT
    CUR.id, TRIM(IR.lastname) AS lastname,
    TRIM(IR.firstname) AS firstname,
    ENS.beg_date,
    ENS.end_date,
    TRIM(NVL(ENS.line1, '')) AS alt_email,
    NVL(ENS.phone,'') AS mobile,
    ENS.opt_out,
    cur.username
FROM
    provisioning_vw CUR
INNER JOIN
    id_rec IR
ON
    CUR.id = IR.id
LEFT JOIN
    aa_rec ENS
ON
    CUR.id = ENS.id
AND
    ENS.aa = 'ENS'
AND
    TODAY BETWEEN ENS.beg_date AND NVL(ENS.end_date, TODAY)
WHERE
    CUR.id IN
