# Text mining pour Disney Paris

Ce projet est lié à un projet scolaire de M2 avec comme commanditaire l’équipe Consumer Experience Integration de Disneyland Paris.

Le but est de récupérer les avis booking.com relatifs aux différents hôtels affiliés à Disneyland Paris et de réaliser des analyses de texte intégrées dans une application.

Ce projet est réalisé en Python.

Pour utiliser l'application et les différents scripts voici la marche à suivre :

Importer le projet en local via zip (à dézipper) ou git clone

Installer les dépendances avec la commande : pip install -r requirements.txt

un fichier .sql est disponible dans l'onglet /data pour installer la base de donnée contenant les avis déjà extraits, nous utilisons MySQL avec phpmyadmin sur le compte local avec user="root" et password="" mais un autre logiciel et compte sont possibles il faudra le préciser dans le fichier app.py au niveau de la connection, ligne 27.

Exécuter le fichier app.py pour lancer l'application.
