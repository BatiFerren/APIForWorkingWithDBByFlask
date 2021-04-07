import csv
import sqlite3
import datetime
from flask import Flask, request, render_template


app = Flask(__name__)


def connect_db(name_db):
    connect = sqlite3.connect(name_db)
    return connect


def create_table(name_table, connect):
    cur = connect.cursor()
    sql = '''CREATE TABLE IF NOT EXISTS ''' + name_table + ''' (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, Device_type text, Operator text, Time text, Success int)'''
    cur.execute(sql)
    connect.commit


def read_csv_and_write_to_db(file_obj, con):
    with open(file_obj, newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        if header != None:
            for row in reader:
                cur = con.cursor()
                cur.execute("INSERT INTO tests_results (Device_type, Operator, Time, Success) VALUES(?, ?, ?, ?);", row)
                con.commit()


@app.route('/api_v1/stat')
def create_operator_db():
    #print("Type the name of the Operator:")
    #operator = input()
    operator = request.args.get("operator")
    nameDB = operator + '_statistic.db'
    name_table = operator + '_statistic_table'
    connect = sqlite3.connect(nameDB)
    cur = connect.cursor()
    sql_delete = '''DROP TABLE IF EXISTS ''' + name_table
    cur.execute(sql_delete)
    connect.commit()

    sql = '''CREATE TABLE IF NOT EXISTS ''' + name_table + ''' (Device_type text, All_tests int, 
                                                                Success_tests int, Unsuccess_tests int)'''
    cur.execute(sql)
    connect.commit()
    main_connect = connect_db('tests.db')
    main_cursor = main_connect.cursor()
    all_select_sql = '''SELECT Device_type, COUNT(*) as All_tests FROM tests_results WHERE Operator = \'''' + operator + '''\' GROUP BY Device_type'''
    success_select_sql = '''SELECT Device_type, COUNT(*) as Success_tests FROM tests_results WHERE Operator = \'''' + operator + '''\' AND Success = 1 GROUP BY Device_type'''
    unsuccess_select_sql = '''SELECT Device_type, COUNT(*) as Unsuccess_tests FROM tests_results WHERE Operator = \'''' + operator + '''\' AND Success = 0 GROUP BY Device_type'''
    add_list = main_cursor.execute(all_select_sql).fetchall()

    dev_type_list = []
    all_tests_list = []
    success_tests_list = []
    unsuccess_tests_list = []
    for item in add_list:
        dev_type_list.append(item[0])
        all_tests_list.append(item[1])
    success_list = main_cursor.execute(success_select_sql).fetchall()
    for item in success_list:
        success_tests_list.append(item[1])
    unsuccess_list = main_cursor.execute(unsuccess_select_sql).fetchall()
    for item in unsuccess_list:
        unsuccess_tests_list.append(item[1])
    result_list = []
    sql_add_by_operator = '''INSERT INTO ''' + name_table + ''' VALUES (?, ?, ?, ?)'''
    for i in range(0, len(add_list) - 1):
        result_list.append((dev_type_list[i], all_tests_list[i], success_tests_list[i], unsuccess_tests_list[i]))

    cur.executemany(sql_add_by_operator, result_list)
    connect.commit()
    cur.close()
    connect.close()
    main_cursor.close()
    main_connect.close()

    header_list = ['Device type', 'All tests', 'Success tests', 'Unsuccess tests']

    return render_template('stat.html', name_operator = operator, header_table = header_list, stat_list = result_list)


@app.route('/api_v1/test_result/<delete_id>')
def delete_test(delete_id):
    main_connect = connect_db('tests.db')
    main_cursor = main_connect.cursor()
    delete_sql = '''DELETE FROM tests_results WHERE id=''' + delete_id
    main_cursor.execute(delete_sql)
    main_connect.commit()
    main_cursor.close()
    main_connect.close()
    return 'Deleted test id # %s' % delete_id


@app.route('/api_v1/test_result', methods=['POST', 'GET'])
def add_test():
    if request.method == 'POST':
        main_connect = connect_db('tests.db')
        main_cursor = main_connect.cursor()

        insert_list = []
        insert_list.append(request.form['dev_type'])
        insert_list.append(request.form['operator'])
        datetime_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_list.append(datetime_now)
        insert_list.append(request.form['success'])

        insert_sql = '''INSERT INTO tests_results (Device_type, Operator, Time, Success) VALUES(?, ?, ?, ?);'''
        main_cursor.execute(insert_sql, insert_list)
        main_connect.commit()
        main_cursor.close()
        main_connect.close()
    return render_template('add.html')


def main():
    file_obj = 'test_results.csv'
    my_con = connect_db('tests.db')
    create_table('tests_results', my_con)
    #read_csv_and_write_to_db(file_obj, my_con)
    #create_operator_db()


if __name__ == '__main__':

    #For run script without Flask interface uncomment main() and comment app.run()

    # For creating db and insert data from csv-file you have to uncomment
    #   read_csv_and_write_to_db(file_obj, my_con)
    # in main function (It has to be executed only once)

    # For get statistics by operator you have to uncomment
    #   print("Type the name of the Operator:")
    #   operator = input()
    # in create_operator_db() function
    # and comment
    #   operator = request.args.get("operator")
    # and uncomment create_operator_db() in main function

    #main()

    #For run Flask interface you have to uncomment app.run() and comment main()
    app.run()