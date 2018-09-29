from database import get_semester_amp_courses, get_single_course, update_course_title
from downloader import iLearn_file_downloader
from moodle_core_objects import IlearnCoursePage
import os
import download_reporter as dr
import yaml, request_functions
import traceback

master_folder = None


def load_config():
    __path__ = os.path.join(os.path.dirname(__file__), "config.yaml").replace('/','//')
    try:
        with open(__path__, 'r') as config:
            try:
                return yaml.load(config)
            except:
                print("Error loading config file")
                return None
    except:
        print(traceback.print_exception())


def load_course_check_list(semester):
    current_courses = get_semester_amp_courses(semester)
    course_ids = []
    if current_courses is not None:
        for course in current_courses:
            course_ids.append( (course.course_id, course.course_folder_name, course.course_title) )
        return course_ids
    else:
        print("No courses found")


def main_download_loop(semester):

    current_courses = load_course_check_list(semester)

    print("Beginning check for {} courses".format(len(current_courses)))

    for course in current_courses:
        course_to_download = IlearnCoursePage(course[0])
        update_course_title(course[0], course_to_download.course_name)
        print("Startind DL for course ID", course[0])
        course_folder = course[1]

        iLearn_file_downloader(course_to_download, load_config()['save_location'], course_folder)
        print("finished downloading", course_to_download.course_name)
    dr.build_report()
    return


def single_course_download(course_id):
    current_course = get_single_course(course_id)

    course_id = current_course.course_id
    course_folder = current_course.course_folder_name


    course_to_download = IlearnCoursePage(course_id)

    iLearn_file_downloader(course_to_download, load_config()['save_location'], course_folder)

    dr.build_report()
    return


if __name__ == '__main__':
    try:
        request_functions.open_iLearn_connection()
        main_download_loop(load_config()['semester'])
    except:
        print("YIKES")
        print(traceback.print_exc())
