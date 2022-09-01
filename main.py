import sqlite3
from sys import path
path.insert(1, 'D:\\Dokumenty\\Python Project\\vinted')
from cryptography.fernet import Fernet
from os import getcwd

dir_dbase = dir_dbase = r'D:\Dokumenty\Python Project\vinted\VINTED-dbase.db'
# class Vinted:
#     def dbase_session(self):
        # self.con = sqlite3.connect(r'D:\Dokumenty\Python Project\vinted\VINTED-dbase.db')   #dir_dbase
        # self.c = self.con.cursor()






class User:
    "This class has basic info about your account"
    def __init__(self) -> None:
        self.con = sqlite3.connect(r'D:\Dokumenty\Python Project\vinted\VINTED-dbase.db')   #dir_dbase
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
                    print(self.password, self.username, self.account_id)
                    running = False
        print('The data has been loaded successfully!')


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


    def show_all_existing_accounts(self) -> None:
        select_query = '''SELECT acc_id, login
                        FROM Accounts'''
        self.c.execute(select_query)
        self.accounts_list = self.c.fetchall()

        if len(self.accounts_list) != 0:
            #wyswietlanie listy kont - domyslnie w gui
            print('\nAccount list: \n')

            for count, account in enumerate(self.accounts_list):
                print(f'{count+1}. {account[0]} - {account[1]}')

        else:
            print('There are no accounts saved in the database. \nPlease create a new account.')    #do zrobienia w gui
        

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




new = User()
# new.create_new_account()
# new.show_all_existing_accounts()
new.load_account_details()


    #odszyfrowywanie hasla
    




# acc1 = Account()
# acc1.create_new_account()

# print(acc1.dir_mykey)


# print(getcwd())