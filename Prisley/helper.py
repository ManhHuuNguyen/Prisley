def update(sql_statement, cursor, db):
    cursor.execute(sql_statement)
    db.commit()


def query_all(sql_statement, cursor):
    num_row = cursor.execute(sql_statement)
    if num_row > 0:
        return list(cursor)
    else:
        return list()


def query_one(sql_statement, cursor):
    num_row = cursor.execute(sql_statement)
    if num_row > 0:
        return list(cursor)[0]
    else:
        return list()


def format_date(date):
    a = str(date).split("-")
    return a[2] + "/" + a[1] + "/" + a[0]


def format_time(time):
    a = str(time).split(":")
    return a[0] + ":" + a[1]

def filter_sql(data_string):
    return data_string.replace("'", "\\'")


