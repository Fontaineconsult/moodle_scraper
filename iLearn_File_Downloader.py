from database import get_semester_courses, get_single_course
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
            course_ids.append( (course.course_id, course.course_folder_name) )
        return course_ids
    else:
        print("No courses found")


def main_download_loop(semester):

    current_courses = load_course_check_list(semester)

    print("Beginning check for {} courses".format(len(current_courses)))

    for course in current_courses:
        print("Startind DL for course ID", course[0])
        course_id = course[0]
        course_folder = course[1]

        iLearn_file_downloader(course_id, master_folder, course_folder)

    dr.build_report()



def single_course_download(course_id):
    current_course = get_single_course(course_id)

    course_id = current_course.course_id
    course_folder = current_course.course_folder_name

    iLearn_file_downloader(course_id, master_folder, course_folder)

    dr.build_report()





if __name__ == '__main__':
    main_download_loop("Fall 2018")
    