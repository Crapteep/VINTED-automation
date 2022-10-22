from ast import Index
from asyncio import events
from calendar import c
from genericpath import exists
from json import load
from msilib.schema import Property
from optparse import Values
from pyclbr import Function
import sqlite3
from config import *
from urls import *
from functions import *
import time
import threading
import os
from cryptography.fernet import Fernet
from os import getcwd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import random

from selenium import webdriver
import pyautogui as pygui
import re
from datetime import datetime


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
from kivy.properties import StringProperty, BooleanProperty
from kivy.properties import Clock
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.uix.dropdown import DropDown

Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '900')


class Database():
    "This class has basic info about your account"
    def __init__(self, dbase_path) -> None:
        self.con = sqlite3.connect(dbase_path)   #dir_dbase
        self.c = self.con.cursor()


    def __del__(self):
        self.con.close()


    def create_new_account(self, id, username, password) -> None:       #ta metoda w gui
        entry = self.fetchall_record(columns='*', table='Accounts', conditions={'acc_id': id})

        if not entry:
            encrypted_password = self._encrypt_password(id, password)
            self.insert_record('Accounts', columns=[], values=[id, username, encrypted_password])
        else:
            print(f'Account with id: {id} already exists!')
    

    def load_account_data(self, id : int) -> None:
        data = self.fetchall_record(columns=['login', 'password'], table='Accounts', conditions={'acc_id': id})
        username, encrypted_password = data[0]
        password = self._decrypt_password(id, encrypted_password)

        return username, password


    def insert_record(self, table : str, columns : list, values : list) -> None:
        if columns:
            column_val = '(' + ', '.join([f'{column}' for column in columns]) + ')'
        else:
            column_val = ''

        self.c.execute(f'''INSERT INTO {table}{column_val}
                        VALUES({','.join(['?' for _ in values])})''', values)
        self.con.commit()


    def update_record(self, table: str, changes: dict, conditions: dict):
        values = tuple(changes.values()) + tuple(conditions.values())
        self.c.execute(f'''UPDATE OR IGNORE {table}
                        set {', '.join([f'{change}=?' for change in changes])}
                        WHERE {' AND '.join([f'{condition}=?' for condition in conditions])}''',
                        values)
        self.con.commit()


    def fetchall_record(self, columns : list, table : str, conditions : dict) -> list:
        values = conditions.values()
        self.c.execute(f'''SELECT {', '.join([f'{column}' for column in columns])}
                        FROM {table}
                        WHERE {' AND '.join([f'{condition}=?' for condition in conditions])}''',
                        tuple(values))
     
        return self.c.fetchall()


    def delete_record(self, table: str, conditions : dict) -> None:   #zrobic usuwanie + powiadomienie ze zostana wszystkie inne info nt przedmiotow usuniete
        values = conditions.values()
        self.c.execute(f'''DELETE FROM {table}
                        WHERE {' AND '.join([f'{condition}=?' for condition in conditions])}''',
                        tuple(values))
        self.con.commit()
        
    
    
    def delete_account(self, id : int, input_password : str) -> None: #hasło musi być poprawne żeby usunać konto z bazy!

        username, password = self.load_account_data(id)
        if input_password == password:
            self.delete_record(table='Accounts', conditions={'acc_id' : id})

            path = getcwd()
            dir_mykey = path + f'\\mykey_{str(id)}'
            try:
                os.remove(dir_mykey)
            except:
                print('File not found!')

        else:
            print('Wrong password!')


    def _encrypt_password(self, id, password) -> None:
        key = Fernet.generate_key()

        with open(f'mykey_{str(id)}', 'wb') as mykey:
            mykey.write(key)
        print(f'mykey_{str(id)}')

        f = Fernet(key)
        return f.encrypt(password.encode())
       

    def _decrypt_password(self, id, encrypted_password) -> None:
        path = getcwd()
        dir_mykey = path + f'\\mykey_{str(id)}'

        with open(dir_mykey, 'rb') as mykey:
            key = mykey.read()

        f = Fernet(key)
        return f.decrypt(encrypted_password).decode("utf-8")


