import csv
import time
from collections import defaultdict
from itertools import combinations

class Student(object):
    def __init__(self, id, registration_year):
        self.id = id
        super(Student, self).__init__()
        self.registration_year = registration_year
        self.courses = {}

    def add_course(self, course):
        if course.name not in self.courses or course.final_grade > self.courses[course.name].final_grade:
            self.courses[course.name] = course

    def all_courses(self):
        return [ course.code for course in self.courses.values() ]

class CourseRecord(object):
    def __init__(self, strings):
        super(CourseRecord, self).__init__()
        self.year_and_month = strings[0]
        self.code = strings[1]
        self.name = strings[2]
        self.credits = strings[3]
        self.final_grade = int(strings[4])

FILE_NAME = "data-2016.csv"

students = []
course_codes = set()
inverted_index = defaultdict(set) # course to student ids

with open(FILE_NAME, "rb") as csvfile:
    reader = csv.reader(csvfile, delimiter=" ")

    r = 0
    for row in reader:
        student = Student(r, row[0])

        for i in range(1, len(row), 5):
            course = CourseRecord(row[i:i+5])
            student.add_course(course)
            course_codes.add(course.code)
            inverted_index[course.code].add(r)

        r += 1
        students.append(student)

def support_count(transactions, itemset):
    if type(itemset) not in (list, set, tuple):
        raise Exception("Expected list or set")
    itemset = set(itemset)

    curr_set = reduce(lambda x, y: x.intersection(y), [inverted_index[item] for item in itemset])
    return len(curr_set)


def support(transactions, itemset):
    if type(itemset) not in (list, set, tuple):
        raise Exception("Expected list or set")
    itemset = set(itemset)

    supp_count = support_count(transactions, itemset)
    return float(supp_count) / len(transactions)

def union(itemset_a, itemset_b):
    return list(set(itemset_a).union(set(itemset_b)))

def build_combinations_with_supp_threshold(itemset, k, threshold):

    combinations_high_supp = []
    for comb in combinations(itemset, k):
        if support(course_transactions, comb) >= threshold:
            combinations_high_supp.append(comb)

    return combinations_high_supp

def generate(lists):
    response = []

    if len(lists) <= 1:
        return response

    index = 0
    while index < len(lists) - 1:
        first = lists[index]


        index2 = index + 1
        while index2 < len(lists):
            second = lists[index2]

            if first[:-1] == second[:-1]:
                response.append(union(first, second))

            index2 += 1

        index += 1

    return response

def apriori(transactions, min_support, k=99999):

    result = []
    for i, result in enumerate(apriori_generator(transactions, min_support)):
        if i+1 == k:
            return result

    return result


def apriori_generator(transactions, min_support):
    itemset = set([item for trans in transactions for item in trans ])

    freq_itemsets = filter(lambda item: support(transactions, set([item])) >= min_support, itemset)
    freq_itemsets = [[item] for item in freq_itemsets]

    while freq_itemsets:
        yield freq_itemsets
        start_time = time.time()
        candidate_itemsets = generate(freq_itemsets)
        end_time = time.time()
        next_freq_itemsets = []

        for cand_itemset in candidate_itemsets:
            supp_count = support(transactions, cand_itemset)
            if supp_count >= min_support:
                next_freq_itemsets.append(cand_itemset)


        print len(next_freq_itemsets), "%s seconds" % (end_time - start_time)


        freq_itemsets = next_freq_itemsets


lists = [[1, 2, 3], [1, 2, 4]]
assert generate(lists) == [[1, 2, 3, 4]]
lists = [[1, 2, 3, 4], [1, 2, 3, 5], [1, 3, 6, 8], [1, 3, 6, 10]]
assert generate(lists) == [[1, 2, 3, 4, 5], [1, 3, 6, 8, 10]]

course_codes = list(course_codes)
n = len(course_codes)
print "7.", n, "unique course codes"
float_n = float(n)

two_combinations = list(combinations(course_codes, 2))
print "8.", len(two_combinations), "combinations"

course_transactions = [ student.all_courses() for student in students ]

for i in range(2,4):

    start_time = time.time()

    combinations_high_supp = build_combinations_with_supp_threshold(course_codes, i , 0.1)

    print str(i+7) + ".", len(combinations_high_supp), "combinations, %s seconds" % (time.time() - start_time)

for i in range(2,10):
    start_time = time.time()

    combinations_high_supp = apriori(course_transactions, 0.1, i)

    print "17.", len(combinations_high_supp), "combinations, %s seconds" % (time.time() - start_time)


combinations_high_supp = apriori(course_transactions, 0.05)
print combinations_high_supp
