#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Languages:
    """
    This class is a simple enumeration container for the different languages implemented
    """
    English = 301
    Spanish = 302
    French = 303


# This variable is a global parameter to hold the language state for the running program
CurrentLanguage = Languages.English

EnglishDictionary = {
    'ABOUT_DIALOG': 'This program was created by NREL for the United States Department of Energy.',
    'Choose File to Update...': 'Choose File to Update...',
    'About...': 'About...',
    'File Path': 'File Path',
    'You must restart the app to make the language change take effect.  Would you like to restart now?':
        'You must restart the app to make the language change take effect.  Would you like to restart now?',
    'Old Version': 'Old Version',
    'Keep Intermediate Versions of Files?': 'Keep Intermediate Versions of Files?',
    'Update File': 'Update File',
    'Close': 'Close',
    'Cancel Run': 'Cancel Run',
    'Program Initialized': 'Program Initialized',
    'Running Transition': 'Running Transition',
    'Transition Cancelled': 'Transition Cancelled',
    'Completed Transition': 'Completed Transition',
    'Failed Transition': 'Failed Transition',
    'All transitions completed successfully - Open run directory for transitioned file':
        'All transitions completed successfully - Open run directory for transitioned file',
    'Could not open run directory': 'Could not open run directory',
    'Open Run Directory': 'Open Run Directory',
    'Cannot find a matching transition tool for this idf version': 'Cannot find a matching transition tool for this idf version',
    'Open File for Transition': '',
    'IDF File doesn\'t exist at path given; cannot transition': '',
    'IDF File exists, ready to go': ''
}

SpanishDictionary = {
    'ABOUT_DIALOG': 'Este programa fue creado por el NREL para el Departamento de Energia de los Estados Unidos.',
    'Choose File to Update...': 'Elegir archivo para actualizar ...',
    'About...': 'Acerca de...',
    'File Path': 'Ruta de archivo',
    'You must restart the app to make the language change take effect.  Would you like to restart now?':
        'Debe reiniciar la aplicacion para que el cambio de idioma tenga efecto. Le gustaria reiniciar ahora?',
    'Old Version': 'Version antigua',
    'Keep Intermediate Versions of Files?': 'Mantener versiones intermedias de Archivos?',
    'Update File': 'Actualizar archivo',
    'Close': 'Cerca',
    'Cancel Run': 'Cancelar Ejecutar',
    'Program Initialized': 'Programa Initialized',
    'Running Transition': 'Transición corriendo',
    'Transition Cancelled': 'transición Cancelado',
    'Completed Transition': 'Transición completado',
    'Failed Transition': 'La transición fallida',
    'All transitions completed successfully - Open run directory for transitioned file':
        'Todas las transiciones completada con éxito - Abrir directorio de ejecución para el archivo de la transición',
    'Could not open run directory': 'No se pudo abrir directorio de ejecución',
    'Open Run Directory': 'Directorio de ejecución abierta',
    'Cannot find a matching transition tool for this idf version':
        'No se puede encontrar una herramienta de transición a juego para esta versión de la FID',
    'Open File for Transition': 'Abrir archivo para la Transición',
    'IDF File doesn\'t exist at path given; cannot transition':
        'IDF El archivo no existe en la ruta dada; no puede transición',
    'IDF File exists, ready to go': 'existe IDF del archivo, listo para ir'


}

FrenchDictionary = {
    'ABOUT_DIALOG': 'Ce logiciel a été créé par NREL pour le Departement de l\'Energie des Etats Unis d\'Amérique (US DOE)',
    'Choose File to Update...': 'Choisissez un Fichier à mettre à jour ...',
    'About...': 'A propos...',
    'File Path': 'Chemin du fichier',
    'You must restart the app to make the language change take effect.  Would you like to restart now?':
        'Vous devez relancer le logiciel pour effectuer le changement de langue. Voulez-vous relancer maintenant?',
    'Old Version': 'Ancienne version',
    'Keep Intermediate Versions of Files?': 'Garder les versions intermediaires des fichiers?',
    'Update File': 'Mettre à jour',
    'Close': 'Fermer',
    'Cancel Run': 'Annuler l\'éxécution',
    'Program Initialized': 'Programme initialisé',
    'Running Transition': 'Transition en cours',
    'Transition Cancelled': 'Transition annulée',
    'Completed Transition': 'Transition terminée',
    'Failed Transition': 'Echec de la Transition',
    'All transitions completed successfully - Open run directory for transitioned file':
        'Toutes les transitions effectuées avec succès - Ouvrir le répertoire du fichier mis à jour',
    'Could not open run directory': 'Impossible d\'ouvrir le répertoire d\'éxecution',
    'Open Run Directory': 'Ouvrir le répertoire d\'éxécution',
    'Cannot find a matching transition tool for this idf version':
        'Impossible de trouver un utilitaire de Transition pour cette version d\'IDF',
    'Open File for Transition': 'Ouvrir un fichier pour la transition',
    'IDF File doesn\'t exist at path given; cannot transition':
        'IDF fichier n\'existe pas au chemin donné; transition impossible',
    'IDF File exists, ready to go': 'Le fichier IDF existe, prêt.'
}


def set_language(lang):
    """
    This is the interface for changing the language, call this, save settings, then restart the program
    :param lang: A language identifier from the :py:class:`Languages` enumeration class
    """
    global CurrentLanguage
    CurrentLanguage = lang


def report_missing_keys():
    """
    This function simply scans dictionaries to see if any keys are missing from them compared to a baseline.
    The baseline is currently the English dictionary.
    This function simply reports to the terminal.
    """
    base_keys = EnglishDictionary.keys()
    for dict_name, dictionary in {'Spanish': SpanishDictionary, 'French': FrenchDictionary}.iteritems():  # add here
        print("Processing missing keys from dictionary: " + dict_name)
        for key in base_keys:
            if key not in dictionary:
                print("Could not find key: \"%s\"" % key)


def translate(key):
    """
    This function translates a string into a dictionary.

    :param key: The string to translate
    :return: The translated string
    """
    # if for some reason blank, just return blank
    if key is None or key == "":
        return ""

    # start with English, but switch based on language
    dictionary = EnglishDictionary
    if CurrentLanguage == Languages.Spanish:
        dictionary = SpanishDictionary
    elif CurrentLanguage == Languages.French:
        dictionary = FrenchDictionary

    # if the key is there, return it, otherwise return a big flashy problematic statement
    if key in dictionary:
        return dictionary[key]
    else:
        print("Could not find this key in the dictionary: \"%s\"" % key)
        return "TRANSLATION MISSING"
