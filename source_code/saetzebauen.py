import os
import subprocess
import sys
import bs4
from einfuehrung import einfuehrung, maximize_console
from menudownload import *
import de_dep_news_trf
satzanalyse_werkzeug = de_dep_news_trf.load()
from fuzzywuzzy import fuzz
import regex
import pickle
from satzmetzger.satzmetzger import Satzmetzger
import numpy as np
linebreaknach = 70
prompt = drucker.f.black.magenta.normal('''Wahrscheinlich sind einige der Wörter falsch! \nDu musst diese Wörter korrigeren!\nGib die Nummer, die vor dem Wort steht ein, um das Wort zu korrgieren!\nGib q ein, um das Programm zu beenden!\n''')
return_choice =  drucker.f.black.brightcyan.italic(" <-- Gib diese Nummer ein, wenn du alles korrigiert hast!\n")
kurzbeschreibung_aufgabe = drucker.f.black.brightyellow.italic("\nKorrigiere die Fehler! Gib die letzte Zahl in der Liste ein, sobald du fertig bist! Dein Ziel ist, auf 100% Übereinstimmung zu kommen!\n")
def read_pkl(filename):
    with open(filename, "rb") as f:
        data_pickle = pickle.load(f)
    return data_pickle


def transpose_list_of_lists(listexxx):
    try:
        return [list(xaaa) for xaaa in zip(*listexxx)]
    except Exception as Fehler:
        print(Fehler)
        try:
            return np.array(listexxx).T.tolist()
        except Exception as Fehler:
            print(Fehler)
            return listexxx


def delete_duplicates_from_nested_list(nestedlist):
    tempstringlist = {}
    for ergi in nestedlist:
        tempstringlist[str(ergi)] = ergi
    endliste = [tempstringlist[key] for key in tempstringlist.keys()]
    return endliste.copy()


def flattenlist_neu_ohne_tuple(iterable):
    def iter_flatten(iterable):
        it = iter(iterable)
        for e in it:
            if isinstance(e, list):
                for f in iter_flatten(e):
                    yield f
            else:
                yield e

    a = [i for i in iter_flatten(iterable)]
    return a



def txtdateien_lesen(text):
    try:
        dateiohnehtml = (
                b"""<!DOCTYPE html><html><body><p>""" + text + b"""</p></body></html>"""
        )
        soup = bs4.BeautifulSoup(dateiohnehtml, "html.parser")
        soup = soup.text
        return soup.strip()
    except Exception as Fehler:
        print(Fehler)


def get_file_path(datei):
    pfad = sys.path
    pfad = [x.replace('/', '\\') + '\\' + datei for x in pfad]
    exists = []
    for p in pfad:
        if os.path.exists(p):
            exists.append(p)
    return list(dict.fromkeys(exists))


def get_text():
    p = subprocess.run(get_file_path(r"Everything2TXT.exe")[0], capture_output=True)
    ganzertext = txtdateien_lesen(p.stdout)
    return ganzertext


