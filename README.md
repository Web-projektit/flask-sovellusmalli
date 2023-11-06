Flask-sovellusmalli
===================

Tämä on Flask-sovellusmalli, joka soveltuu Flask-sovellusten kehittämiseen. Se perustuu Miguel Grinberg kirjan Flask Web Development, second edition, lukuun 10.

Huom. wtf.quick_form tarvitsee flask-bootstrap4-kirjaston, mutta muuten muotoilu perustuu bootstrap 5-versioon, ks. base.html:

https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css
https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js

Lomakevalidointi perustuu bootstrap 5-versioon ja mukautettuun virheilmoitusten poistoon, ks. scripts.js.  Bootstrap/wtf.html-makrot on korvattu tätä varten niihin perustuvilla omilla quick_form- ja form_field -makroilla. 

Flask-sovellusmallissa on kaksi Blueprinttiä React-sovellusta varten:
1. react käynnistää React-sovelluksen (build) Flaskistä 
2. reactapi tekee käyttäjien autentikoinnin sekä itsenäisessä että
   Flaskistä käynnistetyssä React-sovelluksessa.

Tietokannan päivitys ilman edellistä versiota:
1.   Poista kansio Migrations
2.   Poista taulu alembic
3.   flask db init
4.   flask db migrate
5.   flask db upgrade

Tekijä: Jukka Aula