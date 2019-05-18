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

    def reader(self,input_dict,*kwargs):
        for key in input_dict:
            try:
                setattr(self, key, input_dict[key])
            except:
                print("no such attribute,please consider add it at init")
                continue


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
            # adds each course
            all_gens_dict[course_name] = Course(course_name)

from threading import Lock
lock = Lock()

def add_gpa_field(gen_ed,course_in, driver):
    global all_gens_dict
    pterp_url = 'https://planetterp.com/course/'+course_in
    try:
        driver.get(pterp_url)
    except TimeoutException:
        return -1
    try:
        gpa_text = driver.find_element(
            By.XPATH, '//*[@id="course-grades"]/p[1]').text
    except NoSuchElementException:
        return -1
    start_gpa_i = gpa_text.find(':')
    end_gpa_i = gpa_text.find(' ', start_gpa_i+2)
    if(start_gpa_i == -1):
        return -1
    gpa = float(gpa_text[start_gpa_i+2:end_gpa_i])
    samp_num_st = gpa_text.find('between')+8
    samp_num_end = gpa_text.find(' ', samp_num_st)
    samp_num = int(gpa_text[samp_num_st:samp_num_end].replace(',', ''))

    lock.acquire()
    try:
        # adds the gpa to the course obj
        all_gens_dict[course_in].avg_gpa = gpa
        # adds the sample number to the course obj
        all_gens_dict[course_in].samp_num = samp_num
        all_gens_dict[course_in].gen_eds.append(gen_ed)
    finally:
        lock.release() #release lock



def remove_empty(gen_ed):
    for course in all_gens_dict[:]:
        if(course.avg_gpa == 0):
            all_gens_dict.pop(course, None)


jobs = Queue()
jobs2 = Queue()
gens_list = {"DSHS", "DSHU", "DSNS", "DSNL", "DSSP", "DVCC", "DVUP", "SCIS"}
def run(q):
    while not q.empty():
        gen = q.get()
        try:
            options = se.webdriver.ChromeOptions()
            # chrome is set to headless
            options.add_argument('headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-default-apps')
            driver = se.webdriver.Chrome(chrome_options=options)

            # add_gened(gen)
            get_courses(gen, driver)

        finally:
            driver.quit()
            q.task_done()

def run2(q):
     while not q.empty():
        gen = q.get()
        try:
            options = se.webdriver.ChromeOptions()
            # chrome is set to headless
            options.add_argument('headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-default-apps')
            driver = se.webdriver.Chrome(chrome_options=options)

            # add_gened(gen)
            for key, value in all_gens_dict.items():
                add_gpa_field(gen, key, driver)

        finally:
            driver.quit()
            q.task_done()

new_list = dict()
if __name__ == '__main__':

    start_time = time.time()
    open('data.txt', 'w').close()
    for gen in gens_list:
        jobs.put(gen)
    for gen in gens_list:
        jobs2.put(gen)

    for i in range(5):
        worker = threading.Thread(target=run, args=(jobs,))
        worker.start()
    jobs.join()

    for i in range(5):
        worker = threading.Thread(target=run2, args=(jobs2,))
        worker.start()
    jobs2.join()
    print("--- Completed in %s seconds ---" % round(time.time() - start_time, 2))

    with open('course_data.pkl', 'wb') as output:
        # print(all_gens_dict["DVUP"][0].course_name)
        for key, course in all_gens_dict.items():
            pickle.dump(course, output, pickle.HIGHEST_PROTOCOL)


    with open('course_data.pkl', 'rb') as input:
        # company1 = pickle.load(input)
        for key, course in all_gens_dict.items():
            print(course.course_name)
            new_list[course.course_name] = course
    for key, value in new_list.items():
        if (key == "AOSC200"):
            print("asdfasdfasdf")
            print(value.course_name)
            print(value.gen_eds[0])


