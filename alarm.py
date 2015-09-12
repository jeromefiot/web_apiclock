#!/usr/bin/env python

from app import manager
from datetime import *
from random import randint, choice
from time import sleep

@manager.command
def scraptwittos(idcompte, origine, keyword):
    # depuis une recherche sur "#keyword" depuis janvier 2014
    html = urlopen('https://twitter.com/search?q=%23'+keyword+'%20lang%3Afr%20since%3A2014-01-01&src=typd&f=realtime').read()
    soup = BeautifulSoup.BeautifulSoup(html)
    test = soup.findAll('span',attrs={"class":u"username js-action-profile-name"})
    # on creer une liste pour les twittos recherches
    nouveaux = []
    elements = list(test)
    for item in elements:
        # on recupere le nom du twittos
        twittos = item.b.contents[0]
        if twittos not in nouveaux:
            nouveaux.append(twittos)
            # on converti en ID
            idtwittos = IdFromUsername(twittos)[0]
            followerstwittos = IdFromUsername(twittos)[1]
            # on regarde si un nom est identique en base
            testing = Twittos.query.filter_by(idtwitter=idtwittos).all()
            # si ce n'est pas le cas
            if len(testing) == 0:
                # on insere en base
                newtwittos = Twittos(inscription=datetime.utcnow(),
                                     tweeter=twittos,
                                     origine=origine,
                                     idtwitter=idtwittos,
                                     followers=followerstwittos,
                                     etat=0,
                                     iduser=idcompte)
                # on insere en base
                db.session.add(newtwittos)
                # on update les infos de compte
                db.session.commit()
            else:
                pass
    # on attend un peu histoire de pas trop faire mal
    sleep(randint(3,5))
    # on incremente la var nb_scrape du compte User
    nbscrap = User.query.filter(User.id==idcompte).first()
    nbscrap.nb_scrape = nbscrap.nb_scrape+1
    db.session.commit()
    
if __name__ == "__main__":
    manager.run()