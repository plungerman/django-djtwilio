SEARCH_ID = '''
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
'''.format
