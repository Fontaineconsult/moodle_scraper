import requests
import requests.exceptions
import urllib3
import shutil
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)




def iLearn_login_session(calling_function):
##! how to do persistent session for whole program?
    url = 'https://ay1718.ilearn.support.at.sfsu.edu/local/hub/extlogin.php?wantsurl=https%3A%2F%2Fay1718.ilearn.support.at.sfsu.edu%2F'
    login_data = dict(username='913678186', password='learning books reading library')


    ilearn_session = requests.session()
    ilearn_session.get(url, verify=False)
    ilearn_session.post(url, data=login_data, headers={"Referer": "https://ay1617.ilearn.support.at.sfsu.edu"})

    def resource_wrapper(resource_url):
        request_object = calling_function(resource_url, ilearn_session)
        return request_object
    return resource_wrapper



@iLearn_login_session
def get_resources_header(resource_url, *session):
    session = session[0]
    try:
        header = session.head(resource_url)
        return header
    except:
        return None



@iLearn_login_session
def get_ilearn_page(resource_url, *session):
    session = session[0]
    resource = session.get("https://ay1718.ilearn.support.at.sfsu.edu/course/view.php?id=" + resource_url)
    return resource.content

@iLearn_login_session
def get_ilearn_resource(resource_url, *session):
    session = session[0]
    resource = session.get(resource_url)
    return resource.content


@iLearn_login_session
def get_resource_list(resource_list, *session):
    secondary_link_pages = []
    session = session[0]
    for link in resource_list:
        course_page_html = session.get(link)
        secondary_link_pages.append( ((link, course_page_html.status_code), course_page_html.content) )
        return secondary_link_pages
    return secondary_link_pages

@iLearn_login_session
def download_ilearn_resource(resource_url, *session):
    return session[0].get(resource_url)
