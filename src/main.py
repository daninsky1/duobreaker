from selenium import webdriver, common
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import pickle
import time
import logging
import pathlib
from database import Database

# Notification obj
toaster = ToastNotifier()

# Constants
DUOLINGO = 'https://duolingo.com'

# time.sleep compress
wait = time.sleep

# Web driver object 'Firefox' or 'Chrome'
driver = 'Firefox'
if driver == 'Chrome':
    chrome_options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_setting_values.notifications': 2}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options)
elif driver == 'Firefox':
    driver = webdriver.Firefox()


def log_init():
    """Setup the logger file"""
    log_path = pathlib.Path.cwd() / 'log'
    log_path.mkdir(exist_ok=True)

    LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'
    logging.basicConfig(filename=log_path / 'log.log',
                        level=logging.DEBUG,
                        format=LOG_FORMAT,
                        filemode='w')
    global logger
    logger = logging.getLogger()
    logger.info('Starting...')


log_init()


class Cookie():
    """Creates, loads and manipulate cookie"""

    def __init__(self, driver, url):
        ck_folder = pathlib.Path.cwd() / 'cookie'
        ck_folder.mkdir(exist_ok=True)
        self.COOKIE_PATH = ck_folder / 'cookie.txt'

        self.driver = driver
        self.url = url

    def save_cookie(self):
        pickle.dump(self.driver.get_cookies(), open(self.COOKIE_PATH, 'wb'))
        logger.info('Cookie saved.')

    def load_cookie(self):
        cookies = pickle.load(open(self.COOKIE_PATH, 'rb'))
        self.driver.delete_all_cookies()
        # Have to be on a page before you can add any cookie, any page - does not metter which
        self.driver.get(self.url)
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        logger.info('Cookie loaded.')

    def delete_cookie(self):
        self.driver.delete_all_cookies()
        with open(self.COOKIE_PATH, 'wb') as file:
            file.write(b'')
        logger.info('Cookie deleted.')

    def update_cookie(self):
        """It's broken"""
        self.delete_cookie()
        self.save_cookie()
        logger.info('Cookie updated.')


def initializate(cookie):
    '''Start the driver and navigate to the games window'''

    # Mainpage
    driver.get(DUOLINGO)

    # Load cookie or login and save cookie
    try:
        cookie.load_cookie()
    except FileNotFoundError:
        # login
        have_acc_button = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, '//a[@data-test="have-account"]'))
        )
        have_acc_button.click()

        print('''Faça login que vai para a página dos desafios:
'https://www.duolingo.com/learn'.
Caso seja o seu primeiro login no duolingo será necessário configurar sua conta,
assim que chegar na página acima aperte qualquer tecla no prompt''')

        input()

        if driver.current_url == 'https://www.duolingo.com/learn':
            print('Pronto!')
            wait(2)  # Wait to get more time to cookie load into the browser
            cookie.save_cookie()  # save_cookie/login
        else:
            print('Tu não estás em: "https://www.duolingo.com/learn"\nAbortar...')
            input('Aperte qualquer botão para sair')
            driver.quit()

    else:
        driver.get(DUOLINGO)

        if driver.current_url == 'https://www.duolingo.com/learn':
            print('Pronto!')
        else:
            print('''Falha ao carregar login.
Exclua cookie.txt em cookie e reinicie o script.''')
            input('Aperte qualquer botão para sair')
            driver.quit()

    logger.info('init Duo Breaker: Done!')

# Aux functions to the games and A.I.

def next_button(next_button_path='//div[@class="_1cw2r"]',
                timeout=2,
                wait_until='clickable'):
    """
    Find next button element: verificar, continuar, próximo, etc.
    wait_until:
    defaul - 'clickable'
    1 - 'presence'
    2 - 'visibility'
    """

    logger.info('next_button called.')

    if wait_until == 'clickable':
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, next_button_path))
        )
    elif wait_until == 'presence':
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, next_button_path))
        )
    elif wait_until == 'visibility':
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, next_button_path))
        )
    else:
        pass


