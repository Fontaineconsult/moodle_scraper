from moodle_core_objects import IlearnCoursePage
from request_functions import open_iLearn_connection
from database import get_add_date, check_or_commit_resource, get_semester_cap_courses, update_course_title
import requests
import json
import traceback

open_iLearn_connection()


def load_semester_cap_courses(semester):
    course_pages = []
    courses = get_semester_cap_courses(semester)
    for course_id in courses:
        course_pages.append(course_id.course_id)
    return course_pages



def update_cap_courses(semester):

    cap_courses = load_semester_cap_courses(semester)

    if cap_courses is not None:

        for course_page in cap_courses:

            ilearn_page = IlearnCoursePage(course_page)

            course_section_content = ilearn_page.get_sect_dict()
            update_course_title(course_page, ilearn_page.course_name)

            n = 0

            all_section_data = []

            for x in range(len(course_section_content)):

                section_num = "Section-{}".format(n)

                section = course_section_content[section_num]

                section_dict = {'section_num': section_num, 'section_content': []}

                for resource in section:
                    if resource.service_type == 'captioning':


                        if not check_or_commit_resource(resource.resource_title, resource.resource_link, resource.resource_type, course_page):
                            pass
                            ##! disabled for now
                        else:
                            print("ALREADY GOT YO")
                            pass

                        section_dict['section_content'].append({'type': resource.resource_type,
                                                                'link': resource.resource_link,
                                                                'title': resource.resource_title,
                                                                'scan_date': str(get_add_date(resource.resource_link))})
                        print("ADDING")


                all_section_data.append(section_dict)
                n += 1

            data_to_upload = {
                'course_name': ilearn_page.course_name,
                'course_id': course_page,
                'semester': 'Fall 2018',
                'content': all_section_data
            }

            print(data_to_upload)


            try:
                requests.post("https://amp.sfsu.edu/api/ilearn-cap", data=json.dumps(data_to_upload), verify=False)
            except:
                print(traceback.print_exc())
    else:
        return None

if __name__ == '__main__':
    update_cap_courses("Fall 2018")