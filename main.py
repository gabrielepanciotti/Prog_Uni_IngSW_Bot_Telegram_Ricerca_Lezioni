import bs4
import telepot
import requests
import urllib
import time
import re
from urllib.request import Request,urlopen
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

#Pulsanti
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Ricerca Lezioni', callback_data='ricercaLezioni'),
    InlineKeyboardButton(text='Lezioni Personali', callback_data='lezioniPersonali')],
    [InlineKeyboardButton(text='Imposta Filtro', callback_data='impostaFiltro'),
    InlineKeyboardButton(text='Rimuovi Filtro', callback_data='rimuoviFiltro')],
    [InlineKeyboardButton(text='Lista Comandi', callback_data='listaComandi')],
])

keyboard2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Triennale', callback_data='triennale'),
    InlineKeyboardButton(text='Magistrale', callback_data='magistrale')],
    [InlineKeyboardButton(text='Mastriale Ciclo Unico 5 anni', callback_data='magistrale5anni'),
    InlineKeyboardButton(text='Magistrale Ciclo Unico 6 anni', callback_data='magistrale6anni')]
])

keyboardAnnoTriennale = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1', callback_data='primo'),
    InlineKeyboardButton(text='2', callback_data='secondo')],
    [InlineKeyboardButton(text='3', callback_data='terzo'),
    InlineKeyboardButton(text='Fuori Corso', callback_data='fuoriCorso')]
])

keyboardAnnoMagistrale = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1', callback_data='primo'),
    InlineKeyboardButton(text='2', callback_data='secondo')],
    [InlineKeyboardButton(text='Fuori Corso', callback_data='fuoriCorso')]
])

keyboardAnnoMagistrale5 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1', callback_data='primo'),
    InlineKeyboardButton(text='2', callback_data='secondo')],
    [InlineKeyboardButton(text='3', callback_data='terzo'),
    InlineKeyboardButton(text='4', callback_data='quarto')],
    [InlineKeyboardButton(text='5', callback_data='quinto'),
    InlineKeyboardButton(text='Fuori Corso', callback_data='fuoriCorso')]
])

keyboardAnnoMagistrale6 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1', callback_data='primo'),
    InlineKeyboardButton(text='2', callback_data='secondo')],
    [InlineKeyboardButton(text='3', callback_data='terzo'),
    InlineKeyboardButton(text='4', callback_data='quarto')],
    [InlineKeyboardButton(text='5', callback_data='quinto'),
    InlineKeyboardButton(text='6', callback_data='sesto')],
    [InlineKeyboardButton(text='Fuori Corso', callback_data='fuoriCorso')]
])

#Dichiarazione Variabili Globali
dati=[]
nomelezione=[]
docente=[]
nomecorso=[]
linkcorso=[]
parolaChiave=''
mode=0
id_msgOld=0
filtroCorso=''
dipartimentoPersonale = ''
corsoPersonale = ''
annoPersonale = ''
magistrale = 0

