import os
import csv
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random
import time


FILE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data-2016.csv"))
MONTH = relativedelta(months=1)


class Student(object):
    def __init__(self, id, registration_year):
        self.id = id
        super(Student, self).__init__()
        self.registration_year = registration_year
        self.start_date_to_courses = defaultdict(list)
        self.course_sequence = []

    def add_course(self, course):
        self.start_date_to_courses[course.year_and_month].append(course.code)

    def build_course_sequence(self, min_date, max_date):
        keys = sorted(self.start_date_to_courses.keys())

        while min_date <= max_date:
            date_str = min_date.strftime("%Y-%m")
            if date_str in self.start_date_to_courses:
                s = sorted(self.start_date_to_courses[date_str])
                self.course_sequence.append(s)
            min_date += MONTH

    def course_sequence_to_str(self):
        res = []

        for course_set in self.course_sequence:
            if len(course_set) == 0:
                res += "O"
            else:
                res += ",".join([ course.code for course in list(course_set)])
            res += "|"
        return res


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
course_to_students = defaultdict(set) # course to student ids
course_code_to_name = {}
inverted_index = defaultdict(set) # course to student ids

with open(FILE_NAME, "rb") as csvfile:
    reader = csv.reader(csvfile, delimiter=" ")

    r = 0
    min_date = "2016-12"
    max_date = ""
    for row in reader:
        student = Student(r, row[0])

        for i in range(1, len(row), 5):
            course = CourseRecord(row[i:i+5])
            student.add_course(course)
            course_codes.add(course.code)
            course_code_to_name[course.code] = course.name
            course_to_students[course.code].add(student.id)
            min_date = min(course.year_and_month, min_date)
            max_date = max(course.year_and_month, max_date)
            inverted_index[course.code].add(student)

        r += 1
        students.append(student)

def support_count(transactions, sequence):
    matching_transactions = filter(lambda trans: is_subsequence(sequence, trans), transactions)
    return len(matching_transactions)


def support(transactions, sequence):

    if not sequence:
        return 0.0
    supp_count = support_count(transactions, sequence)

    return float(supp_count) / len(transactions)

def flatten(a):
    # print a
    return [item for sublist in a for item in sublist]

def parallel_is_subsequence(tup):
    return is_subsequence(tup[0], tup[1])

def is_subsequence(a, b):
    # is 'a' subsequence of 'b'?
    dim_i_a, dim_j_a = 0, 0
    dim_i_b, dim_j_b = 0, 0

    len_a = len(a)
    len_b = len(b)

    found_in_curr_element = False
    while dim_i_a < len_a and dim_i_b < len_b:
        if a[dim_i_a][dim_j_a] == b[dim_i_b][dim_j_b]:
            dim_j_a += 1
            found_in_curr_element = True

        dim_j_b += 1

        if dim_j_a >= len(a[dim_i_a]):
            dim_j_a = 0
            dim_i_a += 1
            if found_in_curr_element:
                dim_j_b = 0
                dim_i_b += 1
                found_in_curr_element = False

        if dim_i_b < len_b and dim_j_b >= len(b[dim_i_b]):
            dim_j_b = 0
            dim_i_b += 1

    return dim_i_a == len_a

def are_mergeable(sequence_a, sequence_b):

    dim_i_a, dim_j_a = 0, 1
    if len(sequence_a[0]) == 1:
        dim_i_a, dim_j_a = 1, 0

    dim_i_b, dim_j_b = 0, 0
    len_a = len(sequence_a)
    len_b = len(sequence_b)

    while dim_i_a < len_a and dim_i_b < len_b:
        if sequence_a[dim_i_a][dim_j_a] != sequence_b[dim_i_b][dim_j_b]:
            return False

        dim_j_a += 1
        dim_j_b += 1
        if dim_j_a >= len(sequence_a[dim_i_a]):
            dim_j_a = 0
            dim_i_a += 1
        if dim_j_b >= len(sequence_b[dim_i_b]):
            dim_j_b = 0
            dim_i_b += 1


        if dim_i_b == len_b - 1 and dim_j_b == len(sequence_b[dim_i_b]) - 1:
            return True


    return True

