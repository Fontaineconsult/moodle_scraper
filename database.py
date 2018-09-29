from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine("sqlite:///C:\\Users\\913678186\\Box\\SF State Python Projects\\iLearn Scraper Version 2\\database.db")
Base = declarative_base()


class Course(Base):
    __tablename__ = 'course'

    id = Column(Integer, primary_key=True)
    course_id = Column(String)
    course_title = Column(String)
    semester = Column(String)
    service_type = Column(String)
    course_folder_name = Column(String)

class Resources(Base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True)
    resource_name = Column(String)
    resource_link = Column(String)
    resource_type = Column(String)
    course_id = Column(String, ForeignKey('course.id'))
    date_added = Column(DateTime, default=datetime.utcnow)
    course = relationship(Course)


Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def update_course_title(course_id, title):
    course = session.query(Course).filter_by(course_id=course_id).first()
    if course:
        course.course_title = title
        session.commit()



def update_course_folder(course_id, course_name):
    course = session.query(Course).filter_by(course_id=course_id).first()
    if course:
        course.course_folder_name = course_name
        session.commit()
    else:
        return "course not found"
def get_single_course(course_id):

    course = session.query(Course).filter_by(course_id=course_id).first()
    if course:
        return course
    else:
        print("No Course Found For ID: {}".format(course_id))
        return None
def get_semester_amp_courses(semester):

    course_query = session.query(Course).filter_by(semester=semester, service_type='amp').all()

    if course_query:
        return course_query
    else:
        return None

def get_semester_cap_courses(semester):

    course_query = session.query(Course).filter_by(semester=semester,
                                                   service_type='cap').all()

    if course_query:
        return course_query
    else:
        return None

def add_course(page_id, semester, course_title, service_type):
    if course_title == '':
        course_title = ''

    allowed_types = ['amp', 'cap']
    if service_type in allowed_types:

        does_it_already_exist = session.query(Course).filter_by(course_id=page_id,
                                                                semester=semester,
                                                                service_type=service_type).first()

        if does_it_already_exist is None:

            course = Course(course_id=page_id,
                            semester=semester,
                            course_folder_name=course_title,
                            service_type=service_type)
            session.add(course)
            print("Committing to Courses", course)
            session.commit()
            return True
        else:
            print("Course Already Exists")
            return False


def check_or_commit_course(page_id, course_name):
    print(page_id)
    check_course = session.query(Course).filter_by(course_id=page_id).first()
    print(check_course.course_id)
    if check_course:

        if check_course.course_title == '':
            check_course.course_title = course_name
            session.commit()
            return True
        else:
            return True

    else:
        commit_course(page_id,course_name)
        return False
def check_or_commit_resource(name, link, type, course_id):
    check_resource = session.query(Resources).filter_by(resource_link=link, course_id=course_id).first()

    if check_resource:
        print("Returning True")
        return True
    else:
        print("Returning False")
        commit_resource(name, link, type, course_id)
        return False
def commit_course(course_id, course_name, course_folder_name, service_type):
    allowed_types = ['amp', 'cap']

    if service_type.lower() in allowed_types:

        course = Course(course_id=course_id,
                        course_title=course_name,
                        course_folder_name=course_folder_name,
                        service_type=service_type)
        session.add(course)
        session.commit()
        return True
    else:
        return False
def commit_resource(name, link, type, course_id):
    resource = Resources(resource_name=name,
                         resource_link=link,
                         resource_type=type,
                         course_id=course_id)
    session.add(resource)
    session.commit()
def flush_all_resources():
    try:
        delete_all = session.query(Resources).delete()
        session.commit()
        print("All resources deleted")
    except:
        print("There was a problem. Nothing deleted")
        session.rollback()
def flush_all_courses():
    try:
        delete_all = session.query(Course).delete()
        session.commit()
        print("All courses deleted")
    except:
        print("There was a problem. Nothing deleted")
        session.rollback()

def get_add_date(link):
    date_query = session.query(Resources).filter_by(resource_link=link).first()
    if date_query:
        return date_query.date_added
    else:
        return None
def get_courses_resources(course_id):
    all_course_resources = session.query(Resources).filter_by(course_id=course_id).all()
    course_title = all_course_resources.course.course_title
    print(course_title)

def get_course_videos(course_id):
    video_query = session.query(Resources).filter_by(course_id=course_id, resource_type='video')
    if video_query:
        return video_query
    else:
        return None