#Funzione in ascolto per la ricezione di messaggi testuali
def on_chat_message(msg):
    global mode
    global id_msgOld
    global filtroCorso
    global dipartimentoPersonale
    global corsoPersonale
    global annoPersonale
    global magistrale
    content_type, chat_type, chat_id = telepot.glance(msg)
    #Se il testo è di tipo text va bene altrimenti invia messaggio di errore
    if content_type == 'text':
        name = msg["from"]["first_name"]
        txt = msg['text']
        id_msg = msg['message_id']
        #In base a come inizia il messaggio ricevuto, determina cosa fare
        if txt.startswith('/start'):
            bot.sendMessage(chat_id, 'Ciao %s, sono un bot per la ricerca di lezioni dell Università di Perugia!\n'
                                     'Utilizza i pulsanti per scegliere cosa fare\n'%name, reply_markup=keyboard)
            id_msgOld = id_msg
        elif txt.startswith('/help'):
            bot.sendMessage(chat_id, 'Se hai qualche dubbio o vuoi segnalare errori, scrivimi a @gabby_botLezioni', reply_markup=keyboard)
            id_msgOld = id_msg
        else:
            if mode == 0:
                bot.sendMessage(chat_id,'Non puoi inviare messaggi senza prima selezionare un pulsante')
            elif mode == 1:
                while (id_msg == id_msgOld):
                    time.sleep(5)
                parolaRicerca = txt
                print(parolaRicerca)
                id_msgOld = id_msg
                mode = 0
                # Se il filtroCorso è vuoto significa che non ha impostato il filtro per il corso, altrimenti fa la ricerca filtrata
                if filtroCorso != '':
                    print('Ricerca filtrata')
                    ricercaLezioneFiltrata(chat_id, parolaRicerca, filtroCorso)
                else:
                    ricercaLezione(chat_id, parolaRicerca)
                # Se mode=2 significa che ha richiesto di impostare il filtro dipartimento, quindi va preso in input la parola con cui cercare
            elif mode == 2:
                while (id_msg == id_msgOld):
                    time.sleep(5)
                mode = 0
                filtroCorso = txt
                id_msgOld = id_msg
                print(filtroCorso)
                bot.sendMessage(chat_id,
                                'Filtro %s impostato, ora , verranno visualizzati solo le lezioni appartenenti al corso scelto'% filtroCorso,reply_markup=keyboard)
            if mode == 3:
                while (id_msg == id_msgOld):
                    time.sleep(5)
                mode = 4
                dipartimentoPersonale = txt
                id_msgOld = id_msg
                bot.sendMessage(chat_id, 'Dipartimeno di appartanenza inserito\n'
                                         'Inserisci il nome del corso di appartenenza')
            if mode == 4 and id_msg != id_msgOld:
                corsoPersonale = txt
                id_msgOld = id_msg
                mode = 0
                bot.sendMessage(chat_id, 'Corso di appartanenza inserito\n'
                                         "Seleziona il tipo di corso", reply_markup=keyboard2)


    else:
        bot.sendMessage(chat_id, 'Puoi inviare solo messaggi di testo e utilizzare i pulsanti')

