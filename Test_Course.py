from moodle_core_objects import IlearnCoursePage
from request_functions import open_iLearn_connection


open_iLearn_connection()
test = IlearnCoursePage('15250')
print(test.get_staged_content())

staged_content = test.get_staged_content()

for each in  staged_content[1]['resources']:

    print(each.resource_link)
    print(each.file_type)
    print(each.resource_type)
    print(each.resource_title)
    print(each.downloadable)
    print(each.file_extension)
    print(each.file_extension)
    print(each.moodle_resource)
    print("____")