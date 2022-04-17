# PROGRAMMEERLES VOOR OUDEREN

## De server runnen

Dit is een dev-server, dus run je met `debug=True`-flag!

*Als onze website zo goed is, om het in production te runnen, verwijder het `debug=True` :beers:*

**Alle afhankelijkheden installeren:**
```
$ pip3 install flask wtforms flask_sqlalchemy flask-wtf email_validator flask-bcrypt flask-login pillow
```

**De server runnen:**
```
$ python run.py
```

## Uitleg

### Bestanden

| bestand               | route                       | beschrikbaar als<sup>1</sup> | beschrijving                                           |
|-----------------------|-----------------------------|------------------------------|--------------------------------------------------------|
| index.html            | /                           | gast                         | home-pagina                                            |
| about.html            | /about                      | gast                         | over ons                                               |
| register.html         | /register                   | gast                         | registeren van een gebruiker<sup>2</sup>               |
| login.html            | /login                      | gast                         | inloggen van een gebruiker<sup>2,3</sup>               |
|                       | /logout                     | klant                        | uitloggen van een gebruiker                            |
| course_overview.html  | /courses                    | docent                       | lessen bewerken/verwijderen                            |
| new_course.html       | /course/new                 | docent                       | nieuwe les aanmaken                                    |
| course.html           | /course/`:course_id`        | klant                        | les informatie                                         |
| new_course.html       | /course/`:course_id`/update | docent                       | les instellingen                                       |
|                       | /course/`:course_id`/delete | docent                       | les verwijderen                                        |
| admin.html            | /users                      | admin                        | gebruiker overzicht<sup>4</sup>                        |
| account.html          | /user/self                  | klant                        | profiel instellingen                                   |
| admin_user.html       | /user/`:user_id`            | admin                        | gebruiker instellingen                                 |
|                       | /user/`:user_id`/delete     | admin                        | gebruiker verwijderen                                  |
|                       | /user/`:user_id`/reset      | admin                        | gebruikers wachtwoord terugzetten<sup>5</sup>          |
| index.html            | *not found*                 |                              | 404 page not found handler                             |
| **overige bestanden** |                             |                              |                                                        |
| forms.py              |                             |                              | alle forms voor de websites                            |
| models.py             |                             |                              | alle database structs, om alle tabellen te beschrijven |
| routes.py             |                             |                              | alle routen en endpoints                               |
| server.py             |                             |                              | de server initialatie, database etc.                   |
| site.db               |                             |                              | hoofd-database voor users, courses etc.                |
| .gitignore            |                             |                              | om git te stoppen, \__pycache__ mee up te laden        |
| run.py                |                             |                              | om de server te runnen                                 |
| layout.html           |                             |                              | de basis layout voor alle routen                       |
| static/main.css       |                             |                              | de basis stylesheet voor alle routen                   |
| static/profile_pics   |                             |                              | map met alle profielfoto's                             |

> <sup>1</sup> de hierachie is: gast (niet ingelogd), klant, docent, admin<br>
> dus kan een gast het minste bereiken, een klant ook kan alles bereiken wat gast mag etc.

> <sup>2</sup> als hij al ingelogd is, wordt weer naar `/` redirect

> <sup>3</sup> jij kan een `?next=` parameters geven, dan wordt na het inloggen daarheen redirect

> <sup>4</sup> bij gebruiker zoeken moet de naam overeinkomen met de gebruikers naam, nog geen echte zoek-functie

> <sup>5</sup> betekent: zijn wachtwoord is dan gelijk aan zijn e-mail om in te loggen en zijn wachtwoord weer te veranderen, als iemand zijn wachtwoord is vergeten