def on_callback_query(msg):
    global mode
    global magistrale
    global filtroCorso
    global annoPersonale
    global dipartimentoPersonale
    global corsoPersonale
    query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, chat_id, query_data)
    if query_data=='ricercaLezioni':
        bot.sendMessage(chat_id, 'Ricerca Lezione\n'
                                 'Inserisci la parola chiave con cui cercare')
        bot.answerCallbackQuery(query_id,text=None,show_alert=None,url=None, cache_time=None)
        mode = 1
    elif query_data=='impostaFiltro':
        bot.sendMessage(chat_id, 'Imposta il corso di appartenenza per filtrare i risultati della ricerca\n'
                                     'Inserisci il nome del corso')
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        mode = 2
    elif query_data=='rimuoviFiltro':
        bot.sendMessage(chat_id, 'Filtro rimosso correttamente')
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        filtroCorso = ''
        mode = 0
    elif query_data=='lezioniPersonali':
        bot.sendMessage(chat_id, "Imposta il dipartimento, il nome del corso, il tipo di corso e l' anno di appartenenza per visualizzare in unico messaggio tutti i link alle tue lezioni\n"
                                     'Inserisci il nome del Dipartimento')
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        mode = 3
    elif query_data == 'listaComandi':
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        bot.sendMessage(chat_id, 'Ecco la lista dei comandi possibili:\n'
                                 '/start - Avvia il Bot \n'
                                 '/help - Riporta errori o problemi\n'
                                 'Ricerca Lezione - Ricerca link per lezione con parola chiave\n'
                                 'Imposta Corso - Imposti il corso per filtrare la ricerca delle lezioni\n'
                                 "Lezioni Personali - Imposti il dipartimento, il corso e l' anno per visualizzare tutte le proprie lezioni",reply_markup=keyboard)
    elif query_data == 'triennale':
        magistrale = 0
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        bot.sendMessage(chat_id, 'Tipo di corso inserito\n'
                                 "Inserisci l'anno di corso", reply_markup=keyboardAnnoTriennale)
    elif query_data == 'magistrale':
        magistrale = 1
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        bot.sendMessage(chat_id, 'Tipo di corso inserito\n'
                                 "Inserisci l'anno di corso", reply_markup=keyboardAnnoMagistrale)
    elif query_data == 'magistrale5anni':
        magistrale = 2
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        bot.sendMessage(chat_id, 'Tipo di corso inserito\n'
                                 "Inserisci l'anno di corso", reply_markup=keyboardAnnoMagistrale5)
    elif query_data == 'magistrale6anni':
        magistrale = 3
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        bot.sendMessage(chat_id, 'Tipo di corso inserito\n'
                                 "Inserisci l'anno di corso", reply_markup=keyboardAnnoMagistrale6)
    elif query_data == 'primo':
        mode = 0
        annoPersonale=1
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        bot.sendMessage(chat_id, 'Anno di appartanenza inserito')
        ricercaCorso(chat_id, dipartimentoPersonale, corsoPersonale, magistrale, annoPersonale)
    elif query_data == 'secondo':
        mode = 0
        annoPersonale=2
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        bot.sendMessage(chat_id, 'Anno di appartanenza inserito')
        ricercaCorso(chat_id, dipartimentoPersonale, corsoPersonale, magistrale, annoPersonale)
    elif query_data == 'terzo':
        mode = 0
        annoPersonale=3
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        bot.sendMessage(chat_id, 'Anno di appartanenza inserito')
        ricercaCorso(chat_id, dipartimentoPersonale, corsoPersonale, magistrale, annoPersonale)
    elif query_data == 'quarto':
        mode = 0
        annoPersonale=4
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        bot.sendMessage(chat_id, 'Anno di appartanenza inserito')
        ricercaCorso(chat_id, dipartimentoPersonale, corsoPersonale, magistrale, annoPersonale)
    elif query_data == 'quinto':
        mode = 0
        annoPersonale=5
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        bot.sendMessage(chat_id, 'Anno di appartanenza inserito')
        ricercaCorso(chat_id, dipartimentoPersonale, corsoPersonale, magistrale, annoPersonale)
    elif query_data == 'sesto':
        mode = 0
        annoPersonale=6
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        bot.sendMessage(chat_id, 'Anno di appartanenza inserito')
        ricercaCorso(chat_id, dipartimentoPersonale, corsoPersonale, magistrale, annoPersonale)
    elif query_data == 'fuoriCorso':
        mode = 0
        annoPersonale=0
        bot.answerCallbackQuery(query_id, text=None, show_alert=None, url=None, cache_time=None)
        bot.sendMessage(chat_id, 'Anno di appartanenza inserito')
        ricercaCorso(chat_id, dipartimentoPersonale, corsoPersonale, magistrale, annoPersonale)

#Ricerca Lezione con la parola ricevuta in input
def ricercaLezione(chat_id,parolaRicerca):
    try:
        result=0
        #Setta i parametri per la richiesta POST e con request la invia alla pagina HTML
        post_data = {'method': 'POST', 'query': parolaRicerca, 'submit': 'Cerca+link'}
        r = requests.post("https://www.unistudium.unipg.it/cercacorso.php", data=post_data)
        #Se la richiesta è andata a buon fine continua
        if r.ok:
            print('Ricerca Effettuata per:'+parolaRicerca)
            #Legge la pagina con i risultati dalla richiesta
            soup = bs4.BeautifulSoup(r.text, "html.parser")
            i = 0
            #Ricerca tutti gli elementi con tag tr(riga)
            for riga in soup.find_all('tr'):
                #Salta la prima riga di intestazione
                if i > 0:
                    #Aggiunge all'array link corso il link per ogni riga trovata
                    linkcorso.append(riga.find('a')["href"])
                    #Per ogni riga ricerca il tag td(colonne) e l'inserisce in array dati per dividere ogni riga dall'altra
                    for item in riga.find_all('td'):
                        dati.append(item.text)
                #Incrementa contatore per contare righe
                i = i + 1
            j = 0
            #Cicla per il numero di righe-1
            for x in range(i - 1):
                #Aggiunge agli array la colonna corrispondente per ogni riga
                nomelezione.append(dati[j])
                docente.append(dati[j + 1])
                nomecorso.append(dati[j + 2])
                j = j + 4
                #Stampa ogni risultato
                stringa = "Nome Lezione: {0}\nDocente: {1}\n" \
                          "Nome Corso: {2}\nLink Corso: {3}".format(nomelezione[x], docente[x], nomecorso[x],
                                                                    linkcorso[x])
                bot.sendMessage(chat_id, stringa)
                #Imposta result=1, se a 0 significa che non ha trovato risultati
                result=1
            print(nomelezione)
            #Pulisce gli array per la prossima ricerca
            nomelezione.clear()
            docente.clear()
            nomecorso.clear()
            linkcorso.clear()
            dati.clear()
            if (result == 0):
                bot.sendMessage(chat_id, 'Nessun risultato trovato per\n'
                                         'Parola Chiave: {0}\n'.format(parolaRicerca), reply_markup=keyboard)
            else:
                bot.sendMessage(chat_id, 'Ricerca Effettuata Correttamente', reply_markup=keyboard)
    except requests.exceptions.RequestException as e:
        bot.sendMessage(chat_id, 'Pagina non trovata',reply_markup=keyboard)


