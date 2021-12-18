# En local
Pour installer et lancer l'application epicEvent:<br>
1 - cloner le projet<br>
`git clone https://github.com/yoan34/epicEvent.git`<br>

2 - Aller dans le projet et créer un environnement de travail virtuel:<br>
`cd epicEvent/ && python3 -m venv env`<br>

3 - Activer le bureau virtuel et ajouter les dépendances nécessaires au projet.<br>
`. env/bin/activate && pip install -r requirements.txt`<br>

4 - Lancer l'application et se rendre sur le site:<br>
`cd epicevents/ && python manage.py runserver`<br>

# Avec Docker

## Première utilisation
Il faut être dans le dossier epicEvent.<br>
Installer les images et lancer les services:<br>
`docker-compose up -d`<br>

Lancer le service django pour faire les migrations<br>
`docker-compose run --rm django python manage.py migrate`<br>

Créer un **superuser** avec un **username** et **password**.<br>
`docker-compose run --rm django python manage.py createsuperuser`<br>

Restart les services pour actualiser<br>
`docker-compose restart`<br>
Connectez-vous à l'URL **localhost:8000/admin**


## Prochaine utilisation
Il faut être dans le dossier epicEvent.<br>
`docker-compose up -d`<br>
Connectez-vous à l'URL **localhost:8000/admin**
