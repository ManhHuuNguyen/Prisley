def update(sql_statement, cursor, db):
    cursor.execute(sql_statement)
    db.commit()


def query(sql_statement, cursor):
    cursor.execute(sql_statement)
    return cursor


def format_date(date):
    a = str(date).split("-")
    return a[2] + "/" + a[1] + "/" + a[0]


def format_time(time):
    a = str(time).split(":")
    return a[0] + ":" + a[1]
