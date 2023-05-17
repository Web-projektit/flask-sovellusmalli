Flask-sovellus
==============

Tämä on Flask-sovellusrunko, jota voi käyttää omien Flask-sovellusten kehittämiseen. Se perustuu Miguel Grinberg kirjan Flask Web Development, second edition, lukuun 10.

Huom. wtf.quick_form tarvitsee flask-bootstrap4-kirjaston, mutta muuten muotoilu perustuu
bootstrap 5-versioon, ks. base.html:

https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css
https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js

Lomakevalidointi perustuu bootstrap 5-versioon ja mukautettuun virheilmoitusten poistoon, ks.
scripts.js

Flask-sovellusmallissa on kaksi Blueprinttiä React-sovellusta varten:
1. react käynnistää React-sovelluksen (build) Flaskistä 
2. reactapi tekee käyttäjien autentikoinnin sekä itsenäisessä että
   Flaskistä käynnistetyssä React-sovelluksessa.

Tekijä: Jukka Aula