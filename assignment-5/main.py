import os
import csv
from collections import defaultdict
import numpy

course_code_to_name = {}

FILE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data-2016.csv"))


class Student(object):
    def __init__(self, id, registration_year):
        self.id = id
        super(Student, self).__init__()
        self.registration_year = registration_year
        self.start_date_to_courses = defaultdict(list)
        self.courses = []

    def add_course(self, course):
        self.courses.append(course)

class CourseRecord(object):
    def __init__(self, strings):
        super(CourseRecord, self).__init__()
        self.year_and_month = strings[0]
        self.code = int(strings[1])
        self.name = strings[2]
        self.credits = strings[3]
        self.final_grade = int(strings[4])

    def __repr__(self):
        return "%s %s %s" % (self.code, self.name, self.year_and_month)

students = []
course_codes = set()
course_code_to_name = {}
with open(FILE_NAME, "rb") as csvfile:
    reader = csv.reader(csvfile, delimiter=" ")

    r = 0
    for row in reader:
        student = Student(r, row[0])
        for i in range(1, len(row), 5):
            course = CourseRecord(row[i:i+5])
            student.add_course(course)
            course_codes.add(course.code)
            course_code_to_name[course.code] = course.name

        r += 1
        students.append(student)

row = []
code_and_grade_to_column = {}
terminations = ["_0", "_2", "_4", "_PASS", "_FAIL"]
for i, code in enumerate(course_codes):
    for termination in terminations:
        s = str(code) + termination
        row.append(0)
        code_and_grade_to_column[s] = len(row) - 1

registration_years = ['2014', '2008', '2009', '2011', '2010', '2013', '2012']
registration_year_to_column = {}
for registration_year in registration_years:
    row.append(0)
    registration_year_to_column[registration_year] = len(row) - 1

table = []
for student in students:
    new_row = row[:]
    registration_col = registration_year_to_column[student.registration_year]
    new_row[registration_col] = 1
    for course in student.courses:
        if course.final_grade == 0:
            s = str(course.code) + "_0"
            new_row[code_and_grade_to_column[s]] = 1
            s = str(course.code) + "_FAIL"
            new_row[code_and_grade_to_column[s]] = 1
        if course.final_grade == 2:
            s = str(course.code) + "_2"
            new_row[code_and_grade_to_column[s]] = 1
            s = str(course.code) + "_PASS"
            new_row[code_and_grade_to_column[s]] = 1
        if course.final_grade == 4:
            s = str(course.code) + "_4"
            new_row[code_and_grade_to_column[s]] = 1
            s = str(course.code) + "_PASS"
            new_row[code_and_grade_to_column[s]] = 1

    table.append(new_row)

"""
581325 Introduction to programming
582103 Advanced programming
"""


table = numpy.array(table)

grades = ["_0", "_2", "_4"]
passed = ["_FAIL", "_PASS"]

codes = ["581325", "582103"]

intro_code = "581325"
advanced_code = "582103"
data_code = "58131"
for grade_a in grades:
    for p_a in passed:
        grade_col_a = code_and_grade_to_column[intro_code+grade_a]
        p_col_a = code_and_grade_to_column[intro_code+p_a]
        grade_col_a = table[:, grade_col_a]
        p_col_a = table[:, p_col_a]

        for grade_b in grades:
            for p_b in passed:
                grade_col_b = code_and_grade_to_column[advanced_code+grade_b]
                p_col_b = code_and_grade_to_column[advanced_code+p_b]
                grade_col_b = table[:, grade_col_b]
                p_col_b = table[:, p_col_b]

                common_students = grade_col_a & p_col_a & grade_col_b & p_col_b
                # print intro_code+grade_a, intro_code+p_a, advanced_code+grade_b, advanced_code+p_b, sum(common_students)


columns = [table[:, registration_year_to_column[year]] for year in ["2011", "2012", "2013", "2014"]]

registration_common_students = reduce(lambda column_a, column_b: column_a | column_b, columns)
intro_0_col = code_and_grade_to_column[intro_code+"_0"]
intro_2_col = code_and_grade_to_column[intro_code+"_2"]
intro_4_col = code_and_grade_to_column[intro_code+"_4"]
advanced_2_col = code_and_grade_to_column[advanced_code+"_2"]

intro_0_col = table[:, intro_0_col]
intro_2_col = table[:, intro_2_col]
intro_4_col = table[:, intro_4_col]
advanced_2_col = table[:, advanced_2_col]

common_students = registration_common_students & intro_0_col & advanced_2_col
print "{Enrollment Year > 2010, Intro = 0} -> {Advanced = 2} =", sum(common_students)

common_students = registration_common_students & intro_2_col & advanced_2_col
print "{Enrollment Year > 2010, Intro = 2} -> {Advanced = 2} =", sum(common_students)

common_students = registration_common_students & intro_4_col & advanced_2_col
print "{Enrollment Year > 2010, Intro = 4} -> {Advanced = 2} =", sum(common_students)

def get_mean_of_students(common_students, target_course):
    common_students_i = numpy.nonzero(common_students)[0]
    courses_taken = []
    for student_i in common_students_i:
        student = students[student_i]
        courses_taken += filter(lambda c: c.code == int(target_course), student.courses)

    total = sum([c.final_grade for c in courses_taken])
    return float(total)/len(courses_taken)

common_students = registration_common_students & intro_2_col
mean = get_mean_of_students(common_students, int(advanced_code))
print "{Enrollment Year > 2010, Intro = 2} -> Advanced Mean =",
print mean

common_students = registration_common_students & intro_4_col
mean = get_mean_of_students(common_students, int(data_code))
print "{Enrollment Year > 2010, Intro = 4} -> Data Structures Mean =",
print mean

columns = [ table[:, registration_year_to_column[year]] for year in ["2008", "2009"] ]
registration_common_students = reduce(lambda column_a, column_b: column_a | column_b, columns)

common_students = registration_common_students & intro_4_col
mean = get_mean_of_students(common_students, int(data_code))
print "{Enrollment Year < 2010, Intro = 4} -> Data Structures Mean =",
print mean
