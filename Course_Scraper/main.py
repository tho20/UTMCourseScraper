from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import json

# Web scraper: Gets all the courses info from the current academic calendar and
# organizes them into a dictionary with the program as key and a list of all
# the courses for that program. Converts this dictionary into a json file so
# that it can be easily exported.


class Course:
    # No courses for Professional Writing and Environmental Geoscience

    """
    Class Course: has a course code, title and description.

    """
    course_code: str
    course_title: str
    course_description: str  # Contains Exclusions and Prerequisites

    def __init__(self, course_code, course_title, course_description):

        """
        Initialize a course with given parameters.

        :param course_code: course code
        :param course_title: course title
        :param course_description: course description
        """

        self.course_code = course_code
        self.course_title = course_title
        self.course_description = course_description


def get_programs_and_urls_from_files() -> (list, list):

    """
    Gets links and programs from courses_per_program_link.txt and
    programs_list.txt respectively and returns them in two separate lists.

    :return: lists of strings
    """

    all_programs = []
    all_links = []

    with open("programs_list.txt", mode='r') as programs_file:
        for i in range(43):
            all_programs.append(programs_file.readline().strip("\n"))
    programs_file.close()

    with open("courses_per_program_link.txt", mode='r') as links_file:
        for i in range(43):
            all_links.append(links_file.readline().strip("\n"))
    links_file.close()

    return all_links, all_programs


def get_data_from_one_program(my_url: str) -> list:

    """
    Scrapes the courses from the given url for specific program. Returns list
    of all the courses for that url.

    :param my_url: url with the list of all  the courses to be scraped.
    :return: List of Courses
    """

    courses_for_program = []

    uClient = uReq(my_url)  # Opening connection and grabbing the page
    html_page = uClient.read()  # contents of page
    uClient.close()
    page_soup = soup(html_page, "html.parser")

    course_codes_and_titles = page_soup.findAll('p', {'class': 'titlestyle'})
    # Scrapes the courses codes and titles
    courses_description = page_soup.findAll('span', {'class': 'normaltext'})
    # Scrapes the courses descriptions

    for i in range(len(course_codes_and_titles)):

        course_code = course_codes_and_titles[i].text[:8]
        course_title = course_codes_and_titles[i].text[9:]
        course_description = courses_description[i].text.strip("\n")

        course = Course(course_code, course_title, course_description)
        courses_for_program.append(course)

    return courses_for_program


def get_all_data(urls: list, all_programs: list) -> dict:

    """
    Gets all the data needed by calling get_data_from_one_program for all the
    programs. Organizes the data into a dictionary with the programs as keys
    and list of all the courses of that program as values.

    :param urls: list of all the urls
    :param all_programs: list of all the programs
    :return: Dictionary
    """

    courses_per_program_dic = {}
    for i in range(43):  # 43 programs
        courses_from_one_program = get_data_from_one_program(urls[i])
        courses_per_program_dic[all_programs[i]] = courses_from_one_program

    return courses_per_program_dic


def convert_into_writable_json(dic: dict) -> dict:

    """
    Converts dictionary of Course objects into strings so that it can be written
    into json.

    Dic[Program] = [Courses] -> Dic[Program] = {"courseCode" : code,
                                                "courseTitle : title,
                                                "courseDescription":description}
    :param dic:
    :return: Dictionary
    """

    new_dict = {}
    for program in dic:
        course_lst = []
        for course in dic[program]:
            course_dic = {}
            code, title, description = course.course_code, course.course_title,\
                                    course.course_description

            course_dic["courseCode"] = code
            course_dic["courseTitle"] = title
            course_dic["courseDescription"] = description
            course_lst.append(course_dic)

        new_dict[program] = course_lst

    return new_dict


def put_data_in_json(data: dict):

    """
    Writes data into json.

    :param data: dictionary
    """

    j = json.dumps(data)
    with open("courses.json", mode="w") as json_file:
        json_file.write(j)
    json_file.close()


if __name__ == "__main__":  # Runs Program

    urls_and_programs = get_programs_and_urls_from_files()
    all_urls, all_program = urls_and_programs

    dic_with_all_data = get_all_data(all_urls, all_program)
    formatted_dict = convert_into_writable_json(dic_with_all_data)

    put_data_in_json(formatted_dict)
