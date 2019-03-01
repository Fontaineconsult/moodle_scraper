import filter_functions as ifilter
from bs4 import BeautifulSoup
from request_functions import get_ilearn_page, get_ereserves_page


##! Need a way to not get hidden resources
class _IlearnCourseSection:

    def __init__(self, section_content, section_id):
        self.section_id = section_id
        self.section_content = section_content
        self.section_summary = ifilter.get_section_summary(section_content)
        self.raw_section_links = (self.section_id, ifilter.get_section_links(section_content))
        self.section_resources = ifilter.sort_for_content_links(self.raw_section_links)
        self.suspect_links = []


class IlearnCoursePage:

    def __init__(self, page_id):
        self.page_id = page_id
        self.raw_course_page_html = get_ilearn_page(self.page_id)
        self.parsed_html = BeautifulSoup(self.raw_course_page_html, "html.parser")
        self.course_sections = [_IlearnCourseSection(content[0], content[1]) for content
                                in ifilter.get_section_content(self.parsed_html)
                                if content]
        self.course_name = self.parsed_html.find('title', text=True).text[8:]
        self.course_heading = self.parsed_html.find('h1', text=True)
        self.eReserve_files = self.check_eReserves()

    def get_all_resource_links(self):
        links_to_return = []
        for section in self.course_sections:
            for resource in section.section_resources:
                links_to_return.append(resource.resource_link)
        return links_to_return

    def get_sections(self):
        sections_to_return = []
        for section in self.course_sections:
            sections_to_return.append(section)
        return sections_to_return

    def get_sect_dict(self):
        section_dict = dict(zip([x.section_id for x in self.course_sections],
                                [x.section_resources for x in self.course_sections]))
        return section_dict

    def check_eReserves(self):
        eReserve_block = self.parsed_html.find('aside', {'data-block': 'ereserves'})
        if eReserve_block:
            ereserves_link = ifilter.construct_ereserves_request_link(eReserve_block)
            ereserves_page = BeautifulSoup(get_ereserves_page(ereserves_link), "html.parser")
            ereserves_main_content = ereserves_page.find('div', {'role':'main'})
            ereserves_page_links = ifilter.get_section_links(ereserves_main_content)
            ereserve_content = ifilter.sort_for_content_links((None, ereserves_page_links))
            return ereserve_content

        else:
            return None

    def get_all_content(self):
        return_list = []
        for IlearnCourseSection in self.course_sections:

            section = {"section": IlearnCourseSection.section_id, "resources": []}

            for resource in IlearnCourseSection.section_resources:
                section["resources"].append(resource())

            return_list.append(section)
        return return_list

    def get_staged_content(self):
        return_list = []

        for IlearnCourseSection in self.course_sections:

            section = {"section": IlearnCourseSection.section_id, "resources": []}

            for resource in IlearnCourseSection.section_resources:
                section["resources"].append(resource)

            return_list.append(section)

        return return_list

    def __len__(self):
        return len(self.course_sections)
