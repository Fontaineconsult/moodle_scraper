import logging
logging.basicConfig(filename='test.log', level=logging.INFO)

searched_courses = []

current_course_class = None


class current_course:

    def __init__(self, course_id, course_name):
        self.course_id = course_id
        self.course_name = course_name
        self.files_downloaded = []
        self.files_not_downloaded = []





def set_current_course_log(course_id, course_name):

    global current_course_class

    if current_course_class is not None:
        searched_courses.append(current_course_class)

        current_course_class = current_course(course_id, course_name)
    else:
        current_course_class = current_course(course_id, course_name)





def test_report(report_info):
    logging.info("{} courses checked".format(str(len(report_info))))




def log_resource_exists(resource):
    current_course_class.files_not_downloaded.append(resource)


def log_file_download(resource):
    current_course_class.files_downloaded.append(resource)

def log_error(short_name, link, error):
    logging.error("{} {} {}".format(short_name, link, error))

def build_report():
    reports = []
    for course in searched_courses:
        files_downloaded = len(course.files_downloaded)
        files_not_downloaded = len(course.files_not_downloaded)
        course_name = course.course_name
        report = "{} files downloaded, {} already downloaded for: course {}".format(files_downloaded,
                                                                              files_not_downloaded,
                                                                              course_name)
        reports.append(report)
    logging.info("-------------------------")
    for each in reports:
        logging.info(each)



