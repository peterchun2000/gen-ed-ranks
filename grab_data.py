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


def prof_data(course_in, gen_ed, prof_name, driver):
    try:
        pterp_url = 'https://planetterp.com/'
        driver.get(pterp_url)

        search = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="main-search"]')))
        search.send_keys(prof_name)

        enter = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/form/button')))
        enter.click()
        try:
            view = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="grades-button"]')))
            view.click()
        except TimeoutException:
            return -1

        try:
            # clicks on drop down menu

            course_xpath = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="grades-by-course"]')))

            course_xpath.click()

            for course in course_xpath.find_elements_by_tag_name('option'):
                # equals to same course
                if course.get_attribute("value") == course_in:
                    course.click()

        except NoSuchElementException:
            return -1

        try:
            gpa_text = driver.find_element(
                By.XPATH, '//*[@id="grade-statistics"]').text
        except NoSuchElementException:
            return -1
        start_gpa_i = gpa_text.find(':')
        end_gpa_i = gpa_text.find(' ', start_gpa_i+2)
        if(start_gpa_i == -1):
            return -1
        gpa = float(gpa_text[start_gpa_i+2:end_gpa_i])

        index_of_course = find_course(gen_ed, course_in)
        # adds the gpa to the course obj
        samp_num_st = gpa_text.find('between')+8
        samp_num_end = gpa_text.find(' ', samp_num_st)
        samp_num = int(gpa_text[samp_num_st:samp_num_end].replace(',', ''))

        # adds the sample number to the course obj

        all_gens_dict[gen_ed][index_of_course].prof_list[prof_name].avg_gpa = gpa
        all_gens_dict[gen_ed][index_of_course].prof_list[prof_name].samp_size = samp_num
    except:
        print("failed")
        return -1


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

    def get_course_name(self):
        return self.course_name

    def __eq__(self, other):
        if isinstance(other, Course):
            return self.course_name.lower() == other.course_name.lower()
        return False


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

            # adds each course to the set within the dict[gen_ed]
            all_gens_dict[gen_ed].append((Course(course_name)))

            # start of testing
            try:
                section_set = course.find_element_by_class_name(
                    "sections-fieldset")
                view = WebDriverWait(section_set, 2).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'toggle-sections-link-text')))
                # clicks on expand sections
                view.click()

                section_grid = WebDriverWait(course, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'sections-container')))
                section_list = section_grid.find_elements(
                    By.CLASS_NAME, "delivery-f2f")
                index_of_course = find_course(gen_ed, course_name)
                for section in section_list:
                    s1 = section.find_element_by_class_name("section-instructor")
                    # prof_name = section.find_elements(By.XPATH, "//div[@class='section-instructor']")
                    if s1.text != "Instructor: TBA":
                        all_gens_dict[gen_ed][index_of_course].prof_list[s1.text] = (
                            Proffessor(s1.text, 0, 0))
            except:
                continue


def add_gened(gen_ed):
    global all_gens_dict
    all_gens_dict[gen_ed] = []


def add_gpa_field(gen_ed, course_in, driver):
    global all_gens_dict
    pterp_url = 'https://planetterp.com/course/'+course_in
    try:
        driver.get(pterp_url)
    except TimeoutException:
        print("failed")
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
    index_of_course = find_course(gen_ed, course_in)
    # adds the gpa to the course obj
    all_gens_dict[gen_ed][index_of_course].avg_gpa = gpa

    samp_num_st = gpa_text.find('between')+8
    samp_num_end = gpa_text.find(' ', samp_num_st)
    samp_num = int(gpa_text[samp_num_st:samp_num_end].replace(',', ''))

    # adds the sample number to the course obj
    all_gens_dict[gen_ed][index_of_course].samp_num = samp_num


def find_course(gen_ed, course_in):
    try:
        return all_gens_dict[gen_ed].index(Course(course_in))
    except:
        return -1


def remove_empty(gen_ed):
    for course in all_gens_dict[gen_ed][:]:
        if(course.avg_gpa == 0):
            all_gens_dict[gen_ed].remove(course)


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

            add_gened(gen)
            get_courses(gen, driver)

            for course in all_gens_dict[gen]:
                for key, val in course.prof_list.items():
                    prof_data(course.course_name, gen, key, driver)

            for course in all_gens_dict[gen]:
                add_gpa_field(gen, course.course_name, driver)

            remove_empty(gen)

        finally:
            driver.quit()
            q.task_done()


jobs = Queue()
gens_list = {"DSHS", "DSHU", "DSNS", "DSNL", "DSSP", "DVCC", "DVUP", "SCIS"}
course_dict = dict()
if __name__ == '__main__':

    start_time = time.time()
    open('data.txt', 'w').close()
    for gen in gens_list:
        jobs.put(gen)

    # this changes the number of threads that will run at once (recommended number: 4 for normal computer)
    for i in range(4):
        worker = threading.Thread(target=run, args=(jobs,))
        worker.start()

    jobs.join()

    print("--- Completed in %s seconds ---" %
          round(time.time() - start_time, 2))

    # adds the course into the dict
    for key, value in all_gens_dict.items():
        for course in value:
            course_dict[course.course_name] = course

    # adds the gen eds fields to each of the keys/val pair
    for key, courses in all_gens_dict.items():
        for course in courses:
            course_dict[course.course_name].gen_eds.append(key)

    # uploads it to the db
    with open('course_data.pkl', 'wb') as output:
        for key, value in course_dict.items():
            pickle.dump(value, output, pickle.HIGHEST_PROTOCOL)