def generate_candidates(sequences):

    response = []
    if len(sequences) <= 1:
        return response

    for i in range(len(sequences)):
        first = sequences[i]
        for j in range(len(sequences)):
            if i == j: continue

            second = sequences[j]

            mergeable = are_mergeable(first, second)

            if mergeable:
                candidate = deepcopy(first)
                if len(second[-1]) == 1:
                    candidate.append([second[-1][-1]])
                if len(second[-1]) > 1:
                    candidate[-1].append(second[-1][-1])
                    candidate[-1].sort()

                response.append(candidate)

    return response

def apriori(transactions, min_support, k=99999):

    prev_result = []
    for i, result in enumerate(apriori_generator(transactions, min_support)):
        if not result:
            return prev_result
        if i+1 == k:
            return result

        prev_result = result

    return prev_result


def apriori_generator(transactions, min_support):
    s = set()
    for trans in transactions:
        for element in trans:
            for event in element:
                s.add(event)

    sequences = sorted([[elem] for elem in s])

    # generate the 2-sequence manually
    n = len(sequences)
    new_sequences = []
    for i in range(n):
        for j in range(i+1, n):
            if i == j: continue
            # print sequences[i], sequences[j]
            new_sequences.append([sequences[i], sequences[j]])
            new_sequences.append([sequences[j], sequences[i]])
            joined = sequences[i][:]
            joined.append(sequences[j][0])
            new_sequences.append([joined])

    sequences = new_sequences
    freq_sequences = filter(lambda sequence: support(transactions, sequence) >= min_support, sequences)

    while freq_sequences:
        yield freq_sequences
        candidate_sequences = generate_candidates(freq_sequences)
        next_freq_sequences = []

        for cand_itemset in candidate_sequences:
            supp_count = support(transactions, cand_itemset)
            if supp_count >= min_support:
                next_freq_sequences.append(cand_itemset)

        freq_sequences = next_freq_sequences

transactions = [
[ ["bathroom"], ["computer"], ["homework"] ],
[ ["bathroom", "phone"], ["computer"] ],
[ ["computer"], ["homework"], ["phone"] ],
[ ["phone"], ["computer", "homework"] ],
[ ["tv"], ["bathroom"], ["computer"] ],
[ ["tv"], ["bathroom", "phone"] ],
[ ["tv"], ["phone"], ["computer"] ]
]

a = [["bathroom"], ["computer"], ["homework"]]
b = [["computer"], ["homework"], ["phone"]]
assert are_mergeable(a, b)

a = [[1, 2], [3], [4]]
b = [[2], [3], [4], [5]]
assert are_mergeable(a, b)

a = [[1, 2], [4], [5]]
b = [[2], [3], [4], [5]]
assert not are_mergeable(a, b)

a = [[2], [3,6], [8]]
b = [[2,4], [3,5,6], [8]]
assert is_subsequence(a, b)

a = [[2], [8]]
b = [[2,4], [3,5,6], [8]]
assert is_subsequence(a, b)

a = [[1], [2]]
b = [[1,2], [3,4]]
assert not is_subsequence(a, b)

a = [[1,2], [3]]
b = [[1,2,3], [4,5]]
assert not is_subsequence(a, b)

a = [[2], [4]]
b = [[2,4], [2,4], [2,5]]
assert is_subsequence(a, b)

print min_date, max_date
max_date = datetime.strptime(max_date, "%Y-%m")
min_date = datetime.strptime(min_date, "%Y-%m")

for student in students:
    student.build_course_sequence(min_date, max_date)

transactions = [ student.course_sequence for student in students ]

start = time.time()
sequences_high_supp = apriori(transactions, 0.20)
print "%s sequences found in" % len(sequences_high_supp), time.time() - start
for sequence in sequences_high_supp:
    print sequence, support(transactions, sequence)
    for course in flatten(sequence):
        print course_code_to_name[course]
