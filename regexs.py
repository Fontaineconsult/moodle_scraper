import re
##! /mod/resource can also be a direct link. Need to inspect reponse headers before directing // 303 see other


first_level_group = "((.*.pdf|.*.docx|.*.ppt)|" \
              "(resource/view.php\?id=[0-9]{0,7}))" \


url_links_group = "((url/view.php\?id=[0-9]{0,7})|" \
            "(page/view.php\?id=[0-9]{0,7})|" \
            "(assign/view.php\?id=[0-9]{0,7}))"

folders_group = "((resource/view.php\?id=[0-9]{0,7})" \
          "(folder/view.php\?id=[0-9]{0,7}))"


# direct download links on main iLearn page. mod resource can be folder
first_level_resource_links = re.compile(r"(https://ay1718.ilearn.support.at.sfsu.edu/mod/)" + first_level_group)

# links to another page with a download link
first_level_url_links = re.compile(r"(https://ay1718.ilearn.support.at.sfsu.edu/mod/)" + url_links_group)

direct_external_links = re.compile("https://www.youtube.com/watch\?v=.{11}|"
                                   "https://www.dailymotion.com/video/.{7}")


#links to folders with multiple downloads.

folder_links = re.compile(r"(https://ay1718.ilearn.support.at.sfsu.edu/mod/)" + folders_group)



links_to_remove = re.compile("(https://ay1718.ilearn.support.at.sfsu.edu/mod/)("
                             "(turnitintooltwo/.+)|"
                             "(attendance/.+)|"
                             "(forum/.+)|"
                             "(quiz/.+))|"
                             "(zoom/:.+)|"
                             "(mailto:.+)|"
                             "(https://email.sfsu.edu/owa/.+)|"
                             "(https://ay1718.ilearn.support.at.sfsu.edu/course/view.php\?id=\d{0,7}#section-\d+)|"
                             "(https://ay1718.ilearn.support.at.sfsu.edu/course/view.php?id=[0-9]{0,7})|"
                             "(\A#{1}.+)")


# e_reserve_link = re.compile()



moodle_content_id_regex = "https://ay1718.ilearn.support.at.sfsu.edu/mod/(((url|presidioresource|mediasite)|(page)|(assign)|(folder)|(resource))/view.php\?id=[0-9]{0,7})|(.*\.pdf|.*\.docx|.*\.ppt|.*\.doc|.*\.pptx|.*\.jpg|.*\.rtf|.*\.m4a|.*\.pages|.*\.rar|.*\.xlsx|.*\.zip)|(https://diva.sfsu.edu/bundles/[0-9]{5,8}/download)|"

first_level_mediasite_links = re.compile("https://ay1718.ilearn.support.at.sfsu.edu/mod/mediasite/view.php\?id=.+")


url_id = re.compile("[0-9]{5,7}")

resource_type = re.compile("(.*..*.youtu[\.]?be.*..*.|.*.vimeo.*.|.*.mediasite.*.|.*.dailymotion.*.|.*.presidio.*.)|(.*\.pdf|.*\.docx|.*\.ppt|.*\.doc|.*\.pptx|.*\.jpg|.*\.rtf|.*\.m4a|.*\.pages|.*\.rar|.*\.xlsx|.*\.zip)", re.IGNORECASE)


is_moodle_file = re.compile(".*.mod_resource|.*.mod_folder", re.IGNORECASE)

get_folder_id = re.compile("[0-9]{5,6}/mod_folder/")

basic_url_check = re.compile("http.*.|https.*.")

excepted_from_head_check = re.compile("https://presidio.at.sfsu.edu/media/.*.")



def do_not_head(link):
    try:
        if excepted_from_head_check.match(link):
            return True
        else:
            return False
    except TypeError:
        return False

def check_valid_url(link):

    try:
        if basic_url_check.match(link):
            return True
        else:
            return False
    except TypeError:
        return False


def identify_resource_type(link):

    group = resource_type.match(link)

    if group:
        if group.group(1):
            return "video"
        if group.group(2):
            return "file"
    else:
        return "Other"

def identify_link_id(link):
    try:
        url_id_num = url_id.search(link)
        return url_id_num.group(0)
    except:
        return None

def identify_if_moodle(link):
    if is_moodle_file.match(link):
        return True
    else:
        return False

def identify_link(link):
    group_regex = re.compile(moodle_content_id_regex, re.IGNORECASE)
    group = group_regex.match(link)
    if group:

        if group.group(3):
            return "url"
        if group.group(4):
            return "page"
        if group.group(5):
            return "assignment"
        if group.group(6):
            return "folder"
        if group.group(7):
            return "resource"
        if group.group(8):
            return "file"
        if group.group(9): # ereserve file link
            return "file"

    else:
        return None


def identify_folder_id(link):
    match = get_folder_id.search(link)
    if match:
        return match.group(0).split("/", 1)[0]
    else:
        return None
