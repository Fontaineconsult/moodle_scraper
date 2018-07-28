from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
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

class Resources(Base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True)
    resource_name = Column(String)
    resource_link = Column(String)
    resource_type = Column(String)
    course_id = Column(String, ForeignKey('course.id'))
    course = relationship(Course)


Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()



def get_semester_courses(semester):
    print(semester)
    course_query = session.query(Course).filter_by(semester=semester).all()

    return course_query


def add_course(page_id, semester):
    course = Course(course_id=page_id, semester=semester, course_title='')
    session.add(course)
    print("Committing to Courses", course)
    session.commit()


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
        print("already exists")
        return True
    else:
        print("doesn't exist")
        commit_resource(name, link, type, course_id)
        return False


def commit_course(course_id, course_name):
    course = Course(course_id=course_id,
                    course_title=course_name)
    session.add(course)
    session.commit()



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