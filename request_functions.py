import requests
import requests.exceptions
import urllib3
import urllib3.exceptions
import traceback
import download_reporter as dr
import os, yaml




def load_config():
    __path__ = os.path.join(os.path.dirname(__file__), "config.yaml").replace('/','//')
    print(__path__)
    with open(__path__, 'r') as config:
        try:
            return yaml.load(config)
        except:
            print("Error Loading Config File")
            return None


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


ilearn_session = requests.session()


base_course_url = load_config()['base_ilearn_course_url']

def open_iLearn_connection():
    global ilearn_session

    config_file = load_config()

    url = config_file['iLearn_page']
    referer = {"referer": config_file['referrer_page']}
    username = config_file['iLearn_login']
    password = config_file['iLearn_pass']
    login_data = dict(username=username, password=password)
    try:
        ilearn_session.get(url)
        if ilearn_session.cookies.get_dict():
            ilearn_session.post(url, data=login_data, headers=referer)
            return True
        else:
            ilearn_session = None
            print("Couldn't reach {}".format(referer))
            return False


    except:
        dr.log_error("Couldn't Connect to iLearn", url, traceback.format_exc())
        ilearn_session = None
        return False


def iLearn_login_session(calling_function):
    print(ilearn_session)
    if ilearn_session is not None:
        print(ilearn_session.cookies.get_dict())
        def resource_wrapper(resource_url):
            request_object = calling_function(resource_url, ilearn_session)
            return request_object
        return resource_wrapper
    else:
        raise Exception("Couldn't Connect to iLearn")


@iLearn_login_session
def get_resources_header(resource_url, *session):
    session = session[0]
    try:
        header = session.head(resource_url)
        return header
    except (requests.exceptions.SSLError,
            requests.exceptions.ConnectionError,
            urllib3.exceptions.MaxRetryError,
            urllib3.exceptions.NewConnectionError):
        dr.log_error("HEAD REQUEST: Failed to establish a new connection, Max Retries", resource_url, traceback.format_exc())
        return None
    except:
        dr.log_error("HEAD REQUEST: Some Other Type of Error", resource_url, traceback.format_exc())
        return None


@iLearn_login_session
def get_ilearn_page(resource_url, *session):
    session = session[0]
    resource = session.get(base_course_url + resource_url)
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
        secondary_link_pages.append(((link, course_page_html.status_code), course_page_html.content) )
        return secondary_link_pages
    return secondary_link_pages

@iLearn_login_session
def download_ilearn_resource(resource_url, *session):
    return session[0].get(resource_url)
