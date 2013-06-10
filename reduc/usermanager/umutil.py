#! /usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010. RedUC
# All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License.
#
##############################################################################
import os
import ConfigParser

from zope.interface import Interface, implements
from zope.component import getUtility
from five import grok

from plone.registry.interfaces import IRegistry

import reduc.user.command

class IUserManagerUtil(Interface):
    def new(dict):
        '''Crea un nuevo usuario'''

    def find(uid_or_ci):
        '''Selecciona usuarios basados en login o cedula'''

    def modify(oldEntry, newDict):
        '''Modifica el usuario seleccionado'''

    def password(entry, pwd):
        '''Cambia el passowrd del usuario seleccionado'''

    def delete(dn):
        '''Borra un usuario dado su dn'''


def init_user(fn):
    def wrapper(self, *args, **kargs):
        if self.user == None:
            self._init_user()
        return fn(self, *args, **kargs)

    return wrapper

class UserManagerUtil(grok.GlobalUtility):
    implements(IUserManagerUtil)

    def __init__(self, config_file=''):
        try:
            self._init_user()
        except:
            self.user = None

    def _init_user(self):
        registry = getUtility(IRegistry)
        uri = registry['reduc.usermanager.uri']
        base_dn = registry['reduc.usermanager.base_dn']
        root_dn = registry['reduc.usermanager.root_dn']
        root_pwd = registry['reduc.usermanager.root_pwd']
        self.user = reduc.user.command.User(uri, base_dn, root_dn, root_pwd)
        pass

    @init_user
    def new(self, dct):
        '''Crea un nuevo usuario'''
        return self.user.new(dct)

    @init_user
    def find(self, uid_or_ci):
        '''Selecciona usuarios basados en login o cedula'''
        uid_or_ci = 'V' + uid_or_ci if uid_or_ci[0].isdigit() else uid_or_ci
        filter = '(|(uid={0})(uniqueIdentifier={0}))'
        users = self.user.search(filter.format(uid_or_ci))
        return users

    @init_user
    def modify(self, oldEntry, newDict):
        '''Modifica el usuario seleccionado'''
        return self.user.modify(oldEntry, newDict)

    @init_user
    def password(self, entry, pwd):
        '''Cambia el passowrd del usuario seleccionado'''
        return self.user.password(entry, pwd)

    @init_user
    def delete(self, dn):
        '''Borra un usuario dado su dn'''