satzmetzgerle = Satzmetzger()
maximize_console()
einfuehrung('Korrekturnator')
ganzertext = get_text()
einzelnesaetze = satzmetzgerle.zerhack_den_text(ganzertext)
allesaetzefertigfueraufgabe = []
allemoeglichenpunkte = 0
punktevomuser = 0
for satzindex, einzelnersatz in enumerate(einzelnesaetze):
    cfg = {}
    richtigersatz=''
    falschersatz=''
    print('\n')
    analysierter_text = satzanalyse_werkzeug(einzelnersatz)
    dokument_als_json = analysierter_text.doc.to_json()
    alleverbenimsatz = []
    schongedruckt = False
    komplettersatzanzeigen = dokument_als_json["text"]
    for wordindex, token in enumerate(dokument_als_json["tokens"]):
        anfangwort = token["start"]
        endewort = token["end"]
        aktuelleswort = dokument_als_json["text"][anfangwort:endewort]
        leerzeichenplatz = len(dokument_als_json["text"][anfangwort:endewort]) * "_"
        platzhalter = (
                dokument_als_json["text"][:anfangwort]
                + leerzeichenplatz
                + dokument_als_json["text"][endewort:]
        )
        satzschongemacht = dokument_als_json["text"][:anfangwort]
        satzdrucken = drucker.f.black.white.italic('Wir sind hier:   ') + drucker.f.white.black.normal(satzschongemacht) + drucker.f.brightyellow.black.italic(aktuelleswort)
        lemmawort = token["lemma"]
        korrektursatz = f'{(wordindex + 1)}'
        richtigersatz = richtigersatz + aktuelleswort.strip()

        if token['tag'] == 'PPER' or '$' in token['tag'] or token['tag'] == 'PPOSAT':
            if wordindex  == 0:
                aktuelleswort = aktuelleswort.title()
            falschersatz = falschersatz+ aktuelleswort.strip()
            if wordindex+1 < 10:
                cfg['\t' + korrektursatz] = aktuelleswort
            elif wordindex + 1 >= 10:
                cfg[korrektursatz] =  aktuelleswort
            continue
        else:
            if wordindex == 0:
                lemmawort = lemmawort.title()
            falschersatz = falschersatz+ lemmawort.strip()
            if wordindex+1 < 10:

                cfg['\t' +korrektursatz] =lemmawort
            elif wordindex + 1 >= 10:
                cfg[korrektursatz] =  lemmawort
            continue
    aktuelleuebereinstimmung = fuzz.ratio(richtigersatz, falschersatz)
    prompt = drucker.f.black.brightred.italic('     Die aktuelle Übereinstimmung zwischen dem richtigen und dem falschen Satz liegt bei: ') + drucker.f.brightred.black.normal(f' {aktuelleuebereinstimmung} Prozent     ')
    erreichbarepunktzahl = 100 - aktuelleuebereinstimmung
    allemoeglichenpunkte = allemoeglichenpunkte + erreichbarepunktzahl
    cfg = m.config_menu(kurzbeschreibung_aufgabe, cfg.copy(),  return_choice =return_choice, prompt=prompt + kurzbeschreibung_aufgabe)
    falschersatz = regex.sub(r'\s+', '', ''.join([x[1] for x in cfg.items()]))
    aktuelleuebereinstimmungneu = fuzz.ratio(richtigersatz, falschersatz)

    if aktuelleuebereinstimmungneu >= aktuelleuebereinstimmung:
        print(drucker.f.brightwhite.brightgreen.italic('      Super! Der Satz ist besser als vorher: Die jetzige Übereinstimmung liegt bei: ') + drucker.f.brightgreen.black.negative(f' {aktuelleuebereinstimmungneu} Prozent     '))
        punktedieserdurchgang = 100 - aktuelleuebereinstimmungneu
        punktedieserdurchgang = abs(punktedieserdurchgang - erreichbarepunktzahl)
        punktevomuser = punktevomuser + punktedieserdurchgang

    elif aktuelleuebereinstimmungneu < aktuelleuebereinstimmung:
        print(drucker.f.brightwhite.red.italic('     Das war leider nicht so gut! Der Satz ist schlechter als vor der Korrektur! Die jetzige Übereinstimmung liegt bei: ') + drucker.f.brightred.black.negative(f' {aktuelleuebereinstimmungneu} Prozent     '))
        punktedieserdurchgang = 100 - aktuelleuebereinstimmungneu
        punktedieserdurchgang = -1 * abs(punktedieserdurchgang - erreichbarepunktzahl)
        punktevomuser = punktevomuser + punktedieserdurchgang

    print(drucker.f.brightgreen.black.negative(f'\n     Der richtige Satz lautet: {komplettersatzanzeigen}\n\n'))
    print(drucker.f.cyan.brightwhite.italic(f'\n\n     Erreichte Punkte: {punktevomuser} von {allemoeglichenpunkte}            \n\n'))
    print(10 * '\n')
