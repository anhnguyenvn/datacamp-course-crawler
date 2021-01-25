# import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.common.action_chains import ActionChains
import html2markdown
import nbformat as nbf

run_solution_xpath = '//*[@id="gl-editorTabs-solution/solution.py"]/div/div/div[2]/div[2]/button[3]'


def create_browser(driver_path):
    # create a selenium object that mimics the browser
    browser_options = Options()
    # headless tag created an invisible browser
    # browser_options.add_argument("--headless")
    browser_options.add_argument('--no-sandbox')
    chrome = webdriver.Chrome(driver_path, options=browser_options)
    chrome.maximize_window()
    print("Done Creating Browser")
    return chrome


def handle_video(url_path, title, order):
    print('..Handling video lecture')
    video_node = f'<div class="alert alert-block alert-info">\n\n#### {order}. {title} (Video Lecture)\n</div>\n\n'
    video_node += f'({url_path})'
    video_iframe = f"IFrame('{url_path})', width=900, height=650)"
    return [('markdown', video_node), ('code', video_iframe)]


def handle_exercise(url_path, title, browser, order):
    print('..Handling exercise')

    button_there, btn_hint = element_exist(exercise_xpath)

    if button_there:
        btn_hint.send_keys(Keys.LEFT_CONTROL, 'h')
        # print('sent first CTR + H')

    # actions = ActionChains(browser)
    # actions.send_keys(Keys.LEFT_CONTROL, 'h')
    # actions.perform()

    # browser.find_element_by_name("Value").send_keys(Keys.LEFT_CONTROL, 'h')

    # browser.find_element_by_name("Value").send_keys(Keys.LEFT_CONTROL, 'h')
    # actions.send_keys(Keys.LEFT_CONTROL, 'h')
    # actions.perform()

    # wait for the button run solution appear
    element_exist('//*[@id="gl-editorTabs-files/script.py"]/div/div/div[2]/div[2]/button[1]')

    exercise_node = f'<div class="alert alert-block alert-warning">\n\n#### {order}. {title} (Exercise)\n</div>\n\n'
    exercise_node += f'({url_path})'

    soup = BeautifulSoup(browser.page_source, 'html.parser')

    intro = soup.find_all("div", class_='exercise--assignment exercise--typography')[0]
    intro_text = html2markdown.convert(str(intro)).replace('<h1 class=', '<h4 class=').replace('</h1>', '</h4>')

    instruction = soup.find_all('div', class_='exercise--instructions__content')[0]
    instruct_text = html2markdown.convert(str(instruction))

    hint = soup.find_all('div', class_='dc-sct-feedback__campus-content')[0]
    hint_text = html2markdown.convert(str(hint))
    # print(intro_text, instruct_text, hint_text)

    guide_src = soup.find_all('div', {'class': 'view-lines', 'role': 'presentation'})
    # for guide in guide_src:
    #     # print(guide)
    code_line = guide_src[0].find_all('span', class_='')
    src_text = ''
    for i, line in enumerate(code_line):
        # print('sr', line.text)
        # encoded_string = line.text.encode("ascii", "ignore")
        # decode_string = encoded_string.decode()
        src_text += line.text.replace(u"\u00A0", ' ') + '\n'
    # print(src_text)

    btn_hint.send_keys(Keys.LEFT_CONTROL, 'h')
    # print('sent 2nd CTR + H')

    # wait for the button run solution appear
    element_exist('//*[@id="gl-editorTabs-solution/solution.py"]/div/div/div[2]/div[2]/button[3]')

    soup = BeautifulSoup(browser.page_source, 'html.parser')  # reread the source page
    source = soup.find_all('div', {'class': 'view-lines', 'role': 'presentation'})[1]

    solution_text = ''
    code_line = source.find_all('span', class_='')
    for i, line in enumerate(code_line):
        # encoded_string = line.text.encode("ascii", "ignore")
        # decode_string = encoded_string.decode()
        solution_text += line.text.replace(u"\u00A0", ' ') + '\n'
    # print(solution_text)

    # print(len(source))
    # for s in source:
    #     source_text = s.text
    #     print(source_text)
    return [('markdown', exercise_node),
            ('markdown', intro_text),
            ('markdown', instruct_text),
            ('markdown', hint_text),
            ('markdown', '<div class="alert alert-block alert-success">\n\n##### Change block to code-block to '
                         'practice\n</div>'),
            ('raw', src_text),
            ('markdown', '<div class="alert alert-block alert-danger">\n\n##### Solution here\n</div>'),
            ('code', solution_text)]


