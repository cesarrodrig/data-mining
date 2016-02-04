
import csv
from collections import defaultdict
from datetime import datetime

class Student(object):
    def __init__(self, id, registration_year):
        self.id = id
        super(Student, self).__init__()
        self.registration_year = registration_year
        self.course_records = {}

    def add_course(self, course):
        if course.code not in self.course_records or course.final_grade > self.course_records[course.code].final_grade:
            self.course_records[course.code] = course

    def all_courses(self):
        return [ course.code for course in self.course_records.values() ]

class CourseRecord(object):
    def __init__(self, strings):
        super(CourseRecord, self).__init__()
        self.start_date = datetime.strptime(strings[0], "%Y-%m")
        self.code = int(strings[1])
        self.name = strings[2]
        self.credits = strings[3]
        self.final_grade = int(strings[4])

FILE_NAME = "data-2016.csv"

students = []
course_code_to_name = {}
inverted_index = defaultdict(set) # course to student ids

with open(FILE_NAME, "rb") as csvfile:
    reader = csv.reader(csvfile, delimiter=" ")

    r = 0
    for row in reader:
        student = Student(r, row[0])

        for i in range(1, len(row), 5):
            course = CourseRecord(row[i:i+5])
            student.add_course(course)
            course_code_to_name[course.code] = course.name
            inverted_index[course.code].add(r)

        r += 1
        students.append(student)

def get_courses_taken_before(course_records, datetime):
    return filter(lambda c: c.start_date < datetime and c.final_grade > 0, course_records)


def get_support_counts(students, target_course_code):
    # we get all pairs (x, target_course)
    # where target_course.date > x.date
    passed_support_count = defaultdict(int)
    failed_support_count = defaultdict(int)
    total_count = 0
    for student in students:
        # if student took the target course
        if target_course_code not in student.course_records:
            continue

        total_count += 1
        course_record = student.course_records[target_course_code]
        courses_taken_before = get_courses_taken_before(student.course_records.values(), course_record.start_date)
        course_pairs = [course.code for course in courses_taken_before]

        if course_record.final_grade > 0:
            for pair in course_pairs:
                passed_support_count[pair] += 1
        else:
            for pair in course_pairs:
                failed_support_count[pair] += 1

    return passed_support_count, failed_support_count, total_count

def courses_that_help(students, target_course_code, min_support=0.0):
    # we get all pairs (x, target_course)
    # where target_course.date > x.date and target_course.grade > 0
    passed, failed, n = get_support_counts(students, target_course_code)
    passed_support = []
    failed_support = []
    n = float(n)
    for course_code, count in passed.items():
        if count/n > min_support:
            passed_support.append((course_code_to_name[course_code], count/n))

    for course_code, count in failed.items():
        if count/n > min_support:
            failed_support.append((course_code_to_name[course_code], count/n))

    passed_support = sorted(passed_support, key=lambda x: x[1], reverse=True)[:10]
    failed_support = sorted(failed_support, key=lambda x: x[1], reverse=True)[:10]

    print "To pass", course_code_to_name[target_course_code]
    for course_name, support in passed_support:
        print course_name, support


courses_that_help(students, 581259)
