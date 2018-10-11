import re, traceback
import regexs
import request_functions as rf
import database as db
from bs4 import BeautifulSoup
import os, yaml
import mimetypes

##! need workaround for servers not configured to return HEAD requests
##! section number on folders doesn't match actual section numbers.
##! mod URL pages need to be able to search for more than on link

link_buffer_list = []

class InternalResource:

    def __init__(self, link, header, title, hidden):
        self.resource_link = link
        self.file_type = None
        self.resource_type = regexs.identify_resource_type(self.resource_link)
        self.resource_header = header
        self.resource_title = title
        self.downloadable = False
        self.file_extension = None
        self.service_type = regexs.identify_service_type(self.resource_link)
        self.moodle_resource = regexs.identify_if_moodle(self.resource_link)
        self.folder = None
        self.hidden = hidden
        self.initialize_resource()

    def initialize_resource(self):
        self.clean_resource_title()
        self.get_folder_id()
        self.id_file_extension()
        self.get_file_type_from_link()


    def id_file_extension(self):
        if 'Content-Type' in self.resource_header.headers:
            self.file_extension = mimetypes.guess_extension(
                self.resource_header.headers['Content-Type'].split()[0].rstrip(";"))

    def clean_resource_title(self):
        print(self.resource_link, self.resource_title)

        if 'Content-Disposition' in self.resource_header.headers:
            gross_title = self.resource_header.headers['Content-Disposition']
            actual_title = gross_title[22:-1].translate(str.maketrans('', '', '?'))

            if self.resource_title is None:
                self.resource_title = actual_title
            self.downloadable = True ##! this doesn't seem like a good test for downloadable content

            if self.resource_type == 'Other': # in case file name is missing extension
                self.resource_type = 'file'


        elif self.moodle_resource:
            print("moodle resource", self.resource_title)
            file_name = self.resource_link.rsplit('/', 1)[-1].encode('utf-8').translate(str.maketrans('', '', '?'))
            self.downloadable = True

            if self.resource_title is None:
                self.resource_title = file_name

            if self.resource_type == 'Other': # in case file name is missing extension
                self.resource_type = 'file'
        else:
            pass ##! not sure what is going on here

    def get_file_type_from_link(self):

        if self.resource_type == 'file':
            if self.file_extension is not None:
                self.file_type = self.file_extension
                self.resource_title = '{}{}'.format(self.resource_title, self.file_type)

    def get_folder_id(self):
        if self.moodle_resource:
            self.folder = regexs.identify_folder_id(self.resource_link)


class IlearnResource(InternalResource):

    def __init__(self, link, header, title, hidden):
        InternalResource.__init__(self, link, header, title, hidden)

    def __call__(self, *args, **kwargs):

        if self.downloadable:
            resource = rf.download_ilearn_resource(self.resource_link)
            if resource.status_code == 200:
                return {"resource": resource,
                        'title': self.resource_title,
                        'link': self.resource_link,
                        'resource-type': self.resource_type,
                        'file-type': self.file_type,
                        'folder': self.folder,
                        'extension': self.file_extension,
                        'service_type': self.service_type,
                        'hidden': self.hidden}
            else:
                return {"resource": self.resource_link, "code": self.resource_header.status_code}
        else:
            return {'resource': self.resource_link,
                    'title': self.resource_title,
                    'link': self.resource_link,
                    'resource-type': self.resource_type,
                    'file-type': self.file_type,
                    'folder': self.folder,
                    'extension': self.file_extension,
                    'service_type': self.service_type,
                    'hidden': self.hidden}
        pass

    def __str__(self):

        return str({'title': self.resource_title,
                    'link': self.resource_link,
                    'resource-type': self.resource_type,
                    'file-type': self.file_type})


def load_config():
    __path__ = os.path.join(os.path.dirname(__file__), "config.yaml").replace('/','//')
    with open(__path__, 'r') as config:
        try:
            return yaml.load(config)
        except:
            print("Error loading config file")
            return None


