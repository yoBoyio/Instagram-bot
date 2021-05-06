# Built-in/Generic Imports
from time import sleep
import logging
import sys, json
from random import randint

# Library Imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager as CM
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import ui

logging.basicConfig(format='%(levelname)s [%(asctime)s] %(message)s', datefmt='%m/%d/%Y %r', level=logging.INFO)
logger = logging.getLogger()

#GUI
def insert_entry(container, string_to_i, row, column):
    entry_widget = Entry(container)
    entry_widget.insert("end", string_to_i)
    entry_widget.grid(row=row, column=column)
    return entry_widget

def initialize_browser():

    # Do this so we don't get DevTools and Default Adapter failure
    options = webdriver.ChromeOptions()
    # options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # options.add_argument("--log-level=3")

    # Initialize chrome driver and set chrome as our browser
    browser = webdriver.Chrome(executable_path=CM().install(), options=options)

    return browser


def login_to_instagram(browser):
    browser.get('https://www.instagram.com/')
        
    sleep(2)

    # Get the login elements and type in your credentials
    with open("data/database.json", "r") as file:
        database = json.load(file)

    browser.implicitly_wait(30)
    username = browser.find_element_by_name('username')
    username.send_keys(database['credentials']['username'])
    browser.implicitly_wait(30)
    password = browser.find_element_by_name('password')
    password.send_keys(database['credentials']['password'])

    # Click the login button
    browser.implicitly_wait(30)
    browser.find_element_by_xpath("//*[@id='loginForm']/div/div[3]/button").click()

    # If login information is incorrect, program will stop running
    browser.implicitly_wait(30)
    try:
        if browser.find_element_by_xpath("//*[@id='slfErrorAlert']"):
            browser.close()
            sys.exit('Error: Login information is incorrect')
        else:
            pass
    except:
        pass

    
    logger.info('Logged in to '+ database['credentials']['username'])

    # Save your login info? Not now
    browser.find_element_by_xpath("//*[@id='react-root']/section/main/div/div/div/div/button").click()
    # Turn on notifications? Not now
    browser.implicitly_wait(30)
    try:
        btn=browser.find_element_by_xpath("/html/body/div[4]/div/div/div/div[3]/button[2]")
        if btn:
            btn.click()
        else:
            pass
    except:
        pass

def automate_instagram(browser):
    # Keep track of how many you comment
    comments = 0
    with open("data/database.json", "r") as file:
        database = json.load(file)

        browser.implicitly_wait(30)
        browser.get(database['link'])
        sleep(randint(1,2))
      
        # Comment
        while(1):
            # for _ in range (5):
                try:
                    # browser.implicitly_wait(30)
                    browser.find_element_by_xpath("//form").click()
                            # Random chance of commenting
                    browser.implicitly_wait(10)
                    comment = browser.find_element_by_xpath("//textarea")
                    # sleep(randint(database['wait_to_comment']['min'], database['wait_to_comment']['max']))
                    # select 3 random names from list
                    for i in range(3):
                        comment_index=randint(0,len(database['comment_list'])-1)
                        comment.send_keys(database['comment_list'][comment_index])
                  
                    sleep(5)
                    browser.implicitly_wait(10)
                    submit = ui.WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[3]/div/form/button[2]')))
                    submit.click()
                    comments+=1
                    logger.info(f'Commented  {comments} times')
                    #wait some secs and comment again
                    sleep(database['wait_to_comment'])

                except Exception as e:
                        print(e)
                        # logger.info('Error ' + e)
                        browser.refresh()
                        sleep(120)
                        pass
        
            # #after 5 comments wait for 2 mins
            # sleep(120)

    # Close browser when done
    logger.info('Closing chrome browser...')
    browser.close()




# settings window
def setting_ui():
    def save_setting():        

        setting_dict = {
            "credentials": {
                "username": username_f.get(),
                "password": password_f.get()
            },

            "comment_list": [
                comment
                for comment in comment_box_f.get("1.0", "end-1c").split("\n")
                if comment or not comment.isspace()
            ],

            "wait_to_comment": 
                 int(wait_c2_f.get())
            ,

            "link": link_f.get(),


        }

        with open("data/database.json", "w") as file:
            json.dump(setting_dict, file)
        setting_root.destroy()
    

    with open("data/database.json", "r") as file:
        setting = json.load(file)
    

    setting_root = Tk()
    setting_root.resizable(False, False)
    setting_root.title('Bot Settings')

    Label(setting_root, text="USERNAME", width=25).grid(row=0, column=0)
    Label(setting_root, text="PASSWORD", width=25).grid(row=1, column=0)
    Label(setting_root, text="COMMENTS", width=25).grid(row=3, column=0)
    Label(setting_root, text="WAIT TO COMMENT",width=25).grid(row=4, column=0)
    Label(setting_root, text="LINK(POST)",width=25).grid(row=5, column=0)


    username_f = insert_entry(setting_root, setting["credentials"]['username'], 0, 1)
    password_f = insert_entry(setting_root, setting["credentials"]['password'], 1, 1)

    comment_box_f = ScrolledText(setting_root, width=25, height=6)
    comment_box_f.insert("1.0", "\n".join(setting["comment_list"]))
    comment_box_f.grid(row=3, column=1)
    wait_c2_f = insert_entry(setting_root, setting["wait_to_comment"], 4, 1)
    link_f = insert_entry(setting_root, setting["link"], 5, 1)

    Button(setting_root,
                   text="SAVE",
                   bg="#33571c",
                   fg='#ffffff',
                   command=save_setting,
                   width=25).grid(row=11, column=1)

    setting_root.mainloop()

def run_engine():
    browser = initialize_browser()
    login_to_instagram(browser)
    automate_instagram(browser)

if __name__ == "__main__":
    root = Tk()
    root.title('Instagram Comment/Like Bot')
    root.resizable(False, False)
    root.geometry("520x460")
    main_button = Button(root,
                                text="START BOT",
                                bg='#292929',
                                fg='#ffffff',
                                font=25,
                                command=run_engine,
                                width=25).place(relx=0.3, rely=0.5)
    Button(root, text="COMMENT BOT SETTING", command=setting_ui,
                width=25).place(relx=0.35, rely=0.6)

    root.mainloop()