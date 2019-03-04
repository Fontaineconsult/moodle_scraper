
from ilearnscaperQT import Ui_MainWindow
from PyQt5 import QtWidgets
from iLearn_File_Downloader import main_download_loop
from database import add_course, get_semester_amp_courses, get_semester_cap_courses
import yaml, os, request_functions
from cap_tracker import update_cap_courses






def load_config():
    __path__ = os.path.join(os.path.dirname(__file__), "config.yaml").replace('/','//')
    print(__path__)
    with open(__path__, 'r') as config:
        try:
            return yaml.load(config)
        except:
            print("Error loading config file")
            return None



class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.setupUi(self)
        self.ilearn_session_open = False
        self.semester = load_config()['semester']
        self.pushButton_openconnection.clicked.connect(self.open_ilearn_connection)
        self.pushButton_downloadamp.clicked.connect(self.download_amp_courses)
        self.pushButton_scancap.clicked.connect(self.update_cap_courses)
        self.pushButton_addcourse.clicked.connect(self.add_course)
        self.init_lists()

    def open_ilearn_connection(self):
        set_session = request_functions.open_iLearn_connection()
        if set_session:
            self.ilearn_session_open = True
            print("good")
        else:
            print("bad")

    def download_amp_courses(self):
        if self.ilearn_session_open:
            main_download_loop(self.semester)
        else:
            print("no go")

    def update_cap_courses(self):
        if self.ilearn_session_open:
            update_cap_courses(self.semester)
        else:
            print("no go")


    def init_lists(self):
        current_amp_courses = get_semester_amp_courses(self.semester)
        current_cap_courses = get_semester_cap_courses(self.semester)
        print(current_amp_courses)

        if current_amp_courses:
            for each_course in current_amp_courses:
                print(each_course.course_title)
                self.listWidget_ampcourses.addItem(each_course.course_title)

        if current_cap_courses:
            for each_course in current_cap_courses:
                print(each_course.course_title)
                self.listWidget_capcourses.addItem(each_course.course_title)


    def add_course(self):
        course_id = self.textEdit_courseid.toPlainText()
        semester = self.textEdit_semester.toPlainText()
        save_folder = self.textEdit_savefolder.toPlainText()
        amp_state = self.radioButton_amptype.isChecked()
        cap_state = self.radioButton_cap_type.isChecked()

        if amp_state is True:
            print("amp")
            service_type = 'amp'
        elif cap_state is True:
            print("cap")
            service_type = 'cap'

        if course_id is not '' and semester is not '' and save_folder is not '':
            if amp_state is True or cap_state is True:
                add_the_course = add_course(course_id, semester, save_folder, service_type)
            else:
                print("nogo homo")
        else:
            print("Nyaano")



        print(course_id, semester,save_folder)






import sys


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())



