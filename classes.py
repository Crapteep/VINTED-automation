from ast import Index
from asyncio import events
from json import load
from msilib.schema import Property
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
from kivy.properties import StringProperty, BooleanProperty
from kivy.properties import Clock
from kivy.properties import ObjectProperty
from kivy.properties import ListProperty
from kivy.uix.dropdown import DropDown

Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '900')


class User():
    "This class has basic info about your account"
    def __init__(self) -> None:
        self.con = sqlite3.connect(dir_dbase)   #dir_dbase
        self.c = self.con.cursor()

        self.account_id = None
        self.username = None
        self.password = None
        self.accounts_list = []
        self.load_accounts()

    def __del__(self):
        self.con.close()

    def create_new_account(self) -> None:       #ta metoda w gui
        print("Creating a new account.")
        self.username = input("Type username: ")
        self.account_id = int(input("Type account ID: "))
        self.password = input("Type password: ")

        self.insert_new_account_into_dbase()

    
    def load_accountsount_details(self):
        self.load_accounts()
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
            self.load_accounts()
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


    def load_accounts(self) -> list:
        self.accounts_list.clear()
        print('Wczytuje dane!')
        select_query = '''SELECT login
                        FROM Accounts'''
        self.c.execute(select_query)
        for item in self.c.fetchall():
            self.accounts_list.append(item[0])




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

db = User()



    


#Screens
class MainWindow(Screen):
    target = ObjectProperty()
    number_of_acc = len(db.accounts_list)
    event_list = []
    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_interval(self.update, 1/60)


    def update(self, dt):
        
        if self.manager.current == 'accounts' and not self.event_list:
            event = Clock.create_trigger(MyAccountsWindow.load_accounts(self), 2)
            event()
            self.event_list.append(event)
        else:
            try:
                self.event_list[0].cancel()
                self.event_list.clear()
            except:
                pass
                
        if self.manager.current == 'login':
            self.manager.get_screen("login").ids.spinner_id.values = db.accounts_list
        



class LoginInWindow(Screen):
    acc_list = ListProperty(None)
    
    def __init__(self, **kw):
        super().__init__(**kw)


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
        obj = self.manager.get_screen("accounts").ids
        print('\n')
        print('num_of_acc', self.number_of_acc)
        print('obecna liczba kont:', len(db.accounts_list))
        print('\n')
        if self.manager.current == "accounts":
            if self.number_of_acc != len(db.accounts_list):
                db.load_accounts()
                self.number_of_acc = len(db.accounts_list)

            for i in range(5):
                try:
                    obj[f'acc{str(i+1)}'].text = db.accounts_list[i]+' - press to show more info'
            
                except IndexError:
                    obj[f'acc{str(i+1)}'].text = 'Empty!'


class AppSettingsWindow(Screen):
    pass

class AddAccountWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)
    acc_id = ObjectProperty(None)
    
    def clear_inputs_fields(self):
        self.account_id_input.text = ''
        self.password_input.text = ''
        self.username_input.text = ''








#screen manager
class WindowManager(ScreenManager):
    pass



class AccountPrinterLayout(StackLayout):
    pass






kv = Builder.load_file("test_kv.kv")


class VintedApp(App):
    def build(self):
        return kv
    

if __name__ == "__main__":
    VintedApp().run()


    #zrobic tak zeby moznz blylo odswiezac