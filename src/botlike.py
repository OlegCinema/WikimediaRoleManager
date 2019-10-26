""" This module contains a bot that
likes a random editing of users.
The module contains exceptions also.

This module uses pywikibot:
https://github.com/wikimedia/pywikibot
"""


import pywikibot as pwb

import random


class LikerBot:
    """This class use to like random revision of user in wikipedia"""

    def __init__(self, lang, user):
        self.wiki = pwb.Site(lang, 'wikipedia')
        self._connect_user(user)

    def _connect_user(self, wiki_user):
        self.user = pwb.User(self.wiki, wiki_user)
        if self.user.isRegistered() == False:
            raise UserNotRegistered("User not found.")
        if self.is_blocked_user() == True:
            raise UserHasBlocked("User has been blocked.")

    def is_blocked_user(self):
        return self.user.isBlocked()

    def _count_contributions(self, counter=400):
        if self.user.editCount(counter) < 1:
            raise UserHasZeroContributions("User has User has less than 1 revision.")
        return self.user.editCount(counter)

    def _get_contributions(self):
        return self.user.contributions()

    def _generate_random_revision(self):
        self.random_diff = random.randrange(self._count_contributions() % 400)

    def like_random_revision(self):
        self._generate_random_revision()
        variable = 0
        for i in self._get_contributions():
            if variable == self.random_diff:
                self.wiki.thank_revision(i[1])
                return (str(i[1]), str(i[0]))
            variable += 1


class UserError(NameError):
    """Main exception which raise when when an error occurs with users."""
    pass


class UserNotRegistered(UserError):
    """This exception raises when user not found."""
    pass


class UserHasZeroContributions(UserError):
    """Wikipedia account of user hasn't contributions."""
    pass

class UserHasBlocked(UserError):
    """Wikipedia account has been blocked"""
    pass