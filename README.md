# Suivi automatisé des retards SNCF :steam_locomotive:

Cette application python en console permet d'afficher les retards pour un numéro de train donné.

En complément, il est possible de stocker ces informations dans une feuille de calcul Google Sheets, et même d'envoyer un petit message sur Twitter à la SNCF.

Cette application se base sur l'API d'accès aux horaires en temps réel fournie par la [SNCF en open data](http://data.sncf.com/api). Les trains supportés actuellement sont les TGV, TER et Intercités.

## Prérequis
Pour utiliser cette application, un certain nombre de prérequis doivent être validés :

 * Une installation de Python 3, le code n'ayant pas été testé sur des versions antérieures
 * Des identifiants pour accéder aux API de la SNCF, de Twitter, et de Google Documents
 * Les modules [tweepy](https://github.com/tweepy/tweepy), [google-api-python-client](https://pypi.python.org/pypi/google-api-python-client) doivent être installés

Toute la configuration se fait dans le fichier `retards.cfg`.

### Accès à l'API SNCF
Pour accéder à l'API de la SNCF, un token doit être obtenu. L'inscription peut être faite sur cette [page](http://data.sncf.com/api/fr/register).

Le code d'accès est alors envoyé par e-mail, et doit être renseigné dans le fichier de configuration à la ligne `token` de la section **SNCF**

###Accès à l'API Twitter
Afin de publier les retards des trains sur Twitter, il est également nécessaire de disposer de tokens d'accès.

Le plus facile est de créer un compte dédié pour publier ces retards, et de suivre cette [documentation](https://www.digitalocean.com/community/tutorials/how-to-authenticate-a-python-application-with-twitter-using-tweepy-on-ubuntu-14-04#step-2-%E2%80%94-create-your-twitter-application) pour obtenir vos accès.

Les identifiants doivent être complétés dans la section **Twitter** du fichier de configuration.

###Accès à l'API Google Sheets
La publication des retards dans une feuille de calcul Google est également disponible pour bénéficier d'un suivi plus précis des retards.

Dans un premier temps, créer une feuille de calcul avec pour première ligne les en-têtes du document. Ceux-ci doivent être dans cet ordre :

 * Date
 * Numéro de train
 * Direction
 * Départ prévu
 * Arrivée prévue
 * Arrivée effective
 * Retard
 * Cause du retard

Renseigner dans le fichier de configuration, à la section **Google-Sheets**, le nom de l'onglet contenant le tableau, à la ligne `tab_name`, et l'identifiant du document à la ligne `spreadsheet_id` (cet identifiant se trouve dans l'url du document, qui est de la forme `https://docs.google.com/spreadsheets/d/[identifiant]/edit`).

Il est ensuite nécessaire de compléter la ligne `secret_file`. Pour cela, activer l'API Google Document en suivant ce [guide](https://developers.google.com/sheets/api/quickstart/python#step_1_turn_on_the_api_name).

Il est alors possible de définir à la ligne `secret_file` le nom et l'emplacement choisi pour le fichier secret d'autorisation d'accès à l'API.

À la première utilisation du script, une connexion au compte Google est demandée. Les paramètres d'accès sont alors stockés dans le fichier défini à la ligne `credentials_file` du fichier `retards.cfg`.

##Utilisation

###Options courantes

    ./retards.py --help
    usage: retards.py [-h] [--config CONFIG] [--no-google-sheets] [--no-twitter] [--version] num_train
    
    Programme permettant de récupérer les retards pour un numéro de train
    
    positional arguments:
      num_train           Numéro du train à récupérer
    
    optional arguments:
      -h, --help          show this help message and exit
      --config CONFIG     Emplacement du fichier de configuration
      --no-google-sheets  Ne pas envoyer les données sur Google Sheets
      --no-twitter        Ne pas envoyer les données sur Twitter
      --version           show program's version number and exit

###Récupérer le dernier retard d'un train

    ./retards.py 17990
    Train numero 17990 Lyon-Part-Dieu => Annecy
    Heure de depart prévue : 18:08:00
    Heure d'arrivée prévue : 20:01:00
    Heure d'arrivée effective : 20:21:00
    Retard : 0:20:00
    Cause : Indisponibilité d'un matériel

###Récupérer le dernier retard d'un train, sans partager les données

    ./retards.py --no-twitter --no-google-sheets 17990
    Train numero 17990 Lyon-Part-Dieu => Annecy
    Heure de depart prévue : 18:08:00
    Heure d'arrivée prévue : 20:01:00
    Heure d'arrivée effective : 20:21:00
    Retard : 0:20:00
    Cause : Indisponibilité d'un matériel

###Récupérer le dernier retard d'un train, en spécifiant un fichier de configuration alternatif

    ./retards.py --config /home/robert/config/retards.cfg 17990
    Train numero 17990 Lyon-Part-Dieu => Annecy
    Heure de depart prévue : 18:08:00
    Heure d'arrivée prévue : 20:01:00
    Heure d'arrivée effective : 20:21:00
    Retard : 0:20:00
    Cause : Indisponibilité d'un matériel