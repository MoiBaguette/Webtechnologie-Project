# PROGRAMMEERLES VOOR OUDEREN

## De server runnen

Dit is een dev-server, dus run je met `debug=True`-flag!

**Alle afhankelijkheden installeren:**
```
$ pip3 install flask wtforms flask_sqlalchemy flask-wtf email_validator flask-bcrypt flask-login pillow
```

**De server runnen:**
```
$ python run.py
```

## Uitleg

| route                       | bestand              | beschrikbaar als<sup>1</sup> | beschrijving                                             |
|-----------------------------|----------------------|------------------------------|----------------------------------------------------------|
| /                           | index.html           | gast                         | home-pagina                                              |
| /about                      | about.html           | gast                         | over ons                                                 |
| /register                   | register.html        | gast                         | registeren van een gebruiker<sup>2</sup>                 |
| /login                      | login.html           | gast                         | inloggen van een gebruiker<sup>2,3</sup>                 |
| /logout                     | *redirect: /*        | klant                        | uitloggen van een gebruiker                              |
| /courses                    | course_overview.html | docent                       | lessen bewerken/verwijderen                              |
| /course/new                 | new_course.html      | docent                       | nieuwe les aanmaken                                      |
| /course/`:course_id`        | course.html          | klant                        | les informatie                                           |
| /course/`:course_id`/update | new_course.html      | docent                       | les instellingen                                         |
| /course/`:course_id`/delete | *redirect: /courses* | docent                       | les verwijderen                                          |
| /users                      | admin.html           | admin                        | gebruiker overzicht<sup>4</sup>                          |
| /user/self                  | account.html         | klant                        | profiel instellingen                                     |
| /user/`:user_id`            | admin_user.html      | admin                        | gebruiker instellingen                                   |
| /user/`:user_id`/delete     | *redirect: /users*   | admin                        | gebruiker verwijderen                                    |
| /user/`:user_id`/reset      | *redirect: /users*   | admin                        | gebruikers wachtwoord terugzetten<sup>5</sup>            |
|-----------------------------|----------------------|------------------------------|----------------------------------------------------------|
|                             | layout.html          |                              | de basis layout voor alle routen                         |
|                             | static/main.css      |                              | de basis stylesheet voor alle routen                     |
|                             | static/profile_pics  |                              | map met alle profielfoto's inclusief default profielfoto |

> <sup>1</sup> de hierachie is: gast (niet ingelogd), klant, docent, admin<br>
> dus kan een gast het minste bereiken, een klant ook kan alles bereiken wat gast mag etc.

> <sup>2</sup> als hij al ingelogd is, wordt weer naar `/` redirect

> <sup>3</sup> jij kan een `?next=` parameters geven, dan wordt na het inloggen daarheen redirect

> <sup>4</sup> bij gebruiker zoeken moet de naam overeinkomen met de gebruikers naam, nog geen echte zoek-functie

> <sup>5</sup> betekent: zijn wachtwoord is dan gelijk aan zijn e-mail om in te loggen en zijn wachtwoord weer te veranderen, als iemand zijn wachtwoord is vergeten