class VintedSession():
    username_list = []
    threads_list = []

    def __init__(self, database) -> None:
        self.db = database


    def set_browser(self):
        option = webdriver.EdgeOptions()
        option.add_argument('inprivate')

        s = Service(dir_webdriver)

        self.browser = webdriver.Edge(service=s, options=option)
        self.browser.implicitly_wait(RESPOND_TIME)
        self.browser.maximize_window()


    def log_in_to_account(self) -> None:
        self.browser.get(url_login)
        self.browser.find_element(By.ID, 'onetrust-accept-btn-handler').click()
        self.browser.find_element(By.ID, 'username').send_keys(self.username)
        self.browser.find_element(By.ID, 'password').send_keys(self.password + Keys.ENTER)

        self.wait_until_complete_captcha()


    def wait_until_complete_captcha(self) -> None:  #przy captcha img w gui jak prawidlowo ma wygladac
        while True:
            if self.browser.title == 'Vinted':
                break
            else:
                pygui.alert('Complete captcha and press "Finish"!', 'Captcha', 'Finish!')
            

    def find_new_likes(self) -> None:
        self.browser.get(url_notification)
        notifications = self.browser.find_elements(By.CLASS_NAME, 'u-disable-hover')
        
        for notification in notifications:  
            url = notification.get_attribute('href')
            if KEY_STRING in url:
                finder = re.compile(r'/\d\d\d\d\d\d\d\d\d\d/')
                item_id = finder.findall(url)
                item_id = int(item_id[0].replace('/', ''))

                username = notification.find_element(By.XPATH, './/a').text
                notification_time = notification.find_element(By.XPATH, './/h3//span').get_attribute('title')
                notification_date = date_extract(notification_time)

                today_date = get_today_date()

                if not self.db.fetchall_record('*', 'Notifications', {'username' : username, 'item_id' : item_id, 'acc_id' : self.acc_id}):
                    self.db.insert_record('Notifications',
                                    ['acc_id', 'username', 'item_id', 'url', 'created', 'modified'],
                                    [self.acc_id, username, item_id, url, notification_date, today_date]
                                    )

    def is_element_present(self, elem_type, elem_value: str) -> bool:
        try:
            self.browser.find_element(by=elem_type, value=elem_value)
        except NoSuchElementException:
            return False
        return True


    def run_threding(self, function, username: str, delay_time: int) -> None:
        new_thread = threading.Thread(target=function, args=[username, delay_time]) 
        self.threads_list.append(new_thread)
        new_thread.start()


    def delay_delete(self, username: str, delay_time: int) -> None:
        time.sleep(delay_time)
        self.username_list.remove(username)


    def input_price(self, price):
        self.browser.find_element(By.XPATH, '//*[@class="u-flexbox"]/button').click()
        self.browser.find_element(By.ID, 'offer').send_keys(str(price) + Keys.ENTER) 


    def suggest_lower_price(self):
        self.db.c.execute(f'''SELECT item_id, url, username
                        FROM Notifications
                        WHERE acc_id=?
                        AND is_available=?
                        AND personalized=?
                        AND created<datetime('now', '{TIME_AFTER_LIKED}', 'localtime'
                        ''', (self.acc_id, 1, False))
        records = self.c.fetchall()

        for record in records:
            personalized = False
            available = 1
            item_id, url, username = record
            self.browser.get(url)

            if not self.is_element_present('class', 'notification__icon '):
                messages = self.browser.find_elements(By.CLASS_NAME, 'Bubble_narrow__Fmq5T')

                if len(messages) == 1 and self.browser.title not in banned_items:
                    price = float(self.browser.find_element(By.XPATH, '//*[@class="u-flexbox"]/span').text.strip().replace(' zł', '').replace(',', '.'))
                    input_message = self.browser.find_element(By.NAME, 'composerInput')

                    if username not in self.username_list and price > LOWEST_ALLOOWABLE_ITEM_PRICE:
                        gretting = random.choice(grettings_list)

                        input_message.send_keys(message_text.format(gretting, username, PERCENT_OF_PRICE, TIME_TO_NEW_DISCOUNT) + Keys.ENTER)

                        new_price = calc_percent_of_price(price, PERCENT_OF_PRICE)
                        self.input_price(new_price)

                        self.username_list.append(username)
                        self.run_threding(self.delay_delete, username, TIME_TO_NEW_DISCOUNT * 3600)
                        
                        personalized = True

                    else:
                        input_message.send_keys(next_message + Keys.ENTER)

            if not personalized:
                available = 0

            #update bazy danych
            today_date = get_today_date()
            self.db.update_record('Notifications',
                            {'is_available': available, 'personalized': personalized, 'modified': today_date, 'discount': PERCENT_OF_PRICE},
                            {'acc_id': self.acc_id, 'item_id': item_id, 'username': username})


    def chceck_ending_discounts(self):
        records = db.c.execute(f'''SELECT url, discount, item_id
                                FROM Notifications
                                WHERE acc_id=?
                                AND is_available=?
                                AND personalized=?
                                AND modified < datetime('now', '-{TIME_TO_NEW_DISCOUNT} hours', 'localtime')''',
                                self.acc_id, 1, True)
        for record in records:
            url, discount, item_id = record
            if discount == '':
                continue

            self.browser.get(url)
            if self.is_element_present('xpath', '//*[@class="u-flexbox"]/span'):
                read_price = float(self.browser.find_element(By.XPATH, '//*[@class="u-flexbox"]/span').text.strip().replace(' zł', '').replace(',', '.'))
                price = calc_price_before_discount(read_price, discount)
                self.input_price(price)

            time_now = get_today_date()
            self.db.update_record('Notifications', {'modified': time_now, 'is_available': 0}, {'item_id': item_id, 'acc_id': self.acc_id})

        #ogarnac zeby pobralo procent znizki bezposredni z tekstu wiadomosci lub zapisuywalo do bazy danych
        # i pozniej na podstawie ceny jaka jest ta glowna zrobic obliczenie tego %
        #z wiadomoscia moze byc lipa bo jak ktos zmieni jej treść to nie znajdzie
        # moze lepiej zapisywac do bazy % znizki jaki zrobilo albo cene jaka byla oryginalna




    def run(self, acc_id) -> None:

        self.username, self.password = self.db.load_account_data(acc_id)
        self.acc_id = acc_id

        self.set_browser()
        self.log_in_to_account()

        while True:
            self.find_new_likes()
            self.suggest_lower_price()

            self.chceck_ending_discounts()


    def __del__(self):
        self.browser.quit()








