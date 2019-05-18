import math
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from multiprocessing import Process

import os
import requests
from selenium import webdriver
import selenium as se
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from threading import Thread
#import time
import threading
from queue import Queue
import time
from time import sleep
import queue
import pickle
# _________________________________________________
class Course:
    def __init__(self, course_name):
        self.course_name = course_name
        self.prof_list = []
        self.gen_eds = []
        self.avg_gpa = 0
        self.samp_num = 0
        self.gpa_rank = 0
        self.samp_rank = 0
        self.comb_rank = 0

    def get_course_name(self):
        return self.course_name

    def add_section(self, section):
        self.prof_list.append(section)

    def __eq__(self, other):
        if isinstance(other, Course):
            return self.course_name == other.course_name
        return False


class Arnav:
    def __init__(self, course_name, val):
        self.course_name = course_name
        self.val = val


# global vars
course_dict = dict()

def make_temp(gen_ed):
    result = []
    for key, value in course_dict.items():
        if(gen_ed in value.gen_eds ):
            result.append(value)
    return result

def get_best_gpa(gen_ed):
    unordered_list = make_temp(gen_ed)
    output = f'{gen_ed} Best of GPA:\n'
    with open('data.txt', 'a') as the_file:
        the_file.write(output)
    top_gpa = merge_sort(unordered_list, 'gpa')
    index = 1
    for course in top_gpa:
        if(index < 31):
            print(index, ')', course.course_name, ":", course.avg_gpa)
            output = f'{index}) {course.course_name}, avg_gpa: {course.avg_gpa}\n'
            with open('data.txt', 'a') as the_file:
                the_file.write(output)
        index += 1
    output = '\n'
    with open('data.txt', 'a') as the_file:
        the_file.write(output)


def get_best_of_both(gen_ed):
    unordered_list = make_temp(gen_ed)
    output = f'{gen_ed} best of both: \n'
    with open('data.txt', 'a') as the_file:
        the_file.write(output)
    top_gpa = merge_sort(unordered_list, 'gpa')

    top_samp = merge_sort(unordered_list, 'samp')
    # for idx, val in enumerate(top_gpa):
    #     combined_rec[idx] = top_gpa.index()

    for course in unordered_list:
        gpa_idx = top_gpa.index(course)
        samp_idx = top_samp.index(course)
        course.gpa_rank = gpa_idx
        course.samp_rank = samp_idx
        course.comb_rank = samp_idx + gpa_idx

    best_of_both = merge_sort(unordered_list, 'comb')
    index = 1
    for val in best_of_both:
        if(index < 31):
            print(index, ')', val.course_name, ":",
                  val.gpa_rank, ":", val.samp_rank)
            output = f'{index}) {val.course_name} (gpa):{val.gpa_rank} (samplSz):{val.samp_num}\n'
            with open('data.txt', 'a') as the_file:
                the_file.write(output)
        index += 1
    output = '\n'
    with open('data.txt', 'a') as the_file:
        the_file.write(output)


def arnav(gen_ed):
    unordered_list = make_temp(gen_ed)
    best_list = []
    output = f'{gen_ed} best with Arnav alg: \n'
    with open('data.txt', 'a') as the_file:
        the_file.write(output)
    for course in unordered_list:
        best_list.append(Arnav(course.course_name, float(
            course.avg_gpa * math.log2(course.samp_num))))
    best_of_both = merge_sort(best_list, 'norm')
    index = 1
    for elt in best_of_both:
        if(index < 31):
            print(index, ')', elt.course_name, ":", elt.val)
            output = f'{index}) {elt.course_name} val:{elt.val}\n'
            with open('data.txt', 'a') as the_file:
                the_file.write(output)
        index += 1
    output = '\n'
    with open('data.txt', 'a') as the_file:
        the_file.write(output)


def merge_norm(left_half, right_half):
    res = []
    while len(left_half) != 0 and len(right_half) != 0:
        if left_half[0].val > right_half[0].val:
            res.append(left_half[0])
            left_half.remove(left_half[0])
        else:
            res.append(right_half[0])
            right_half.remove(right_half[0])
    if len(left_half) == 0:
        res = res + right_half
    else:
        res = res + left_half
    return res


def merge_sort(unsorted_list, type_in):
    if len(unsorted_list) <= 1:
        return unsorted_list
    # Find the middle point and devide it
    middle = len(unsorted_list) // 2
    left_list = unsorted_list[:middle]
    right_list = unsorted_list[middle:]

    left_list = merge_sort(left_list, type_in)
    right_list = merge_sort(right_list, type_in)
    if(type_in == 'gpa'):
        return list(merge_with_gpa(left_list, right_list))
    elif(type_in == 'samp'):
        return list(merge_with_samp(left_list, right_list))
    elif (type_in == 'comb'):
        return list(merge_with_comb(left_list, right_list))
    elif (type_in == 'norm'):
        return list(merge_norm(left_list, right_list))


def merge_with_gpa(left_half, right_half):
    res = []
    while len(left_half) != 0 and len(right_half) != 0:
        if left_half[0].avg_gpa > right_half[0].avg_gpa:
            res.append(left_half[0])
            left_half.remove(left_half[0])
        else:
            res.append(right_half[0])
            right_half.remove(right_half[0])
    if len(left_half) == 0:
        res = res + right_half
    else:
        res = res + left_half
    return res


def merge_with_samp(left_half, right_half):
    res = []
    while len(left_half) != 0 and len(right_half) != 0:
        if left_half[0].samp_num > right_half[0].samp_num:
            res.append(left_half[0])
            left_half.remove(left_half[0])
        else:
            res.append(right_half[0])
            right_half.remove(right_half[0])
    if len(left_half) == 0:
        res = res + right_half
    else:
        res = res + left_half
    return res


def merge_with_comb(left_half, right_half):
    res = []
    while len(left_half) != 0 and len(right_half) != 0:
        if left_half[0].comb_rank < right_half[0].comb_rank:
            res.append(left_half[0])
            left_half.remove(left_half[0])
        else:
            res.append(right_half[0])
            right_half.remove(right_half[0])
    if len(left_half) == 0:
        res = res + right_half
    else:
        res = res + left_half
    return res


gens_list = {"DSHS", "DSHU", "DSNS", "DSNL", "DSSP", "DVCC", "DVUP", "SCIS"}
if __name__ == '__main__':

    with open('course_data.pkl', 'rb') as input:
        while(True):
            try:
                curr_course = pickle.load(input)
            except:
                break
            course_dict[curr_course.course_name] = curr_course

    for key, value in course_dict.items():
        # print(course.course_name)
        print(value.course_name)
        print(value.avg_gpa)
        for gen in value.gen_eds:
           print(gen)

    for gen in gens_list:
        get_best_of_both(gen)
        print("_____________________________")
    # for key, value in course_dict.items():
    #     if (key == "AOSC200"):
    #         print("asdfasdfasdf")
    #         print(value.course_name)
    #         for gen in value.gen_eds:
    #             print(gen)