def get_folder_links(link):
    folder_html = rf.get_ilearn_resource(link)
    folder_links = []
    folder_name = BeautifulSoup(folder_html, "lxml").find("h2")
    table_main = BeautifulSoup(folder_html, "lxml").find("div", {"role": "main"})

    for link in table_main.find_all('a'):

        try:
            link_url = link['href']
        except KeyError:
            link_url = None

        try:
            link_span = link.select_one("span[class*='fp-filename']").text
            link_text = link_span.next_element
            print(link, link_text)
        except AttributeError:
            link_text = None

        folder_links.append((link_url, link_text))

    return folder_links


def filter_first_level_iframe(page_html):
    first_level_iframe_src = []
    first_level_iframes = page_html.find_all("iframe")

    if first_level_iframes:
        for iframe in first_level_iframes:
            first_level_iframe_src.append(iframe['src'])
    return first_level_iframe_src


def get_section_links(section_html):
    links = []


    for bs4tag in section_html.find_all('a'):

        first_level_iframe_links = filter_first_level_iframe(section_html)
        if first_level_iframe_links:
            for bs4tag in first_level_iframe_links:
                links.append((bs4tag, None, None))

        content_dimmed = None
        try:
            link_span = bs4tag.attrs  # is resource hidden from students
            if 'class' in link_span:
                if 'dimmed' in link_span['class']:
                    content_dimmed = True
                else:
                    content_dimmed = False

        except AttributeError:
            content_dimmed = False
            pass


        try:
            link_url = bs4tag['href']
        except KeyError:
            link_url = None
        except TypeError:
            link_url = bs4tag

        try:
            link_span = bs4tag.select_one("span[class*='instancename']")
            link_text = link_span.next_element
        except AttributeError:
            link_text = None

        if link_url is not None:
            link_name_tuple = link_url, link_text, content_dimmed
            links.append(link_name_tuple)
    print(links)
    return links


def get_section_content(page_html):
    section_classes = []
    n = 0

    for section_content in page_html.findAll(id=re.compile("section-*\d")):
        section_id = "Section-" + str(n)
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



    if div_main is not None:


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


    else:  # if div main doesn't exist, check of content is in a frame, get the frame src.
        div_frame = BeautifulSoup(mod_url_page_html, "lxml").find_all("frame")

        if div_main is not None:
            div_main = div_frame[1]
            secondary_link = div_main['src']

            return secondary_link
        else:
            return None


def get_iframe_video(link):
    iframe_video_resource = rf.get_ilearn_page(link)
    presidio_container = BeautifulSoup(iframe_video_resource, 'lxml').find("div", {"class": "presidio-container"})


def get_assign_resource_page_link(link):
    mod_url_page_html = rf.get_ilearn_resource(link)
    div_main = BeautifulSoup(mod_url_page_html, "lxml").find("div", {"id": "intro"})
    if div_main is not None:
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
    else:
        return None


def get_header(link):
    allowed_codes = [200, 300, 301, 302, 303]
    if link is not None:
        have_visited_link = db.check_or_commit_link_visit(link)

        if have_visited_link:
            return have_visited_link  # returns old header


        header = rf.get_resources_header(link)


        if header is not None:
            db.check_or_commit_link_visit(link, header)
            if header.status_code in allowed_codes:

                return header
            else:
                return None
        else:
            return None
    else:
        return None


def construct_ereserves_request_link(ereserves_button_div):
    inputs = ereserves_button_div.find_all("input")
    q_param1 = inputs[0]['name'] + '=' + inputs[0]['value'].replace(' ', '+')
    q_param2 = inputs[1]['name'] + '=' + inputs[1]['value']
    ereserves_page = load_config()['ereserves_base_url'] + '?' + q_param1 + '&' + q_param2
    return ereserves_page


def link_buffer(link):

    """

    :param link:
    :return:

    Keeps a persistent buffer of the last 2 links to check if the header check is stuck in a loop.
    This seems to happen when sites return alternating but identical links in the 'location' header.
    if the current link matches the link 2 searches prior, it returns true and the resource search
    defaults to 200ok.

    """

    link_buffer_list.append(link)

    if len(link_buffer_list) == 3:
        if link == link_buffer_list[0]:
            if len(link_buffer_list) > 2:
                link_buffer_list.pop(0)
            return True
        else:

            if len(link_buffer_list) > 2:
                link_buffer_list.pop(0)
            return False


