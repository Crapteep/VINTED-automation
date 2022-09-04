import sqlite3
from config import *
from urls import *
from functions import *
import time
from cryptography.fernet import Fernet
from os import getcwd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium import webdriver
import pyautogui as pygui
import re

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import SlideTransition
from kivy.lang import Builder
from kivy.graphics.vertex_instructions import Line
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.anchorlayout import AnchorLayout



Config.set('graphics', 'width', '1366')
Config.set('graphics', 'height', '820')

class Session:
    def __init__(self) -> None:
        account = User()
        account.load_account_details()
        vinted = Vinted(account)
        vinted.log_in_to_account()
        vinted.wait_until_complete_captcha()
        vinted.find_new_likes()
        time.sleep(10)


class Item:
    def __init__(self) -> None:
        pass
    

class User:
    "This class has basic info about your account"
    def __init__(self) -> None:
        self.con = sqlite3.connect(dir_dbase)   #dir_dbase
        self.c = self.con.cursor()

        self.account_id = None
        self.username = None
        self.password = None


    def create_new_account(self) -> None:       #ta metoda w gui
        print("Creating a new account.")
        self.username = input("Type username: ")
        self.account_id = int(input("Type account ID: "))
        self.password = input("Type password: ")

        self.insert_new_account_into_dbase()

    
    def load_account_details(self):
        self.show_all_existing_accounts()
        if self.accounts_list:
            running = True
            while running:
                acc_number = int(input('Select the number off account you want to log in to: '))
                if acc_number < 1 or acc_number > len(self.accounts_list):
                    print('Enter the correct account number.')

                else:
                    self.account_id = self.accounts_list[acc_number - 1][0]
                    self.username = self.accounts_list[acc_number - 1][1]
                    
                    select_query = '''SELECT password
                                        FROM Accounts
                                        WHERE login=? AND acc_id=?'''
                    self.c.execute(select_query, (self.username, self.account_id,))
                    encrypted_password = self.c.fetchone()
                    self._decrypt_password(encrypted_password[0])
                    running = False
        print('\nThe data has been loaded successfully!')


    def insert_new_account_into_dbase(self) -> None:
        is_exist = self.did_account_existing(self.account_id)

        if not is_exist:
            self._encrypt_password()
            insert_query = '''INSERT OR IGNORE INTO Accounts(acc_id, login, password)
                            VALUES(?,?,?)'''
            self.c.execute(insert_query, (self.account_id, self.username, self.password))
            self.con.commit()

            print('Account added successfully!')    #tez w gui do zrobienia

        else:
            print('An account with ID: %s already exists!'%self.account_id)    #powiadomienie w gui ze konto istnieje juz


    def did_account_existing(self, account_id : int) -> bool:
        select_query = '''SELECT *
                        FROM Accounts
                        WHERE acc_id=?'''
        self.c.execute(select_query, (str(account_id),))
        entry = self.c.fetchone()

        if entry is None:
            return False
        else:
            return True


    def show_all_existing_accounts(self) -> list:
        print('Wczytuje dane!')
        select_query = '''SELECT acc_id, login
                        FROM Accounts'''
        self.c.execute(select_query)
        self.accounts_list = self.c.fetchall()

        if len(self.accounts_list) != 0:
            #wyswietlanie listy kont - domyslnie w gui
            pass
            # print('\nAccount list: \n')

            # for count, account in enumerate(self.accounts_list):
            #     print(f'{count+1}. {account[0]} - {account[1]}')

        else:
            print('There are no accounts saved in the database. \nPlease create a new account.')    #do zrobienia w gui
        return self.accounts_list

    def delete_account():   #zrobic usuwanie + powiadomienie ze zostana wszystkie inne info nt przedmiotow usuniete
        pass


    def _encrypt_password(self) -> None:
        key = Fernet.generate_key()
        print(getcwd())

        with open(f'mykey_{str(self.account_id)}', 'wb') as mykey:
            mykey.write(key)
        print(f'mykey_{str(self.account_id)}')

        f = Fernet(key)

        self.password = f.encrypt(self.password.encode())


    def _decrypt_password(self, encrypted_password) -> None:
        path = getcwd()
        dir_mykey = path + f'\\mykey_{str(self.account_id)}'

        with open(dir_mykey, 'rb') as mykey:
            key = mykey.read()

        f = Fernet(key)

        self.password = f.decrypt(encrypted_password).decode("utf-8")


