import os
import csv
import time
from collections import defaultdict
from itertools import combinations

FILE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data-2016.csv"))

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
        self.code = int(strings[1])
        self.name = strings[2]
        self.credits = strings[3]
        self.final_grade = int(strings[4])

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
        raise Exception("Expected list or set, got %s" % type(itemset))
    itemset = set(itemset)

    curr_set = reduce(lambda x, y: x.intersection(y), [inverted_index[item] for item in itemset])
    return len(curr_set)


def support(transactions, itemset):
    if type(itemset) not in (list, set, tuple):
        raise Exception("Expected list or set, got %s" % type(itemset))
    itemset = set(itemset)

    supp_count = support_count(transactions, itemset)
    return float(supp_count) / len(transactions)

def merge(itemset_a, itemset_b):
    if itemset_a[-1] > itemset_b[-1]:
        res = itemset_b[:]
        res.append(itemset_a[-1])
        return res
    elif itemset_a[-1] < itemset_b[-1]:
        res = itemset_a[:]
        res.append(itemset_b[-1])
        return res
    else:
        raise Exception("Item sets have different last elements")

def generate(frequent):

    candidates = []

    if len(frequent) <= 1:
        return candidates

    index = 0
    while index < len(frequent):
        while index < len(frequent) and frequent[index] == "BOUND":
            index += 1
        if index >= len(frequent): break
        first = frequent[index]


        index2 = index + 1
        while index2 < len(frequent) and frequent[index2] != "BOUND":
            second = frequent[index2]
            merged = merge(first, second)
            candidates.append(merged)
            index2 += 1

        index += 1
        candidates.append("BOUND")

    return candidates

def apriori(transactions, min_support, k=99999):

    prev_result = []
    for i, result in enumerate(apriori_generator(transactions, min_support)):
        if not result:
            return prev_result
        if i+1 == k:
            return result

        prev_result = result

    return result


def apriori_generator(transactions, min_support):
    itemset = set([item for trans in transactions for item in trans ])

    freq_itemsets = filter(lambda item: support(transactions, set([item])) >= min_support, itemset)
    freq_itemsets = [[item] for item in freq_itemsets]
    freq_itemsets = sorted(freq_itemsets, key=lambda x: x[0])
    while freq_itemsets:
        yield filter(lambda a: a!="BOUND", freq_itemsets)
        start_time = time.time()
        candidate_itemsets = generate(freq_itemsets)
        end_time = time.time()
        next_freq_itemsets = []

        for cand_itemset in candidate_itemsets:
            if cand_itemset == "BOUND":
                next_freq_itemsets.append(cand_itemset)
            elif support(transactions, cand_itemset) >= min_support:
                next_freq_itemsets.append(cand_itemset)

        freq_itemsets = next_freq_itemsets

course_transactions = [ student.all_courses() for student in students ]

for i in range(3,5):
    start_time = time.time()

    combinations_high_supp = apriori(course_transactions, 0.1, i)
    for comb in combinations_high_supp:
        print comb
    print len(combinations_high_supp), "combinations, %s seconds" % (time.time() - start_time)

start_time = time.time()
combinations_high_supp = apriori(course_transactions, 0.04, 5)
print len(combinations_high_supp), "combinations, %s seconds" % (time.time() - start_time)
