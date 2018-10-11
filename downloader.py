from moodle_core_objects import IlearnCoursePage
import os
import win32com.client
import traceback
from database import check_or_commit_course, check_or_commit_resource
import download_reporter as dr

##! missing ereserves download code

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


def iLearn_file_downloader(passed_in_ilearn_page, save_location, course_folder):

    iLearn_page = passed_in_ilearn_page

    dr.set_current_course_log(iLearn_page.page_id, iLearn_page.course_name)


    ilearn_course_name = scrub_filename(iLearn_page.course_name)

    split_ilearn_name = ilearn_course_name.split()

    if course_folder == '':
        formatted_name = "{}{}".format(split_ilearn_name[0], split_ilearn_name[1])
        formatted_name = scrub_filename(formatted_name)

    else:
        formatted_name = course_folder

    course_folder = os.path.join(save_location, course_folder)

    if not os.path.exists(course_folder):
        os.mkdir(course_folder)


    save_folder = os.path.join(save_location, formatted_name, ilearn_course_name + " - iLearn Content")
    save_folder = os.path.normpath(save_folder)


    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    check_or_commit_course(iLearn_page.page_id, iLearn_page.course_name)

    if iLearn_page.eReserve_files:

        ereserves_folder = os.path.join(save_folder, "eReserves")

        if not os.path.exists(ereserves_folder):
            os.mkdir(ereserves_folder)


        for content in iLearn_page.eReserve_files:
            download_and_save(content, iLearn_page, ereserves_folder)

    staged_resources = iLearn_page.get_staged_content()

    for section in staged_resources:

        if len(section['resources']) > 0:
            section_dir = os.path.join(save_folder, section['section'])
            if not os.path.exists(section_dir):
                os.mkdir(section_dir)

            for content in section['resources']:
                if not content.hidden:
                    download_and_save(content, iLearn_page, section_dir)
                else:
                    print("{} is hidden".format(content.resource_title))
                    continue

def download_and_save(content, iLearn_page, local_save_folder):
    if check_or_commit_resource(content.resource_title,
                                content.resource_link,
                                content.resource_type,
                                iLearn_page.page_id):
        dr.log_resource_exists(content)
    else:

        resource_get = content()
        print("THISISTHECONENT", content)
        section_dir_local = local_save_folder
        folder = None
        if resource_get['folder'] is not None:
            folder_id = resource_get['folder']
            folder_path = os.path.join(section_dir_local, 'Folder ' + folder_id)
            folder = folder_path
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)
        if folder:
            section_dir_local = folder

        if resource_get['resource-type'] == 'file':
            try:
                with open(os.path.join(section_dir_local, scrub_filename(resource_get['title'])), 'wb') as file:
                    try:
                        file.write(resource_get['resource'].content)
                    except AttributeError:
                        ##! log this
                        pass
            except FileNotFoundError:
                short_title = resource_get['title'][5:]
                short_dir = section_dir_local + short_title

                with open(scrub_filename(short_dir), 'wb') as file:
                    try:
                        file.write(resource_get['resource'].content)
                    except AttributeError:
                        ##! log this
                        pass
            except OSError:
                dr.log_error("Problem with file name", traceback.format_exc(), resource_get['title'])

        elif resource_get['resource-type'] == 'Other':
            url = resource_get['resource']
            create_url_shortcut(url, section_dir_local)

        elif resource_get['resource-type'] == 'video':
            video_dir = os.path.join(section_dir_local, "Videos")

            if not os.path.exists(video_dir):
                os.mkdir(video_dir)
            item_url = resource_get['resource']
            create_url_shortcut(item_url, video_dir)

        dr.log_file_download(content)


def scrub_filename(filename):
    filename=filename

    char_to_remove = ['"', '*', ':', '<', '>', '?', '/', '~', '#', '%', '&', '{', '}', ':', ';']
    for char in filename:
        if char in char_to_remove:

            filename = filename.replace(char, '')

    return filename

def create_url_shortcut(url, save_directory):
    print("URL TO CLEAN", url)
    fixed_url = url.replace('/', '_')\
        .replace('.', ' ')\
        .replace(':','')\
        .replace('?','')\
        .replace('=','')\
        .replace('http','')\
        .replace('html','')\
        .replace('com','')

    path = os.path.join(save_directory,fixed_url)
    if len(path) > 254:
        path = path[0:254] + '.url'
    else:
        path = path + '.url'
    ws = win32com.client.Dispatch("wscript.shell")
    scut = ws.CreateShortcut(path)
    scut.TargetPath = url
    scut.Save()

