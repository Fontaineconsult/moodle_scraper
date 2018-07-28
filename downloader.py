from moodle_core_objects import IlearnCoursePage
import os
import win32com.client
from database import check_or_commit_course, check_or_commit_resource

def download_all_page_content(iLearn_Page_id, save_location):
    iLearn_page = IlearnCoursePage(iLearn_Page_id)
    course_content = iLearn_page.get_all_content()

    save_folder = save_location + iLearn_page.course_name + " - iLearn Content/"

    if not os.path.exists(save_folder):
        os.mkdir(save_folder)
    for section in course_content:
        if len(section['resources']) > 0:
            section_dir = save_folder + section['section'] + "/"
            if not os.path.exists(section_dir):
                os.mkdir(section_dir)
            for item in section['resources']:
                section_dir_local = section_dir

                folder = None
                if item['folder'] is not None:
                    folder_id = item['folder']
                    folder_path = section_dir_local + 'Folder ' + folder_id + "/"
                    folder = folder_path
                    if not os.path.exists(folder_path):
                        os.mkdir(folder_path)
                if folder:
                    section_dir_local = folder
                if item['resource-type'] == 'file':
                    with open(section_dir_local + item['title'], 'wb') as file:
                        try:
                            file.write(item['resource'].content)
                        except AttributeError:
                            ##! log this
                            pass
                elif item['resource-type'] == 'Other':
                    url = item['resource']
                    create_url_shortcut(url, section_dir_local)
                elif item['resource-type'] == 'video':
                    video_dir = section_dir_local + "videos/"
                    if not os.path.exists(video_dir):
                        os.mkdir(video_dir)
                    item_url = item['resource']
                    create_url_shortcut(item_url, video_dir)


def iLearn_file_downloader(iLearn_Page_id, save_location):

    iLearn_page = IlearnCoursePage(iLearn_Page_id)

    save_folder = save_location + iLearn_page.course_name + " - iLearn Content/"

    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    check_or_commit_course(iLearn_Page_id, iLearn_page.course_name)

    staged_resources = iLearn_page.get_staged_content()

    print(staged_resources)

    for section in staged_resources:

        if len(section['resources']) > 0:
            section_dir = save_folder + section['section'] + "/"

            if not os.path.exists(section_dir):
                os.mkdir(section_dir)

            for item in section['resources']:
                if check_or_commit_resource(item.resource_title,
                                            item.resource_link,
                                            item.resource_type,
                                            iLearn_Page_id):

                    print("already exists")
                else:
                    resource_get = item()
                    print(resource_get)
                    section_dir_local = section_dir

                    folder = None

                    if resource_get['folder'] is not None:
                        folder_id = resource_get['folder']
                        folder_path = section_dir_local + 'Folder ' + folder_id + "/"
                        folder = folder_path
                        if not os.path.exists(folder_path):
                            os.mkdir(folder_path)
                    if folder:
                        section_dir_local = folder
                    if resource_get['resource-type'] == 'file':
                        try:
                            with open(section_dir_local + resource_get['title'], 'wb') as file:
                                try:
                                    file.write(resource_get['resource'].content)
                                except AttributeError:
                                    ##! log this
                                    pass
                        except FileNotFoundError:
                            short_title = resource_get['title'][5:]
                            short_dir = section_dir_local + short_title
                            with open(short_dir, 'wb') as file:
                                try:
                                    file.write(resource_get['resource'].content)
                                except AttributeError:
                                    ##! log this
                                    pass

                            print("SAVING ERROR", len(section_dir_local + resource_get['title']))
                    elif resource_get['resource-type'] == 'Other':
                        url = resource_get['resource']
                        create_url_shortcut(url, section_dir_local)
                    elif resource_get['resource-type'] == 'video':
                        video_dir = section_dir_local + "videos/"
                        if not os.path.exists(video_dir):
                            os.mkdir(video_dir)
                        item_url = resource_get['resource']
                        create_url_shortcut(item_url, video_dir)


def create_url_shortcut(url, save_directory):
    fixed_url = url.replace('/', '_')\
        .replace('.', ' ')\
        .replace(':','')\
        .replace('?','')\
        .replace('=','')\
        .replace('http','')\
        .replace('html','')\
        .replace('com','')

    path = save_directory + fixed_url
    if len(path) > 254:
        path = path[0:254] + '.url'
    else:
        path = path + '.url'
    ws = win32com.client.Dispatch("wscript.shell")
    scut = ws.CreateShortcut(path)
    scut.TargetPath = url
    scut.Save()

