import tkinter as tk
from iLearn_File_Downloader import single_course_download, main_download_loop
from database import add_course, get_semester_courses
import yaml, os, request_functions





def load_config():
    __path__ = os.path.join(os.path.dirname(__file__), "config.yaml").replace('/','//')
    print(__path__)
    with open(__path__, 'r') as config:
        try:
            return yaml.load(config)
        except:
            print("Error loading config file")
            return None


class Downloader(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.winfo_toplevel().title("iLearn Downloader")
        self.ilearn_session_open = False


        self.geometry("500x500")

        self.program_name_label = tk.Label(self)

        ### open ilearn session Button ###
        self.open_ilearn_connection = tk.Button(self, text="Open iLearn Session", command=self.open_ilearn_connecton)
        self.open_ilearn_connection.grid(row=1, column=3)
        ###

        ### info label ###
        self.feed_back_label = tk.Label(self, text= 'iLearn Downloader')
        self.feed_back_label.grid(row=0, column=3)
        ###

        ### course list window ###
        self.courses_label = tk.Label(self, text='', justify='left')
        self.courses_label.grid(row=7, column=0, columnspan=4, pady = 10, padx=5)


        ### Main Course Crawl Button
        self.crawl_all_courses = tk.Button(self, text="Get All Courses", command=self.download_all_courses)
        self.crawl_all_courses.grid(row=6, column=1, pady = 10)
        ###

        ### Single Course Run ###
        self.course_id_to_run_label = tk.Label(self, text="Course ID")
        self.course_id_to_run = tk.Entry(self)
        self.run_course = tk.Button(self, text="Download Course", command=self.get_single_course)
        self.course_id_to_run_label.grid(row=0, column=0)
        self.course_id_to_run.grid(row=0, column=1, pady=5)
        self.run_course.grid(row=1, column=1, pady=5)
        ###

        ### Course Adding Section ###
        self.course_id_to_enter_label = tk.Label(self, text = "Course ID")
        self.course_id_to_enter = tk.Entry(self)
        self.course_semester_to_enter_label = tk.Label(self, text = "Semester")
        self.course_semester_to_enter = tk.Entry(self)
        self.course_folder_name_label = tk.Label(self, text ="Save Folder")
        self.course_folder_name = tk.Entry(self)
        self.add_course = tk.Button(self, text="Add Course", command=self.add_course)
        self.course_id_to_enter_label.grid(row=2, column=0)
        self.course_id_to_enter.grid(row=2, column=1)
        self.course_semester_to_enter_label.grid(row=3, column=0)
        self.course_semester_to_enter.grid(row=3, column=1)
        self.course_folder_name_label.grid(row=4, column=0)
        self.course_folder_name.grid(row=4, column=1)
        self.add_course.grid(row=5, column=1, pady = 5)
        ###


        self.get_current_course_list()

    def get_single_course(self):
        if self.ilearn_session_open:
            self.feed_back_label['text'] = "Downloading Single Course"
            print(self.course_id_to_run.get())
            single_course_download(self.course_id_to_run.get())
        else:
            self.feed_back_label['text'] = "No Ilearn Session Open"


    def add_course(self):
        course_id = self.course_id_to_enter.get()
        course_semester = self.course_semester_to_enter.get()
        course_folder_name = self.course_folder_name.get()

        if course_id is '' or course_semester is '' or course_folder_name is '':
            self.feed_back_label['text'] = "Missing Something. Can't Add"
        else:
            self.feed_back_label['text'] = "Adding Course"
            add_course(course_id, course_semester, course_folder_name)



    def download_all_courses(self):
        if self.ilearn_session_open == True:
            self.feed_back_label['text'] = "Downloading all courses"
            main_download_loop(load_config()['semester'])
        else:
            self.feed_back_label['text'] = "No iLearn Session Open"
        return

    def open_ilearn_connecton(self):
        set_session = request_functions.open_iLearn_connection()
        self.feed_back_label['text'] = "Updated"
        if set_session:
            self.feed_back_label['text'] = "iLearn Session Opened"
            self.ilearn_session_open = True
        else:
            self.feed_back_label['text'] = "Could Not Open Session"


    def get_current_course_list(self):
        current_courses_str = ''
        current_courses = get_semester_courses(load_config()['semester'])
        for course in current_courses:
            if course.course_title is not None:
                current_courses_str = current_courses_str + course.course_title + "\n"
        self.courses_label['text'] = current_courses_str






load_config()
w = Downloader()
w.mainloop()