#Ricerca Lezione come precedente ma con l'aggiunta del filtro per il Dipartimento
def ricercaLezioneFiltrata(chat_id,parolaRicerca,filtroCorso,stampaBottoni=1):
    try:
        result=0
        post_data = {'method': 'POST', 'query': parolaRicerca, 'submit': 'Cerca+link'}
        r = requests.post("https://www.unistudium.unipg.it/cercacorso.php", data=post_data)
        if r.ok:
            print('Ricerca Effettuata:'+parolaRicerca)
            soup = bs4.BeautifulSoup(r.text, "html.parser")
            i = 0
            for riga in soup.find_all('tr'):
                if i > 0:
                    linkcorso.append(riga.find('a')["href"])
                    for item in riga.find_all('td'):
                        dati.append(item.text)
                i = i + 1
            j = 0
            for x in range(i - 1):
                nomelezione.append(dati[j])
                docente.append(dati[j + 1])
                nomecorso.append(dati[j + 2])
                #Se nel nome del corso non viene trovata la parola usata come filtro, ritorna -1 e salta la stampa
                if re.search(filtroCorso, nomecorso[x], re.IGNORECASE):
                    stringa = "Nome Lezione: {0}\nDocente: {1}\n" \
                              "Nome Corso: {2}\nLink Corso: {3}".format(nomelezione[x], docente[x], nomecorso[x],
                                                                        linkcorso[x])
                    bot.sendMessage(chat_id, stringa)
                    result=1
                j = j + 4
            nomelezione.clear()
            docente.clear()
            nomecorso.clear()
            linkcorso.clear()
            dati.clear()
            if result==0:
                bot.sendMessage(chat_id, 'Nessun risultato trovato per\n'
                                         'Parola Chiave: {0}\n'
                                         'Filtro Corso: {1}'.format(parolaRicerca, filtroCorso))
            elif result!=0 and stampaBottoni == 1:
                bot.sendMessage(chat_id, 'Ricerca Effettuata Correttamente', reply_markup=keyboard)

    except requests.exceptions.RequestException as e:
        bot.sendMessage(chat_id, 'Pagina non trovata', reply_markup=keyboard)


