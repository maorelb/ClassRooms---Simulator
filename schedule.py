import sqlite3
import os
import sys
import atexit


def main():
    def close_db():
        dbcon.commit()
        cursor.close()
        dbcon.close()

    atexit.register(close_db)

    DBExist = os.path.isfile('schedule.db')
    if not DBExist: #if database was not found exit
        print('DB not found')
        sys.exit()

    # database found
    dbcon = sqlite3.connect('schedule.db')
    cursor = dbcon.cursor()

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

    # check if there are courses left in the database
    def isempty():
        cursor.execute('SELECT * FROM ' + 'courses')
        return len(cursor.fetchall()) == 0

    # returns a list of available classes
    def get_available_classes():
        cursor.execute('SELECT * FROM classrooms where classrooms.current_course_time_left = 0')
        return cursor.fetchall()

    # returns a course with class_id
    def get_course(class_id):
        cursor.execute('SELECT * from courses where courses.class_id ={}'.format(class_id))
        return cursor.fetchone()

    # returns a list of occupied classes
    def get_occupied_classes():
        cursor.execute('SELECT * FROM classrooms where classrooms.current_course_time_left >=2')
        return cursor.fetchall()

    # returns a list of classes for which the courses have just finished
    def get_just_finished():
        cursor.execute('SELECT * FROM classrooms where classrooms.current_course_time_left==1')
        return cursor.fetchall()

    # assign course to classroom
    def assign_course(iteration,course,classroom):
        print(('({}) {}: {} is schedule to start').format(iteration, classroom[1], course[1]))
        cursor.execute('UPDATE classrooms SET current_course_id={},current_course_time_left={} where id={}'
                       .format(course[0], course[5], course[4]))
        cursor.execute("UPDATE students SET count= count - ? where grade= ?",
                       (course[3], course[2]))

    # in case there are no courses
    if isempty():
        print_tables()
        sys.exit()


    # main loop
    i = 0
    while DBExist and not isempty():
        available_classes=get_available_classes()
        occupied_classes=get_occupied_classes()
        just_finished=get_just_finished()
        if len(available_classes) > 0:  # case 1 - there are available classes
            for class_room in available_classes:
                course_to_assign=get_course(class_room[0])
                if(course_to_assign is not None):
                    assign_course(i,course_to_assign,class_room)

        if len(occupied_classes) > 0:  # case 2 - some classes are occupied
            for class_room in occupied_classes:
                print(('({}) {}: occupied by {}').format(i,class_room[1],get_course(class_room[0])[1]))
                cursor.execute('UPDATE classrooms SET current_course_time_left=current_course_time_left-1 where id={}'
                               .format(class_room[0]))
        if len(just_finished) > 0: #case 3 - some clases have just finished
            for class_room in just_finished:
                print(('({}) {}: {} is done').format(i, class_room[1], get_course(class_room[0])[1]))
                cursor.execute('UPDATE classrooms SET current_course_id={},current_course_time_left={} where id={}'
                               .format(0, 0, class_room[0]))
                cursor.execute('DELETE FROM courses where id={}'.format(class_room[2]))
                course_to_assign=get_course(class_room[0]) #assign a new course rightaway
                if (course_to_assign is not None):
                    assign_course(i, course_to_assign, class_room)

        print_tables()
        i += 1


if __name__=='__main__':
    main()