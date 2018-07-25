import re
import regexs
import request_functions as rf
from bs4 import BeautifulSoup


class InternalResource:

    def __init__(self, link):
        self.resource_link = link
        self.file_type = None
        self.resource_type = regexs.identify_resource_type(self.resource_link)
        self.resource_header = rf.get_resources_header(link)
        self.resource_title = None
        self.downloadable = False
        self.moodle_resource = regexs.identify_if_moodle(self.resource_link)
        self.folder = None
        self.initialize_resource()

    def initialize_resource(self):
        self.clean_resource_title()
        self.get_folder_id()

    def clean_resource_title(self):
        if 'Content-Disposition' in self.resource_header.headers:
            gross_title = self.resource_header.headers['Content-Disposition']
            actual_title = gross_title[22:-1].translate(str.maketrans('', '', '?'))
            self.resource_title = actual_title
            self.downloadable = True
        elif self.moodle_resource:
            file_name = self.resource_link.rsplit('/', 1)[-1].encode('utf-8').translate(str.maketrans('', '', '?'))
            self.downloadable = True
            self.resource_title = file_name
        else:
            self.resource_title = "No Name Provided"


    def get_folder_id(self):
        if self.moodle_resource:
            self.folder = regexs.identify_folder_id(self.resource_link)


class IlearnResource(InternalResource):

    def __init__(self, link):
        InternalResource.__init__(self, link)

    def __call__(self, *args, **kwargs):

        if self.downloadable:
            resource = rf.download_ilearn_resource(self.resource_link)
            if resource.status_code == 200:
                return {"resource": resource,
                        'title': self.resource_title,
                        'link': self.resource_link,
                        'resource-type': self.resource_type,
                        'file-type': self.file_type,
                        'folder': self.folder}
            else:
                return {"resource": self.resource_link, "code": self.resource_header.status_code}
        else:
            return {'resource': self.resource_link,
                    'title': self.resource_title,
                    'link': self.resource_link,
                    'resource-type': self.resource_type,
                    'file-type': self.file_type,
                    'folder': self.folder}
        pass

    def __str__(self):

        return str({'title': self.resource_title,
                    'link': self.resource_link,
                    'resource-type': self.resource_type,
                    'file-type': self.file_type})


def get_folder_links(link):
    folder_html = rf.get_ilearn_resource(link)
    folder_links = []
    folder_name = BeautifulSoup(folder_html, "lxml").find("h2")
    table_main = BeautifulSoup(folder_html, "lxml").find("div", {"role": "main"})

    for link in table_main.find_all('a', href=True):
        folder_links.append(link['href'])
    return folder_links

def filter_fist_level_iframe(page_html):
    first_level_iframe_src = []
    first_level_iframes = page_html.find_all("iframe")

    if first_level_iframes:
        for iframe in first_level_iframes:
            first_level_iframe_src.append(iframe['src'])
    return first_level_iframe_src

def get_links(page_html):
    links = []

    for link in page_html.find_all('a', href=True):
        links.append(link['href'])
    first_level_iframe_links = filter_fist_level_iframe(page_html)
    if first_level_iframe_links:
        for link in first_level_iframe_links:
            links.append(link)
    return links

def get_section_content(page_html):
    section_classes = []
    n = 0
    for section_content in page_html.findAll(id=re.compile("section-*\d")):
        section_id = "section-" + str(n)
        section_classes.append((section_content, section_id))
        n = n + 1
    return section_classes

def get_section_summary(section_html):
    try:
        section_summary = section_html.find("h3", {"class":"sectionname"}).string
    except AttributeError:
        section_summary = None
    return section_summary

def get_mod_resource_page_link(link):
    mod_url_page_html = rf.get_ilearn_resource(link)
    div_main = BeautifulSoup(mod_url_page_html, "lxml").find("div", {"role": "main"})

    secondary_link = div_main.find("a", href=True)
    if not secondary_link:  # look for iFrame if not 'a' tag
        iframe_tag = div_main.find("iframe")
        if iframe_tag:
            return iframe_tag['src']
        else:
            return None
    if secondary_link:
        return secondary_link['href']
    else:
        return None

def get_assign_resource_page_link(link):
    mod_url_page_html = rf.get_ilearn_resource(link)
    div_main = BeautifulSoup(mod_url_page_html, "lxml").find("div", {"id": "intro"})

    secondary_link = div_main.find("a", href=True)
    if not secondary_link:  # look for iFrame if not 'a' tag
        iframe_tag = div_main.find("iframe")
        if iframe_tag:
            return iframe_tag['src']
        else:
            return None
    if secondary_link:
        return secondary_link['href']
    else:
        return None

def get_header(link):
    if link is not None:
        header = rf.get_resources_header(link)

        if header.status_code is not "404":
            return header
        else:
            print("404")
            return None
    else:
        return None

def initial_resource_search(header, link):
    if header is not None:
        if header.status_code == 303 or header.status_code == 302 or header.status_code == 301:

            header_resource = header.headers['Location']
            link_type = regexs.identify_link(header_resource)
            return header_resource, header.status_code, link_type

        elif header.status_code == 200:
            link_type = regexs.identify_link(link)
            return link, header.status_code, link_type
    else:
        return None

def sort_main_body_links(section_links):
    resource_objects = []

    sorted_resources = master_link_sorter(section_links)

    for resource_link in sorted_resources:
        resource_objects.append(IlearnResource(resource_link))

    return resource_objects

def master_link_sorter(section_links):

    section_id = section_links[0]
    section_links = section_links[1]
    scrubbed_links = [x for x in section_links if not regexs.links_to_remove.match(x)]
    working_list = [x for x in scrubbed_links]
    raw_resource_links = []

    while len(working_list) > 0:
        for link in working_list:

            search = initial_resource_search(get_header(link), link)

            if search is not None:
                if search[2] == 'file':

                    working_list.remove(link)
                    raw_resource_links.append(search[0])
                elif search[2] == 'url':
                    working_list.remove(link)
                    new_link = get_mod_resource_page_link(search[0])
                    if new_link is not None:
                        working_list.append(new_link)
                elif search[2] == 'folder':
                    working_list.remove(link)
                    folder_links = get_folder_links(search[0])
                    if len(folder_links) > 0:
                        for link in folder_links:
                            if link is not None:
                                working_list.append(link)
                elif search[2] == 'assignment':
                    working_list.remove(link)
                    new_link = get_assign_resource_page_link(link)
                    if new_link is not None:
                        working_list.append(new_link)
                elif search[2] == 'resource':
                    working_list.remove(link)
                    working_list.append(search[0])
                else:
                    working_list.remove(link)
                    raw_resource_links.append(link)


    return raw_resource_links

