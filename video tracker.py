from moodle_core_objects import IlearnCoursePage
from request_functions import open_iLearn_connection
from database import get_add_date, check_or_commit_resource, get_semester_cap_courses
import requests
import json


open_iLearn_connection()


def load_semester_cap_courses():
    course_pages = []
    courses = get_semester_cap_courses("Fall 2018")
    for course_id in courses:
        course_pages.append(course_id.course_id)
    return course_pages


cap_courses = load_semester_cap_courses()

print(cap_courses)

if cap_courses is not None:
    for course_page in cap_courses:

        ilearn_page = IlearnCoursePage(course_page)

        course_section_content = ilearn_page.get_sect_dict()
        print(course_section_content)
        n = 0
        upload_data = []
        for x in range(len(course_section_content)):

            section_num = "section-{}".format(n)

            section = course_section_content[section_num]
            section_dict = {section_num: []}

            for resource in section:

                if resource.resource_type == 'video':

                    if check_or_commit_resource(resource.resource_title, resource.resource_link, resource.resource_type, course_page):

                        section_dict[section_num].append({'type': resource.resource_type,
                                                           'link': resource.resource_link,
                                                           'title': resource.resource_title,
                                                           'scan_date': str(get_add_date(resource.resource_link))})

                        print(resource.resource_type, resource.resource_link, get_add_date(resource.resource_link), section_num, "OLD")
                    else:
                        print(resource.resource_type, resource.resource_link, get_add_date(resource.resource_link), section_num, "NEW")

            upload_data.append(section_dict)
            n += 1
        print("UPLOAD DATA", upload_data)
        requests.post("http://127.0.0.1:5000/api/ilearn-cap", data=json.dumps({'course_name': ilearn_page.course_name,
                                                                               'course_id': course_page,
                                                                               'semester': 'Fall 2018', ##! Fix
                                                                               'content': upload_data}))