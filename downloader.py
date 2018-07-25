from moodle_core_objects import IlearnCoursePage
import os
import win32com.client

iLearn_page = IlearnCoursePage("16938")
course_content = iLearn_page.get_all_content()
print(iLearn_page.course_name)
test_folder = "C:/Users/913678186/Box/SF State Python Projects/iLearn Scraper Version 2/test/"

def download_all_page_content():

    save_folder = test_folder + iLearn_page.course_name + " - iLearn Content/"

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
                        file.write(item['resource'].content)

                elif item['resource-type'] == 'Other':
                    url = item['resource']
                    create_url_shortcut(url, section_dir_local)


                elif item['resource-type'] == 'video':
                    video_dir = section_dir_local + "videos/"
                    if not os.path.exists(video_dir):
                        os.mkdir(video_dir)

                    item_url = item['resource']
                    create_url_shortcut(item_url, video_dir)




def create_url_shortcut(url, save_directory):
    fixed_url = url.replace('/', '_').replace('.', ' ').replace(':','').replace('?','').replace('=','').replace('http','').replace('html','').replace('com','')
    path = save_directory + fixed_url
    if len(path) > 254:
        path = path[0:254] + '.url'
    else:
        path = path + '.url'
    ws = win32com.client.Dispatch("wscript.shell")
    scut = ws.CreateShortcut(path)
    scut.TargetPath = url
    scut.Save()




download_all_page_content()