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
class Proffessor:
    def __init__(self, name, avg_gpa, samp_size):
        self.name = name
        self.avg_gpa = 0
        self.samp_size = 0

    def __eq__(self, other):
        if isinstance(other, Proffessor):
            return self.name.lower() == other.name.lower() 
        return False
        
class Course_Rank:
    def __init__(self, course_name):
        self.course_name = course_name
        self.arnav_val = 0
        self.prof_avg_gpa = 0
        self.prof_high_gpa = 0
        self.high_prof_arnav_val = 0
        self.avg_prof_arnav_val = 0
        self.high_prof_name = ""

    def __eq__(self, other):
        if isinstance(other, Course):
            return self.course_name.lower() == other.course_name.lower()
        return False

class Course:
    def __init__(self, course_name):
        self.course_name = course_name
        self.prof_list = dict()
        self.gen_eds = []
        self.avg_gpa = 0
        self.samp_num = 0
        self.gpa_rank = 0
        self.samp_rank = 0
        self.comb_rank = 0

    def __eq__(self, other):
        if isinstance(other, Course):
            return self.course_name.lower() == other.course_name.lower()
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
        if(gen_ed in value.gen_eds):
            result.append(value)
    return result


def find_course_index(list_in, course_in):
    try:
        return list_in.index(Course_Rank(course_in))
    except:
        return -1

def add_prof_data(gen_ed):
    unordered_list = make_temp(gen_ed)
    result_list = []
    for course in unordered_list:
        high_prof_arnav_val = 0
        high_prof_name = ""
        avg_prof_arnav_val = 0
        result_list.append(Course_Rank(course.course_name))
        for key2, prof in course.prof_list.items():
            prof_arnav_val = float(prof.avg_gpa * math.log2(prof.samp_size+1))
            avg_prof_arnav_val += prof_arnav_val
            if (prof_arnav_val > high_prof_arnav_val):
                high_prof_arnav_val = prof_arnav_val
                high_prof_name = prof.name
        if len(course.prof_list) != 0:
            avg_prof_arnav_val = avg_prof_arnav_val / len(course.prof_list)
        else:
            avg_prof_arnav_val = 0
        c_index = find_course_index(result_list, course.course_name)
        result_list[c_index].high_prof_arnav_val = high_prof_arnav_val
        result_list[c_index].avg_prof_arnav_val = avg_prof_arnav_val
        result_list[c_index].high_prof_name = high_prof_name
    return result_list

def prof_rank(gen_ed):
    best_list = add_prof_data(gen_ed)
    output = f'{gen_ed} best with Arnav_Prof alg: \n'
    with open('data.txt', 'a') as the_file:
        the_file.write(output)
    best_of_both = merge_sort(best_list, 'prof_val')
    index = 1
    for elt in best_of_both:
        if(index < 31):
            print(index, ')', elt.course_name, ":", elt.high_prof_arnav_val , "with ", elt.high_prof_name)
            output = f'{index}) {elt.course_name} val:{elt.high_prof_arnav_val} with {elt.high_prof_name} \n'
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
        best_list.append(Course_Rank(course.course_name))
        c_index = find_course_index(best_list, course.course_name)
        best_list[c_index].arnav_val = float(course.avg_gpa * math.log2(course.samp_num))
    best_of_both = merge_sort(best_list, 'norm')
    index = 1
    for elt in best_of_both:
        if(index < 31):
            print(index, ')', elt.course_name, ":", elt.arnav_val)
            output = f'{index}) {elt.course_name} val:{elt.arnav_val}\n'
            with open('data.txt', 'a') as the_file:
                the_file.write(output)
        index += 1
    output = '\n'
    with open('data.txt', 'a') as the_file:
        the_file.write(output)


def merge_norm(left_half, right_half):
    res = []
    while len(left_half) != 0 and len(right_half) != 0:
        if left_half[0].arnav_val > right_half[0].arnav_val:
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

def merge_prof_val(left_half, right_half):
    res = []
    while len(left_half) != 0 and len(right_half) != 0:
        if left_half[0].high_prof_arnav_val > right_half[0].high_prof_arnav_val:
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

    if (type_in == 'norm'):
        return list(merge_norm(left_list, right_list))
    elif (type_in == 'prof_val'):
        return list(merge_prof_val(left_list, right_list))


gens_list = {"DSHS", "DSHU", "DSNS", "DSNL", "DSSP", "DVCC", "DVUP", "SCIS"}
if __name__ == '__main__':
    open('data.txt', 'w').close()
    with open('course_data.pkl', 'rb') as input:
        while(True):
            try:
                curr_course = pickle.load(input)
            except:
                break
            course_dict[curr_course.course_name] = curr_course

    # for key, value in course_dict.items():
    #     # print(course.course_name)
    #     # print(value.course_name)
    #     # print(value.avg_gpa)
    #     for key2, prof in value.prof_list.items():
    #         print(prof.name)
    #         print(prof.avg_gpa)
    #         print(prof.samp_size)
    #         print("")

    for gen in gens_list:
        print(gen)
        prof_rank(gen)
        print("_____________________________")
        # arnav(gen)