def check_keyboard():
    """Some games need the keyboard to be turned on for the script can write the answer"""
    logger.info('check_keyboard called.')
    try:
        driver.find_element_by_xpath('//div[@class="_20M9T _25h83"]')
    # print('teste teclado')
    except common.exceptions.NoSuchElementException:
        keyboard_toggle = True
    # print('o uso do teclado já esta ligado')
    else:
        driver.find_element_by_xpath('//div[@class="_2j1n8"]').click()
        keyboard_toggle = True

# print('o uso do teclado foi ligado')

# Functions that play various duo games

# Right solution element xpath
r_solut_text_xpath = '//h2[text()="Solução correta:"]'

# Right solution element text
right_solution = lambda: driver.find_element_by_xpath('//div[starts-with(@class, "_75iiA")]').text


def play_card_choice(header, card_choice_database):
    '''Selecionar a carta correspondente em inglês'''
    logger.info('play_card_choice called.')

    if not isinstance(card_choice_database, Database):
        raise EOFError('TypeError. It\'s not a Database object.')

    print('[Card Choice]\n%s\n' % header)
    to_transl = header[23:-2]

    translation = card_choice_database.get_translation(to_transl, False)

    if translation != None:
        print('Resposta:\n\"%s\"' % translation)
        correct_card = driver.find_element_by_xpath(
            '//span[text()="%s"]//ancestor::label[@data-test="challenge-choice-card"]' % translation
        ).click()
        next_button().click()
    else:
        # clicks on the first choice and press verify
        wait(1)
        first_choice = '//label[@data-test="challenge-choice-card"][1]'
        driver.find_element_by_xpath(first_choice).click()
        next_button().click()
        wait(1)
        try:
            # Try to find the right solution answer element
            driver.find_element_by_xpath(r_solut_text_xpath)
        except common.exceptions.NoSuchElementException:
            # ripe the answer from the right answer from the box
            choice_answer = driver.find_element_by_xpath(first_choice).text[:-2]
            print('Acertei sem querer:\n%s' % choice_answer)

            card_choice_database.add_translation(choice_answer, to_transl)
        else:
            # ripe the answer from the right solution header
            print('Errei, a resposta é:\n%s' % right_solution())

            card_choice_database.add_translation(right_solution(), to_transl)
    logger.info('play_card_choice end.')


def play_phrase_choice(header, phrase_choice_database):
    '''Jogo de multipla escolha pede que você marque a tradução do português para
    o inglês'''
    logger.info('play_phrase_choice called.')

    if not isinstance(phrase_choice_database, Database):
        raise EOFError('TypeError. It\'s not a Database object.')

    print('[Phrase Choise]\n%s\n' % header)
    # block to convert the hint box into a string, because he comes separeted
    to_transl = driver.find_element_by_xpath('//div[@class="KRKEd _3xka6"]').text

    translation = phrase_choice_database.get_translation(to_transl, False)
    if translation != None:
        print('Resposta:\n\"%s\"\n' % translation)
        correct_choice = driver.find_element_by_xpath(
            '//div[@data-test="challenge-judge-text" and text()="%s"]' % translation
        ).click()
        next_button().click()
    else:
        # clicks on the first choice and press verify
        first_choice = '//label[@data-test="challenge-choice"][1]'
        wait(.500)
        driver.find_element_by_xpath(first_choice).click()
        next_button().click()
        try:
            # Try to find the right solution answer element
            wait(1)
            right_solution()
        except common.exceptions.NoSuchElementException:
            # ripe the answer from the right answer from the box
            choice_answer_raw = driver.find_element_by_xpath(first_choice).text
            choice_answer = choice_answer_raw[2:]
            print('Acertei sem querer:\n%s' % choice_answer)

            phrase_choice_database.add_translation(choice_answer, to_transl)
        else:
            # ripe the answer from the right solution header
            print('Errei, a resposta é:\n%s\n' % right_solution())

            phrase_choice_database.add_translation(right_solution(), to_transl)
    logger.info('play_phrase_choice end.')


