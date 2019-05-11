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


# global vars
all_gens_dict = dict()


def get_courses(gen_ed, driver):
    global all_gens_dict
    gen_url = "https://app.testudo.umd.edu/soc/gen-ed/201908/" + gen_ed
    print(gen_url)
    driver.get(gen_url)

    all_dept_list = driver.find_element(
        By.XPATH, '//*[@id="courses-page"]')
    dept_row = all_dept_list.find_elements(
        By.CLASS_NAME, "course-prefix-container")
    for dept in dept_row:
        course_list = dept.find_elements(By.CLASS_NAME, "course")
        for course in course_list:
            course_name = course.get_attribute("id")
            # print(course_name)
            # adds each course to the set within the dict[gen_ed]
            all_gens_dict[gen_ed].append((Course(course_name)))


def add_gened(gen_ed):
    global all_gens_dict
    all_gens_dict[gen_ed] = []


def add_gpa_field(gen_ed, course_in, driver):
    global all_gens_dict
    pterp_url = 'https://planetterp.com/course/'+course_in
    driver.get(pterp_url)
    try:
        gpa_text = driver.find_element(
            By.XPATH, '//*[@id="course-grades"]/p[1]').text
    except NoSuchElementException:
        driver.refresh()
        return -1
    start_gpa_i = gpa_text.find(':')
    end_gpa_i = gpa_text.find(' ', start_gpa_i+2)
    if(start_gpa_i == -1):
        driver.refresh()
        return -1
    gpa = float(gpa_text[start_gpa_i+2:end_gpa_i])
    index_of_course = find_course(gen_ed, course_in)
    # adds the gpa to the course obj
    all_gens_dict[gen_ed][index_of_course].avg_gpa = gpa

    samp_num_st = gpa_text.find('between')+8
    samp_num_end = gpa_text.find(' ', samp_num_st)
    samp_num = int(gpa_text[samp_num_st:samp_num_end].replace(',', ''))

    # adds the sample number to the course obj
    # print(gen_ed,":",index_of_course)
    all_gens_dict[gen_ed][index_of_course].samp_num = samp_num


def find_course(gen_ed, course_in):
    try:
        return all_gens_dict[gen_ed].index(Course(course_in))
    except:
        return -1


def remove_empty(gen_ed):
    for course in all_gens_dict[gen_ed][:]:
        if(course.avg_gpa == 0):
            print("removing")
            all_gens_dict[gen_ed].remove(course)


class Course:
    def __init__(self, course_name):
        self.course_name = course_name
        self.prof_list = []
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


def get_best_gpa(gen_ed):
    top_gpa = merge_sort(all_gens_dict[gen_ed], 'gpa')
    for course in top_gpa:
        print(course.course_name, ":", course.avg_gpa)


def get_best_of_both(gen_ed):

    top_gpa = merge_sort(all_gens_dict[gen_ed], 'gpa')

    top_samp = merge_sort(all_gens_dict[gen_ed], 'samp')
    # for idx, val in enumerate(top_gpa):
    #     combined_rec[idx] = top_gpa.index()

    for course in all_gens_dict[gen_ed]:
        gpa_idx = top_gpa.index(course)
        samp_idx = top_samp.index(course)
        course.gpa_rank = gpa_idx
        course.samp_rank = samp_idx
        course.comb_rank = samp_idx + gpa_idx

    best_of_both = merge_sort(all_gens_dict[gen_ed], 'comb')
    for val in best_of_both:
        print(val.course_name, ":", val.gpa_rank, ":", val.samp_rank)


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


def run(gen):

    options = se.webdriver.ChromeOptions()
    # chrome is set to headless
    options.add_argument('headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--no-default-browser-check')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-default-apps')
    driver = se.webdriver.Chrome(chrome_options=options)

    add_gened(gen)
    get_courses(gen, driver)

    for course in all_gens_dict[gen]:
        add_gpa_field(gen, course.course_name, driver)

    remove_empty(gen)

    print("________________________")
    print(gen, ": best GPA")
    print("")
    get_best_gpa(gen)
    print("")
    print(gen, ": best Over All")
    print("")
    get_best_of_both(gen)
    print("_________________________")
    # driver.quit()


gens_list = {"DSHS", "DSHU", "DSNS", "DSNL", "DSSP"}
thread_list = []
if __name__ == '__main__':
    processes = []

    for gen in gens_list:
        p = Process(target=run, args=(gen,))
        thread_list.append(p)
        processes.append(p)

    for thread in thread_list:
        thread.start()


