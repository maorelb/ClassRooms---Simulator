import sqlite3
import os
import atexit
import sys


def main(argv):
    DBExist = os.path.isfile('schedule.db')
    if DBExist: #if database already exists, exit.
        sys.exit()

    else:
        dbcon = sqlite3.connect('schedule.db')
        cursor = dbcon.cursor()


    def close_db():
        dbcon.commit()
        cursor.close()
        dbcon.close()

    atexit.register(close_db)

    def create_tables():
        if not DBExist:  # First time creating the database tables.
            cursor.execute(""" CREATE TABLE courses (id INTEGER PRIMARY KEY , course_name TEXT NOT NULL,student TEXT,number_of_students INTEGER NOT NULL,
                                          class_id INTEGER REFERENCES classrooms(id),course_length INTEGER NOT NULL)""")
            cursor.execute("""CREATE TABLE students (grade TEXT PRIMARY KEY , count INTEGER NOT NULL)""")
            cursor.execute(""" CREATE TABLE classrooms (id INTEGER PRIMARY KEY , location TEXT NOT NULL , current_course_id INTEGER NOT NULL ,
                                     current_course_time_left INTEGER NOT NULL)""")

    def insert_course(id, course_name, student, number_of_students, class_id, course_length):
        cursor.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?)", [id, course_name, student,number_of_students,class_id,course_length])

    def insert_student(grade, count):
        cursor.execute("INSERT INTO students VALUES (?, ?)",  [grade, count])

    def insert_classroom(id, location):
        cursor.execute("INSERT INTO classrooms VALUES (?, ? , ?, ?)", [id, location,0,0])

    def create_list_of_tuples(table):
        cursor.execute('SELECT * FROM ' + table)
        return cursor.fetchall()

    def print_table(list_of_tuples):
        for item in list_of_tuples:
            print(item)

    def print_tables():
        print('courses')
        print_table(create_list_of_tuples('courses'))
        print('classrooms')
        print_table(create_list_of_tuples('classrooms'))
        print('students')
        print_table(create_list_of_tuples('students'))

    create_tables()
    # read the config file
    with open(argv[1]) as configFile:
            for line in configFile:
                line = line.split(',')
                line = [x.strip() for x in line]
                if line[0] == 'C':
                    insert_course(line[1], line[2], line[3], line[4], line[5], line[6])
                elif line[0] == 'R':
                    insert_classroom(line[1], line[2])
                elif line[0] == 'S':
                    insert_student(line[1], line[2])

    print_tables()


if __name__=='__main__':
    main(sys.argv)