def initial_resource_search(header, link):
    if header is not None:
        if header.status_code == 303 or header.status_code == 302 or header.status_code == 301:

            header_resource = header.headers['Location']


            if link_buffer(header_resource):
                if regexs.check_valid_url(header_resource):
                    link_type = regexs.identify_link(link)
                    return link, 200, link_type
                else:
                    return None


            bad_characters = ['#', '/']
            if header_resource[-1] in bad_characters: # some sites return the same link in the Location area. This causes an infinite loop
                if header_resource[:-1] == link:
                    if regexs.check_valid_url(header_resource):
                        link_type = regexs.identify_link(link)
                        return link, 200, link_type
                    else:
                        return None

            if regexs.check_valid_url(header_resource):
                link_type = regexs.identify_link(header_resource)
                return header_resource, header.status_code, link_type
            else:
                return None ##! log this

        elif header.status_code == 200:
            link_type = regexs.identify_link(link)
            return link, header.status_code, link_type
    else:
        print("header returned as none", header, link)
        return None


def sort_for_content_links(section_links):
    resource_objects = []
    sorted_resources = master_link_sorter(section_links)

    for resource in sorted_resources:
        resource_url = resource[0]
        resource_title = resource[1]
        resource_hidden = resource[2]

        resources_header = rf.get_resources_header(resource_url)

        if resources_header is not None:

            new_ilearn_resource = IlearnResource(resource_url, resources_header, resource_title, resource_hidden)

            resource_objects.append(new_ilearn_resource)
        else:
            print("Error getting resources header before creating resource class")
            continue

    return resource_objects


def master_link_sorter(section_links):

    section_links = section_links[1]

    scrubbed_links = [(url, title, hidden) for url, title, hidden in section_links if not regexs.scrub_links(url)]

    working_list = [x for x in scrubbed_links]

    raw_resource_links = []

    while len(working_list) > 0:

        for resource in working_list:

            resource_url = resource[0]  # url
            resource_title = resource[1]  # title
            resource_hidden = resource[2]  # hidden state

            if resource_url is not None and regexs.do_not_head(resource_url) and regexs.scrub_links(resource_url) is not None: # removes troublesome links that we know we still want

                working_list.remove(resource)
                # raw_resource_links.append(resouce) ##! find a way to store these links elsewhere
                continue

            if regexs.check_valid_url(resource_url):

                search = initial_resource_search(get_header(resource_url), resource_url)

                if search is not None:

                    if search[2] == 'file':
                        working_list.remove(resource)
                        raw_resource_links.append( (search[0], resource_title, resource_hidden) )

                    elif search[2] == 'url':
                        working_list.remove(resource)
                        new_link = get_mod_resource_page_link(search[0])
                        if new_link is not None:

                            working_list.append( (new_link, resource_title, resource_hidden) )

                    ##! Folder link search must return tuple with link span names
                    elif search[2] == 'folder':

                        working_list.remove(resource)
                        folder_links = get_folder_links(search[0])

                        if len(folder_links) > 0:

                            for resource in folder_links:
                                folder_resource_url = resource[0]
                                folder_resource_title = resource[1]

                                if resource is not None:
                                    working_list.append((folder_resource_url, folder_resource_title, resource_hidden))

                    elif search[2] == 'assignment':
                        working_list.remove(resource)
                        new_link = get_assign_resource_page_link(resource_url)
                        if new_link is not None:
                            working_list.append( (new_link, resource_title, resource_hidden))

                    elif search[2] == 'resource':
                        if search[1] == 200:
                            new_link = get_mod_resource_page_link(search[0])
                            working_list.remove(resource)
                            working_list.append( (new_link, resource_title, resource_hidden))
                        else:
                            working_list.remove(resource)
                            working_list.append( (search[0], resource_title, resource_hidden))

                    elif search[2] == 'page':
                        ##! make sure page search works
                        working_list.remove(resource)


                    elif search[1] in [301, 302, 303]:
                        working_list.remove(resource)
                        working_list.append( (search[0], resource_title, resource_hidden) )


                    elif search[2] is None:
                        working_list.remove(resource)
                        raw_resource_links.append( (search[0], resource_title, resource_hidden) )
                else:
                    ##! need better way to short bad headers
                    working_list.remove(resource)
            else:
                working_list.remove(resource) # removes invalid URLs
    return raw_resource_links

