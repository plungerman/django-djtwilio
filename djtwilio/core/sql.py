# -*- coding: utf-8 -*-

SEARCH_ID = """
SELECT UNIQUE
    id_rec.lastname, id_rec.firstname, id_rec.id,
    id_rec.zip, id_rec.ctry, id_rec.phone,
    id_rec.addr_line1, id_rec.addr_line2, id_rec.city,
    id_rec.st, id_rec.zip, id_rec.ctry,
    NVL(aa_rec.phone,"")
FROM
    id_rec
LEFT JOIN
    aa_rec
ON
    id_rec.id = aa_rec.id
WHERE
    aa_rec.phone <> ""
AND
    id_rec.id = {student_number}
""".format

STUDENTS = """
SELECT
    UNIQUE
    CASE
        WHEN
            NVL(UPPER(stu_serv_rec.bldg), '') = 'CMTR'
        OR
            NVL(stu_serv_rec.bldg, '') = 'undc'
        OR
            NVL(UPPER(stu_serv_rec.bldg), '') = ''
        THEN
            'Commuter'
        ELSE
            'Resident'
        END
    AS
        residency_status,
    id_rec.id, id_rec.lastname, id_rec.firstname, id_rec.middlename,
    TRIM(NVL(mobile_rec.phone, mobile_rec2.phone)) as mobile,
    id_rec.addr_line1, id_rec.addr_line2, id_rec.city, id_rec.st,
    id_rec.zip, id_rec.ctry, id_rec.phone, cvid_rec.ldap_name,
    profile_rec.birth_date,
    profile_rec.sex,
    prog_enr_rec.cl
FROM
    id_rec
INNER JOIN
    prog_enr_rec ON  id_rec.id = prog_enr_rec.id
LEFT JOIN
    cvid_rec
ON
    id_rec.id = cvid_rec.cx_id
LEFT JOIN
    stu_acad_rec    ON  id_rec.id   =   stu_acad_rec.id
LEFT JOIN
    stu_serv_rec    ON  id_rec.id   =   stu_serv_rec.id
LEFT JOIN
    profile_rec  ON  id_rec.id = profile_rec.id
LEFT JOIN
    aa_rec as mobile_rec
ON
    id_rec.id = mobile_rec.id
AND
    mobile_rec.aa = "ENS"
AND
    TODAY BETWEEN mobile_rec.beg_date AND NVL(mobile_rec.end_date, TODAY)
LEFT JOIN
    aa_rec as mobile_rec2
ON
    id_rec.id = mobile_rec2.id
AND
    mobile_rec.aa = "ENS"
WHERE
    prog_enr_rec.subprog NOT IN  (
        "UWPK","RSBD","SLS","PARA","MSW","KUSD","ENRM","CONF","CHWK"
    )
AND
    prog_enr_rec.lv_date IS NULL
AND
    stu_serv_rec.yr = "{year}"
AND
    stu_serv_rec.sess = "{term}"
ORDER BY
    id_rec.lastname
""".format
