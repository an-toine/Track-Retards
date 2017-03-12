# Suivi automatisé des retards SNCF :steam_locomotive:

Cette application python en console permet d'afficher les retards pour un numéro de train donné.

En complément, il est possible de stocker ces informations dans une feuille de calcul Google Sheets, et même d'envoyer un petit message sur Twitter à la SNCF.

Cette application se base sur l'API d'accès aux horaires en temps réel fournie par la [SNCF en open data](http://data.sncf.com/api). Les trains supportés actuellement sont les TGV, TER et Intercités.

## Prérequis
Pour utiliser cette application, un certain nombre de prérequis doivent être validés :

 * Une installation de Python 3, le code n'ayant pas été testé sur des versions antérieures
 * Des identifiants pour accéder aux API de la SNCF, de Twitter, et de Google Documents
 * Les modules [tweepy](https://github.com/tweepy/tweepy), [google-api-python-client](https://pypi.python.org/pypi/google-api-python-client), [dateutil](https://pypi.python.org/pypi/python-dateutil/2.6.0), [emoji](https://pypi.python.org/pypi/emoji) et [peewee](https://github.com/coleifer/peewee) doivent être installés pour utiliser les différents modules de sortie
 * Un serveur et une base de données MySQL pour stocker la ponctualité des trains et afficher des statistiques détaillées sur les évènements de la semaine ou du mois.

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

###Stockage des données dans MySQL
Si le module `peewee` est installé, il est possible de stocker dans une base de données des informations sur la ponctualité des trains et d'afficher des rapports détaillés sur ceux-ci.

La configuration de ce module de sortie se fait dans le fichier `retards.cfg`, dans la section **MySQL**. Les options suivantes doivent être complétées :

 * `mysql_host` : le nom d'hôte de la base de données
 * `mysql_port` : le port de connexion à utiliser
 * `mysql_user` : le nom d'utilisateur à utiliser pour se connecter
 * `mysql_password` : le mot de passe de connexion de l'utilisateur
 * `mysql_db` : la base de données qui contiendra les tables créées par le script

À la première utilisation du script, les tables suivantes seront créées :

 * `city`
 * `disruption`
 * `train`
 * `trip`

Ces tables sont alors alimentées à chaque utilisation du programme, même si le train n'a pas rencontré de difficulté sur son trajet.

##Utilisation

###Options courantes

    ./retards.py --help
    usage: retards.py [-h] [--config CONFIG] [--show-stats] [--weekly] [--monthly]
                      [--no-google-sheets] [--no-twitter] [--no-mysql] [--version]
                      num_train
    
    Programme permettant de récupérer les retards pour un numéro de train
    
    positional arguments:
      num_train           Numéro du train à récupérer
    
    optional arguments:
      -h, --help          show this help message and exit
      --config CONFIG     Emplacement du fichier de configuration
      --show-stats        Afficher des statistiques pour ce train. Cette option
                          requiert MySQL
      --weekly            Afficher des statistiques hebdomadaires pour ce train.
      --monthly           Afficher des statistiques mensuelles pour ce train.
      --no-google-sheets  Ne pas envoyer les données sur Google Sheets
      --no-twitter        Ne pas envoyer les données sur Twitter
      --no-mysql          Ne pas envoyer les données sur MySQL
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

    ./retards.py --no-twitter --no-google-sheets --no-mysql 17990
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

###Statistiques

Note : pour utiliser au mieux cette fonctionnalité, il est nécessaire de disposer du plus de données possible pour un train.
Il est donc conseillé d'exécuter de manière quotidienne ce programme (avec un outil comme `cron` par exemple) pour enregistrer chaque jour les évènements qui ont pu se produire sur le trajet.

####Afficher les statistiques de ponctualité d'un train pour la semaine, sans envoyer de message sur Twitter

    ./retards.py --no-twitter --show-stats --weekly 886739
    Du 06/03/2017 au 12/03/2017, le train 886739 a été perturbé 2 voyages sur 4, soit un taux de ponctualité de 50.0%, en hausse par rapport à la periode précédente (3 perturbations, 50.0%, de ponctualité).
    
    Le retard moyen est de 6.25 minutes.
    
    Causes de perturbation :
    
    * Réutilisation d'un train : 1 problème
    * Train en panne : 1 problème

####Afficher les statistiques de ponctualité d'un train pour le mois, sans envoyer de message sur Twitter

    ./retards.py --no-twitter --show-stats --monthly 886739
    Du 01/03/2017 au 31/03/2017, le train 886739 a été perturbé 2 voyages sur 7, soit un taux de ponctualité de 71.43%, en hausse par rapport à la periode précédente (11 perturbations, 47.62%, de ponctualité).
    
    Le retard moyen est de 3.57 minutes.
    
    Causes de perturbation :
    
    * Train en panne : 1 problème
    * Réutilisation d'un train : 1 problème

####Afficher les statistiques de ponctualité d'un train pour le mois, et envoyer un message sur Twitter

    ./retards.py --no-twitter --show-stats --monthly 886739
    Du 01/03/2017 au 31/03/2017, le train 886739 a été perturbé 2 voyages sur 7, soit un taux de ponctualité de 71.43%, en hausse par rapport à la periode précédente (11 perturbations, 47.62%, de ponctualité).
    
    Le retard moyen est de 3.57 minutes.
    
    Causes de perturbation :
    
    * Train en panne : 1 problème
    * Réutilisation d'un train : 1 problème

###Compte Twitter de démonstration

Le compte Twitter [@RALeBot](https://twitter.com/RALeBot) suit les trains TER 886811 et 886739 et permet de voir des exemples de messages qui peuvent être publiés.

##Tests du code

Pour controler les modifications apportées au code, des tests unitaires ont été écrits dans le fichier `tests.py`.
Leur réalisation nécessite l'installation des modules python `unittest` et `tornado`.

Pour pouvoir disposer de deux situations de test, les réponses renvoyées par l'API de la SNCF ont été sauvegardées dans deux répertoires distincts du dossier `test_server` du projet :

 * Le train 889951, qui est supprimé,
 * Le train 96559, en retard de 10 minutes

Ces réponses sont adaptées à la date de réalisation des tests, et envoyées par un serveur Tornado situé dans le script `test_server/server.py`.

###Réalisation des tests

Modifier l'option `server_name` de la section **SNCF** pour y définir la valeur `http://127.0.0.1:8080/`.

Démarrer ensuite le serveur Tornado : `test_server/server.py`.

Une fois le serveur démarré, lancer les tests avec la commande `python -m unittest` à la racine du projet.