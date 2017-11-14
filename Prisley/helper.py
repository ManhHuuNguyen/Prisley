def update(sql_statement, cursor, db):
    cursor.execute(sql_statement)
    db.commit()


def query(sql_statement, cursor):
    cursor.execute(sql_statement)
    return cursor