def ricercaCorso(chat_id,dipartimentoPersonale,corsoPersonale,magistrale,annoPersonale):
    codicecorso=[]
    codcorso=None
    if magistrale == 1:
        link='https://www.unipg.it/didattica/offerta-formativa/offerta-formativa-2021-22?ricerca=on&annoregolamento=2021&dipartimento=&lingua=&tipocorso=LM&sede=&nomecorso='+corsoPersonale+'&cerca=Cerca'
    elif magistrale == 2:
        link = 'https://www.unipg.it/didattica/offerta-formativa/offerta-formativa-2021-22?ricerca=on&annoregolamento=2021&dipartimento=&lingua=&tipocorso=LM5&sede=&nomecorso=' + corsoPersonale + '&cerca=Cerca'
    elif magistrale == 3:
        link ='https://www.unipg.it/didattica/offerta-formativa/offerta-formativa-2021-22?ricerca=on&annoregolamento=2021&dipartimento=&lingua=&tipocorso=LM6&sede=&nomecorso='+corsoPersonale+'&cerca=Cerca'
    else:
        link='https://www.unipg.it/didattica/offerta-formativa/offerta-formativa-2021-22?ricerca=on&annoregolamento=2021&dipartimento=&lingua=&tipocorso=L&sede=&nomecorso='+corsoPersonale+'&cerca=Cerca'
    print(link)
    r = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
    link = ''
    if r.ok:
        print('Ricerca Effettuata')
        soup = bs4.BeautifulSoup(r.text, "html.parser")
        i = 0
        for riga in soup.find_all('tr'):
            if i > 0:
                for links in riga.find_all('a'):
                    linkcorso.append(links.get('href'))
                    print('Linkcorso:'+links.get('href'))
                for item in riga.find_all('td'):
                    dati.append(item.text)
            i = i + 1
        j = 0
        for x in range(i - 1):
            print('dati')
            print(dati)
            nomecorso.append(dati[j+1])
            if magistrale == 3:
                codicecorso.append(dati[j + 4])
            else:
                codicecorso.append(dati[j+3])
            print('corso ')
            print(nomecorso)
            # Se nel nome del corso non viene trovata la parola usata come filtro, ritorna -1 e salta la stampa
            if re.search(dipartimentoPersonale, nomecorso[x], re.IGNORECASE):
                link = 'https://www.unipg.it' + linkcorso[x] + '&tab=INS'
                stringa = "Nome Corso: {0}\nLink Corso: {1}".format(nomecorso[x], link)
                bot.sendMessage(chat_id, stringa)
                print('Corso Trovato')
                print('Link Corso:' + link)
                codcorso = codicecorso[x]
            j = j + 4
        nomecorso.clear()
        linkcorso.clear()
        dati.clear()
        nomelezione.clear()
        try:
            r = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
            if r.ok:
                print('Accesso a corso Effettuato')
                bot.sendMessage(chat_id, "Ecco tutte le lezioni relative al tuo corso e al tuo anno di corso:")
                soup = bs4.BeautifulSoup(r.text, "html.parser")
                x=0
                if annoPersonale == 0:
                    bot.sendMessage(chat_id, 'Essendo fuori corso , verrano visualizzate le lezioni di tutti gli anni')
                for tab in soup.find_all('table'):
                    x=x+1
                    print('x='+str(x))
                    if annoPersonale != 0:
                        if x == annoPersonale:
                            i = 0
                            for riga in tab.find_all('tr'):
                                if i > 0:
                                    j = 0
                                    for lez in riga.find_all('a'):
                                        j = j + 1
                                        if j == 1:
                                            ricercaLezioneFiltrata(chat_id, lez.text.replace("\n", "\t"), codcorso,0)
                                            print('Riga' + str(i) + ' n:' + str(j) + lez.text)
                                i = i + 1
                    else:
                        i = 0
                        for riga in tab.find_all('tr'):
                            if i > 0:
                                j = 0
                                for lez in riga.find_all('a'):
                                    j = j + 1
                                    if j == 1:
                                        ricercaLezioneFiltrata(chat_id, lez.text.replace("\n", "\t"), codcorso,0)
                                        print('Riga' + str(i) + ' n:' + str(j) + lez.text)
                            i = i + 1

                bot.sendMessage(chat_id, 'Fine lista', reply_markup=keyboard)
            else:
                bot.sendMessage(chat_id, 'Corso non trovato', reply_markup=keyboard)
        except requests.exceptions.RequestException as e:
            bot.sendMessage(chat_id, 'Corso non trovato', reply_markup=keyboard)

#Stringa per gestione BOT
TOKEN = 'TOKEN BOT'
bot = telepot.Bot(TOKEN)

bot.message_loop({'chat':on_chat_message, 'callback_query': on_callback_query})


print ('Sto ascoltando...')

#Ciclo per non terminare il programma e farlo continuare all'infinito
while 1:
    time.sleep(8)