def play_phrase_transl(header, phrase_transl_database):
    '''Resolves the translation games'''
    logger.info('play_phrase_transl called.')

    if not isinstance(phrase_transl_database, Database):
        raise EOFError('TypeError. It\'s not a Database object.')

    check_keyboard()
    print('[Phrase Translation]')
    text_area = driver.find_element_by_xpath(
        '//textarea[@data-test="challenge-translate-input"]')

    # Phrase to translate, it's the text of the hint box
    to_transl = driver.find_element_by_xpath('//span[@data-test="hint-sentence"]').text

    # se é português ele roda uma pesquisa no banco de dados de frases em português'''
    if header == 'Escreva em português':
        translation = phrase_transl_database.get_translation(to_transl, True)
        print(header, '\n')
        if translation != None:
            print('Resposta:\n\"%s\"' % translation)
            text_area.send_keys(translation)
            next_button().click()
        else:
            text_area.send_keys('idk')
            next_button().click()
            wait(1)
            print(right_solution())

            phrase_transl_database.add_translation(to_transl, right_solution())
    elif header == 'Escreva em inglês':
        translation = phrase_transl_database.get_translation(to_transl, False)
        print(header, '\n')
        if translation != None:
            print('Resposta:\n\"%s\"' % translation)
            text_area.send_keys(translation)
            next_button().click()
        else:
            text_area.send_keys('idk')
            next_button().click()
            wait(1)
            print(right_solution())

            phrase_transl_database.add_translation(right_solution(), to_transl)
    logger.info('play_phrase_transl end.')


def play_word_transl(header, word_transl_database):
    '''O jogo pede para você escrever uma palavra em inglês'''
    logger.info('play_word_transl called.')

    if not isinstance(word_transl_database, Database):
        raise EOFError('TypeError. It\'s not a Database object.')

    print('[Word Translation]\n')
    to_transl = header[9:-11]
    print(to_transl)

    translation = word_transl_database.get_translation(to_transl, False)

    if translation != None:
        translation_list = translation.split(
            ',')  # some translations comes with more than one translation inplicit in the page
        print('Resposta:\n\"%s\"' % translation_list[-1])
        driver.find_element_by_xpath('//input[@data-test="challenge-text-input"]').send_keys(
            translation_list[-1])
        next_button().click()
    else:
        driver.find_element_by_xpath('//input[@data-test="challenge-text-input"]').send_keys(
            'idk')
        next_button().click()
        wait(.5)
        right_solution()
        print(right_solution())

        word_transl_database.add_translation(right_solution(), to_transl)
    logger.info('play_word_transl end.')


def play_compl_the_phrase_choice(header, compl_the_phrase_choice_database):
    '''o jogo pede para que você complete a frase com a resposta correta e oferece
    multiplas escolhas'''
    logger.info('play_compl_the_phrase_choice called.')

    if not isinstance(compl_the_phrase_choice_database, Database):
        raise EOFError('TypeError. It\'s not a Database object.')

    def clean_list(list_):
        """Removes numbers and new lines"""
        pattern = '[0-9]\n'
        list_ = [re.sub(pattern, '', i) for i in list_]
        return list_

    print('[Choice Game]\n%s' % header)

    # hint_list
    hint_str_raw = driver.find_element_by_xpath('//div[@dir="ltr"]').text
    hint_list = hint_str_raw.splitlines()
    # Choices
    choices_raw = driver.find_elements_by_xpath('//label[@data-test="challenge-choice"]')
    choices = []
    for choice in choices_raw:
        choices.append(choice.text)
        print(choice.text)
    choices = clean_list(choices)
    right_choice = None

    # check the choice position
    if ''.join(hint_list).islower():
        # in the beginning of a phrase
        insert_pos = 0
    else:
        # in-between or end of a frase
        insert_pos = 1

    for choice in choices:
        hypothesis_list = hint_list.copy()
        hypothesis_list.insert(insert_pos, choice)
        hypothesis_str = ' '.join(hypothesis_list)
        print(hypothesis_list)
        search = compl_the_phrase_choice_database.get_translation(hypothesis_str, True)
        if search != None:
            right_choice = choice
            break

    # checks if the right answer or not
    if right_choice != None:
        print('Resposta:\n\"%s\"\n' % right_choice)
        right_choice_button = driver.find_element_by_xpath(
            '//div[text()="%s"]//ancestor::label[@data-test="challenge-choice"]' % right_choice)
        right_choice_button.click()
        next_button().click()
    else:
        first_button = text_area = driver.find_element_by_xpath(
            '//label[@data-test="challenge-choice"][1]')
        first_button.click()
        next_button().click()
        try:
            # try to find the wrong answer element
            driver.find_element_by_xpath('//h2[text()="Solução correta:"]')
        except common.exceptions.NoSuchElementException:
            # ripe the answer from the right answer from the box
            hypothesis_list = hint_list.copy()
            choice = choices[0]
            hypothesis_list.insert(insert_pos, choice)
            site_answer = ' '.join(hypothesis_list)
            print('Acertei sem querer:\n%s\n%s' % (site_answer, right_solution()))

            wait(1)

            compl_the_phrase_choice_database.add_translation(site_answer, right_solution())

        else:
            # ripe the answer from the right solution header
            wait(1)
            hypothesis_list = hint_list.copy()
            choice = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="_75iiA _2qUov"][1]'))
            ).text
            hypothesis_list.insert(insert_pos, choice)
            site_answer = ' '.join(hypothesis_list)
            print('Errei, a resposta é:\n%s\n' % site_answer)

            translation_pt = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="_2GiCe"][2]//child::div'))
            ).text

            wait(1)

            compl_the_phrase_choice_database.add_translation(site_answer, translation_pt)
    logger.info('play_compl_the_phrase_choice end.')


