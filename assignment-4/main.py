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
    curr_set = reduce(lambda x, y: x.intersection(y), [inverted_index[item] for item in itemset])
    return len(curr_set)


def support(transactions, itemset):
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

def generate_candidates(frequent):

    candidates = []

    if len(frequent) <= 1:
        return candidates

    freq_index = frozenset([frozenset(l) for l in frequent])
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
            all_in_freq = True

            for comb in combinations(merged, len(merged)-1):
                is_in_set = frozenset(comb) in freq_index

                if not is_in_set:
                    all_in_freq = False
                    break

            if all_in_freq:
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
        candidate_itemsets = generate_candidates(freq_itemsets)
        next_freq_itemsets = []

        for i, cand_itemset in enumerate(candidate_itemsets):
            if cand_itemset == "BOUND" and candidate_itemsets[i-1] != "BOUND":
                next_freq_itemsets.append(cand_itemset)
            elif cand_itemset != "BOUND" and support(transactions, cand_itemset) >= min_support:
                next_freq_itemsets.append(cand_itemset)

        freq_itemsets = next_freq_itemsets

def confidence(rule):
    union = rule[0] | rule[1]
    union_supp = support_count(None, union)
    conseq_supp = support_count(None, rule[1])

    return float(union_supp) / conseq_supp

def generate_rules_of_all_itemsets(freq_itemsets, min_confidence):
    rules = []
    for freq_itemset in freq_itemsets:

        """ GENERATING 1-CONSEQUENCE RULES"""
        consequences = [[item] for item in freq_itemset]
        freq_supp = support_count(None, freq_itemset)
        freq_set = frozenset(freq_itemset)
        next_consequences = []
        for consequence in consequences:
            disjoint = sorted(list(freq_set - set(consequence)))
            conf = float(freq_supp) / float(support_count(None, disjoint))
            if conf >= min_confidence:
                rules.append((disjoint, consequence, conf))
                next_consequences.append(consequence)
        """ END """

        consequences = next_consequences
        k = len(freq_itemset)
        m = len(consequences[0])
        while k > m + 1:

            candidates = generate_candidates(consequences)
            consequences = []
            for i, candidate in enumerate(candidates):
                if candidate == "BOUND":
                    consequences.append(candidate)
                    continue

                cand_set = frozenset(candidate)
                disjoint = sorted(list(freq_set - cand_set))
                conf = float(freq_supp) / float(support_count(None, disjoint))

                if conf < min_confidence:
                    continue

                rules.append((disjoint, candidate, conf))
                consequences.append(candidate)

            k = len(freq_itemset)
            m = len(consequences[0])

    return rules

course_transactions = [ student.all_courses() for student in students ]