def handle_quiz(url_path, title, order):
    print('..Handling quiz')
    quiz_node = f'<div class="alert alert-block alert-info">\n\n#### {order}. {title} (Quiz)\n</div>\n\n'
    quiz_node += f'({url_path})'
    quiz_iframe = f"IFrame('{url_path})', width=900, height=650)"
    return [('markdown', quiz_node), ('code', quiz_iframe)]


def handle_exercise_quiz():
    print('Handling exercise quiz')
    return None


def element_exist(xpath, timeout=1):
    try:
        element = WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        return True, element
    except TimeoutException:
        return False, None


def create_node(nb_node, nb_text):
    if nb_node == 'markdown':
        return nbf.v4.new_markdown_cell(nb_text)
    elif nb_node == 'raw':
        return nbf.v4.new_raw_cell(nb_text)
    else:
        return nbf.v4.new_code_cell(nb_text)



video_xpath = '//*[@id="root"]/div/main/div[1]/section/div[2]/button[2]'
# Take hint button
# exercise_xpath = "//*[@id=\"gl-aside\"]/div/aside/div/div/div/div[2]/div[2]/div/div/div/div[2]/section/nav/button"
exercise_xpath = "//div[@id='gl-aside']/div/aside/div/div/div/div[2]/div[2]/div/div/div/div[2]/section/nav/button"
# Take hint button
quiz_xpath = '//*[@id="root"]/div/main/div[1]/section/div/div[5]/div/section/nav/button'
script_py_xpath = '//*[@id="rendered-view"]/div/div/div[3]/div[1]/div'

####
# CHANGE YOUR COURSE DATA, OUTPUT PATH HERE
####

# download chrome driver from google, version should match the installed Chrome
driver_path = 'D:/Chrome/chromedriver.exe'
output_path = 'D:/DataCamp/CaseStudyInStatisticalThinking2/'

base_url = 'https://campus.datacamp.com/courses/'
course_url = 'case-studies-in-statistical-thinking'
# (chaper title, chapter total section)
chapter_urls = [('fish-sleep-and-bacteria-growth-a-review-of-statistical-thinking-i-and-ii', 11),
                ('analysis-of-results-of-the-2015-fina-world-swimming-championships', 13),
                ('the-current-controversy-of-the-2013-world-championships', 13),
                ('statistical-seismology-and-the-parkfield-region', 12),
                ('earthquakes-and-oil-mining-in-oklahoma', 12)]

chapter_count = 0
for chapter, number_lesson in chapter_urls:
    chapter_count += 1

    lesson_range = range(1, number_lesson + 1)
    all_url = [base_url + course_url + '/' + chapter + '?ex=' + str(i) for i in lesson_range]

    main_title = chapter + '-crawled'
    # print(main_title)

    import_code = 'import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nfrom IPython.display import IFrame'
    nodes = [('markdown', '## Self-prepare Data for exercise'), ('code', import_code)]

    is_first = False
    count_lecture = 0
    btn_next = None

    for url in all_url:
        count_lecture += 1
        # Create a browser and navigate to the url
        if not is_first:
            browser = create_browser(driver_path)
            browser.get(url)
            is_first = True
        else:
            if btn_next is None:
                is_next, btn_next = element_exist('//*[@id="root"]/div/header/div/nav/a')
                if is_next:
                    btn_next.send_keys(Keys.LEFT_CONTROL, 'k')
            else:
                btn_next.send_keys(Keys.LEFT_CONTROL, 'k')
            browser.implicitly_wait(3)

        print(f"Done navigating {browser.title}")
        title = browser.title.replace('| Python', '')

        # check exercise first due to its majority
        hasHintBtnInExercise, hint_button = element_exist(exercise_xpath, timeout=7)
        if hasHintBtnInExercise:
            has_script_py_view, _ = element_exist(script_py_xpath)
            if has_script_py_view:
                nodes.extend(handle_exercise(url, title, browser, count_lecture))
            else:
                print('Ignore quiz in exercise view')
                nodes.append(('markdown', f'Unrecognized {url}'))
                nodes.append(('code', f"IFrame('{url})', width=900, height=650)"))
        else:
            is_video, _ = element_exist(video_xpath, timeout=1)
            if is_video:
                nodes.extend(handle_video(url, title, count_lecture))
            else:
                is_quiz, _ = element_exist(quiz_xpath)
                if is_quiz:
                    nodes.extend(handle_quiz(url, title, count_lecture))
                else:
                    print('Cannot recognize Datacamp type')
                    nodes.append(('markdown', f'Unrecognized {url}'))
                    nodes.append(('code', f"IFrame('{url})', width=900, height=650)"))
        if count_lecture == number_lesson:
            browser.close()

    nb = nbf.v4.new_notebook()
    nb['cells'] = [create_node(nb_node, nb_text) for nb_node, nb_text in nodes]
    nbf.write(nb, output_path + f'{chapter_count} {main_title}.ipynb')