class Vinted:
    def __init__(self, account) -> None:
        self.account = account

        option = webdriver.EdgeOptions()
        option.add_argument('inprivate')
        s = Service(dir_webdriver)
        self.browser = webdriver.Edge(service=s, options=option)
        self.browser.implicitly_wait(RESPOND_TIME)
        self.browser.maximize_window()


    def log_in_to_account(self) -> None:
        self.browser.get(url_login)
        self.browser.find_element(By.ID, 'onetrust-accept-btn-handler').click()
        self.browser.find_element(By.ID, 'username').send_keys(self.account.username)
        self.browser.find_element(By.ID, 'password').send_keys(self.account.password + Keys.ENTER)


    def wait_until_complete_captcha(self) -> None:
        while True:
            if self.browser.title == 'Vinted':
                break
            else:
                pygui.alert('Complete captcha and press "Finish"!', 'Captcha', 'Finish!')
    

    def suggest_lower_price(self) -> None:
        pass


    def find_new_likes(self) -> None:
        self.browser.get(url_notification)
        notifications = self.browser.find_elements(By.CLASS_NAME, 'u-disable-hover')

        for item in notifications:
            url = item.get_attribute('href')
            if KEY_STRING in url:
                compiler = re.compile(r'/\d\d\d\d\d\d\d\d\d\d/')
                item_id = compiler.findall(url)
                item_id = int(item_id[0].replace('/', ''))
                username = item.find_element(By.XPATH, './/a').text
            
                self.account.c.execute('''SELECT *
                                        FROM Notifications
                                        WHERE username=? 
                                        AND item_id=?
                                        AND acc_id=?''', (username, item_id, self.account.account_id))

                entry = self.account.c.fetchone()

                if entry is None:
                    notification_time = item.find_element(By.XPATH, './/h3//span').get_attribute('title')
                    notification_date = date_extract(notification_time)
                    self.account.c.execute('''INSERT INTO Notifications(acc_id, username, item_id, url, created, modified)
                                            VALUES(?,?,?,?,?,datetime('now', 'localtime'))''',
                                            (self.account.account_id, username, item_id, url, notification_date))
                    self.account.con.commit()
                    print('New record added!')

                else:
                    print('This notification exist!')







class MenuWindow(Screen):
    def on_button_click(self):
        print('hej, działa!')
        print(self.width, self.height)
        print(self.width*0.008 + self.height*0.008)

class AccountWindow(Screen):
    pass

class WindowManager(ScreenManager):
    pass


class StackLayoutExample(StackLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.account = User()
        self.account_list = self.account.show_all_existing_accounts()
        self.orientation = "lr-tb"
        self.spacing = 10
        # self.orientation = 'vertical'

        for count, account in enumerate(self.account_list):
            #size = dp(100) + i*10
            size = dp(50)
            b = Button(text=f'{count+1}. {account[0]} - {account[1]}', size_hint=(1, None), size=(dp(10), size))
            self.add_widget(b)



# class ScrollViewAccounts(ScrollView):
#     pass

kv = Builder.load_file('vinted.kv')


class VintedApp(App, ):
    def build(self):
        # self.account = User()
        # self.account_list = self.account.show_all_existing_accounts()
        return kv
        # sm = ScreenManager(transition=SlideTransition())
        # sm.add_widget(MenuScreen(name="menu_screen"))
        # sm.add_widget(AccountScreen(name="account_screen"))
        # # sm.transition = NoTransition()
        # # sm.add_widget(Test(name="test"))

        # return sm




