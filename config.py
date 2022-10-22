
dir_dbase = dir_dbase = r'D:\Dokumenty\Python Project\vinted\VINTED-dbase.db'
dir_webdriver = 'D:\\Programy\\edgedriver\\msedgedriver.exe'




RESPOND_TIME = 20   #maksymalny czas oczekiwania na zaladowanie strony [s]
TIME_TO_NEW_DISCOUNT = 24 #[h] - za tyle nastepna znizka
TIME_AFTER_LIKED = '-10 minute'
LOWEST_ALLOOWABLE_ITEM_PRICE = 5    
PERCENT_OF_PRICE = 15

KEY_STRING = '/items/' and '/want_it/new?offering_id='


banned_items = ['Zielony body z wycięciami Zara'] #tytul strony przedmiotu 


grettings_list = ['Cześć', 'Hej', 'Hejka']
message_text = '''{} {} ❤ Zauważyłam, że jedno z moich ubrań wpadło Ci w oko, w związku z tym mam dla Ciebie zniżkę w wysokości {}% z bazowej ceny przedmiotu. Zniżka będzie dostępna przez {}h.'''
next_message = '''Kupując w zestawie płacisz mniej!'''