from database import get_semester_courses
from downloader import iLearn_file_downloader
import os
import download_reporter as dr





master_folder = "Z:/Edit Files/semesters/Fall 2018/"
os.chdir(master_folder)

def load_course_check_list(semester):
    current_courses = get_semester_courses(semester)
    course_ids = []
    if current_courses is not None:
        for course in current_courses:
            course_ids.append(course.course_id)
        return course_ids
    else:
        print("No courses found")


def main_download_loop(semester):

    current_courses = load_course_check_list(semester)

    for course_id in current_courses:
        print("Startind DL for course ID", course_id)



        iLearn_file_downloader(course_id, master_folder)

if __name__ == '__main__':
    main_download_loop("Fall 2018")
    