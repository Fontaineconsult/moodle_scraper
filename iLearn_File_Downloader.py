from database import get_semester_courses
from downloader import iLearn_file_downloader

master_folder = "C:/Users/913678186/Box/SF State Python Projects/iLearn Scraper Version 2/test/"

def load_course_check_list(semester):
    current_courses = get_semester_courses(semester)
    course_ids = []
    for course in current_courses:
        course_ids.append(course.course_id)
    return course_ids


def main_download_loop(semester):

    current_courses = load_course_check_list(semester)

    for course_id in current_courses:
        print("Startind DL for course ID", course_id)
        iLearn_file_downloader(course_id, master_folder)

main_download_loop("Fall 2018")