def play_compl_the_phrase_transl(header, compl_the_phrase_transl_database):
    '''Insert doc'''
    logger.info('play_compl_the_phrase_transl called.')

    if not isinstance(compl_the_phrase_transl_database, Database):
        raise EOFError('TypeError. It\'s not a Database object.')

    print('[Complete Translation Game]\n%s\n' % header)

    text_area = driver.find_element_by_xpath('//input[@data-test="challenge-text-input"]')

    # block to convert the hint box into a string, because he comes separeted
    to_transl = driver.find_element_by_xpath('//span[@data-test="hint-sentence"]').text

    en_hint_str = driver.find_element_by_xpath('//label[@dir="ltr"]').text

    print(en_hint_str)

    translation = compl_the_phrase_transl_database.get_translation(to_transl, False)

    '''se ele não achar, executa uma cópia da frase em inglês, erra o jogo
    e rouba a tradução em português. As frases são quardadas em dois arquivos distintos
    pareados pelo número da linha'''
    if translation is not None:
        translation_list = translation.split()
        hint_list = en_hint_str.split()
        print(hint_list)
        for index, word_transl in enumerate(translation_list):
            try:
                if word_transl != hint_list[index]:
                    missing_word = re.sub(r"[.!?]", "", word_transl)
                    break
            except IndexError:
                missing_word = re.sub(r"[.!?]", "", word_transl)
                break

        print('Resposta:\n\"%s\"' % missing_word)
        text_area.send_keys(missing_word)

        next_button().click()
    else:
        text_area.send_keys('idk')
        next_button().click()
        print(right_solution())

        compl_the_phrase_transl_database.add_translation(right_solution(), to_transl)
    logger.info('play_compl_the_phrase_transl end.')


header_xpath = '//h1[@data-test="challenge-header"]'
duolingo_element = '//div[@class="_1PvQ4"]'
lesson_complete = '//h2[@data-test="answers-correct"]'


def run_games():
    '''Runs the A.I.'''
    while True:
        wait(0.5)
        # Is duolingo speaking? (this only skip with next button)
        try:
            header = WebDriverWait(driver, 2).until(
                EC.visibility_of_element_located((By.XPATH, header_xpath))
            ).text
        except common.exceptions.TimeoutException:
            next_button(timeout=10)
            next_button().click()
        else:
            # Is it a card game?  data-test='challenge challenge-select'
            if 'Qual destas imagens é ' in header:
                play_card_choice(header, words)

            # Is it a judge game?
            elif header == 'Marque o significado correto':
                play_phrase_choice(header, phrase_choice)

            # Is it a form translation game?  data-test='challenge challenge-translate'
            elif (header == 'Escreva em português') or (header == 'Escreva em inglês'):
                play_phrase_transl(header, phrases)

            # Is it a write word game?
            elif 'Escreva "' and '" em inglês' in header:
                play_word_transl(header, words)

            # Is it a include choice game?
            elif header == 'Escolha a palavra que falta':
                play_compl_the_phrase_choice(header, phrases_word_choice)

            # Is it a complete translation game?
            elif header == 'Complete a tradução':
                play_compl_the_phrase_transl(header, compl_the_phrase_transl)

            # Is duolingo trying to get the bot to speak?
            elif header == 'Fale esta frase':
                driver.find_element_by_xpath('//button[@data-test="player-skip"]').click()

        # Is finished?
        try:
            complete = driver.find_element_by_xpath('//div[@style="opacity: 1; width: 100%;"]')
            print('100%')
        except common.exceptions.NoSuchElementException:
            next_button().click()
            print('\nPróximo ========>\n')
        else:
            next_button(timeout=10).click()
            wait(3)
            driver.get(DUOLINGO)
            wait(2)
            break