# db = Database()



    


# Screens
class MainWindow(Screen):
    target = ObjectProperty()
    # number_of_acc = len(db.accounts_list)
    event_list = []
    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_interval(self.update, 1/60)

    def on_click(self):
        s.run(90570960)

    def update(self, dt):
        
        if self.manager.current == 'accounts':
            MyAccountsWindow.load_accounts(self)

        if self.manager.current == 'login':
            self.manager.get_screen(self.manager.current).ids.spinner_id.values = db.accounts_list
        
        if self.manager.current == 'add_new_account':
            # AddAccountWindow.input_checker()
            pass




            # username_inp = self.manager.get_screen(self.manager.current).ids.username_input.text
            # password_inp = self.manager.get_screen(self.manager.current).ids.password_input.text
            # acc_id_inp = self.manager.get_screen(self.manager.current).ids.account_id_input.text

            # if (username_inp and password_inp and acc_id_inp) != '':
            #     AddAccountWindow.st(self)
            #     app = VintedApp.get_running_app()
            #     add_screen = app.root.get_screen('add_new_account')

            #     bl = add_screen.sumbit_enabled
            #     print(bl)

            # print(username_inp)
            # print(password_inp)
            # print(acc_id_inp)
            pass
            #zrobic to moze na ekranie funckje i tu wywolac


                



class LoginInWindow(Screen):
    acc_list = ListProperty(None)
    
    def __init__(self, **kw):
        super().__init__(**kw)

    def start(self):
        s.run()


    def spinner_clicked(self, value):
        self.ids.click_label.text = f'You selected:{value}'



class MyAccountsWindow(Screen):
    # acc1 = ObjectProperty(None)
    # acc2 = ObjectProperty(None)
    # acc3 = ObjectProperty(None)
    # acc4 = ObjectProperty(None)
    # acc5 = ObjectProperty(None)
    def on_reload(self):
        db.create_new_account()


    def load_accounts(self, *args):
        # print('dzziala')
        # obj = self.manager.get_screen(self.manager.current).ids
    
        # if self.number_of_acc != len(db.accounts_list):
        #     db.load_accounts()
        #     self.number_of_acc = len(db.accounts_list)

        # for i in range(5):
        #     try:
        #         obj[f'acc{str(i+1)}'].text = db.accounts_list[i]+' - press to show more info'
        
        #     except IndexError:
        #         obj[f'acc{str(i+1)}'].text = 'Empty!'
        pass

class AppSettingsWindow(Screen):
    def on_click(self):
        s.browser.get('https://www.facebook.com/')
    pass

class AddAccountWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)
    acc_id = ObjectProperty(None)

    sumbit_enabled = BooleanProperty(False)

    def st(self):
        # print('dziala')
        self.sumbit_enabled = True
    
    def on_click_add_btn(self):
        db.create_new_account(self.ids.account_id_input.text, self.ids.username_input.text, self.ids.password_input.text)
        # print(self.ids.username_input.text, self.ids.password_input.text, self.ids.account_id_input.text)

    def clear_inputs_fields(self):
        self.account_id_input.text = ''
        self.password_input.text = ''
        self.username_input.text = ''

    def input_checker(self, *args):
        pass
        # obj = self.manager.get_screen(self.manager.current).ids
        # print(obj)


        


        # name = obj['username_input'].text
        # psw = obj['password_input'].text
        # id = obj['account_id_input'].text

        # print(name, psw, id)
        # if (name and psw and id) == '':
        #     AddAccountWindow.sumbit_enabled = True
        # # print(obj['username_input'].text)
        # # print(self.username_input)





#screen manager
class WindowManager(ScreenManager):
    pass



class AccountPrinterLayout(StackLayout):
    pass






kv = Builder.load_file("vinted.kv")


class VintedApp(App):
    def build(self):
        return kv
    

if __name__ == "__main__":
    db = Database(dir_dbase)
    s = VintedSession(db)
    
    VintedApp().run()
    # s.run()
    
# s.browser.get('xd')
# time.sleep(5)