def run_levels(skill_name, replay=False, play_all_levels=True):
    """Run levels"""
    while True:
        skill_button = WebDriverWait(driver, 14).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//div[contains(text(), "%s")]//ancestor::div[@data-test="skill"]'
                 % skill_name)))
        skill_button.click()

        level_status = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="_1eGmL"]'))
        ).text

        if (level_status == 'Nível 5/5') and (replay != True):
            toaster.show_toast('Duo Breaker', 'All Games Are Done!')
            print('All Games Are Done!')
            break

        wait(2)
        start_level = WebDriverWait(driver, 4).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@data-test="start-button"]'))
        )
        start_level.click()
        if replay:
            play_all_levels = False
            next_button().click()

        run_games()

        if play_all_levels == True:
            continue
        else:
            break


def get_skill_names(overwrite=False):
    '''Get skill challenge names and save to a file'''
    cookie = Cookie(driver, DUOLINGO)
    initializate(cookie)
    wait(4)
    skill_path = pathlib.Path.cwd() / 'skill_lists'
    skill_path.mkdir(exist_ok=True)

    title_list = driver.title.split(' ')
    course = title_list[-1]

    SKILLS_FILE_PATH = skill_path / '{}_skill_names.txt'.format(course)
    try:
        with open(SKILLS_FILE_PATH, 'r') as file:
            pass
    except FileNotFoundError:
        file_exist = False
    else:
        print('Já satisfeito')
        file_exist = True

    if overwrite or file_exist == False:
        skill_names_path = driver.find_elements_by_css_selector('.QmbDT')
        x = len(skill_names_path)
        y = 0
        pattern = r'^\d\s'  # Whatever digit on the left + \n gets ripoff

        for skill_raw in skill_names_path:
            skill_name = re.sub(pattern, '', skill_raw.text)
            with open(SKILLS_FILE_PATH, 'a') as file:
                print(skill_name)
                file.write(skill_name)
                file.write('\n')
            y += 1
            porc = (y / x) * 100
            print('Getting challenge names: %{}'.format(int(porc)))
        print('Search for challenges in {}'.format(SKILLS_FILE_PATH))


def get_tip(skill_name):
    skill_button = WebDriverWait(driver, 14).until(
        EC.visibility_of_element_located(
            (By.XPATH, '//div[contains(text(), "%s")]//ancestor::div[@data-test="skill"]'
             % skill_name)))

    skill_button.click()

    tip_button = WebDriverWait(driver, 4).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@class="IeiLn"]//child::button[1]'))
    )
    tip_button.click()

    wait(3)

    tip_text = WebDriverWait(driver, 4).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@class="_3E4No"]'))
    )

    skill_name = WebDriverWait(driver, 4).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="_2m4ST"]'))
    ).text
    print(skill_name)
    print(tip_text.text)

    with open('%s_tip.txt' %skill_name, 'w', encoding='utf-8') as file:
        file.write(tip_text.text)

    driver.get(DUOLINGO)


if __name__ == '__main__':
    cookie = Cookie(driver, DUOLINGO)

    skills = []
    for skill in skills:

        initializate(cookie)
        get_tip(skill)

        # phrases = Database(skill, 'phrases', 'en', 'pt')
        # phrases_word_choice = Database(skill, 'phrases_word_choice', 'en', 'pt')
        # phrase_choice = Database(skill, 'phrases_choice', 'en', 'pt')
        # compl_the_phrase_transl = Database(skill, 'compl_the_phrase_transl', 'en', 'pt')
        # words = Database(skill, 'words', 'en', 'pt')
        #
        #
        # run_levels(skill)


# //textarea[@lang="en"] or //textarea[@lang="pt"]