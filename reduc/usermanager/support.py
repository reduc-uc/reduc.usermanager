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

from zope.component import getMultiAdapter, getUtility
from reduc.usermanager.umutil import IUserManagerUtil

class AdminUtil:
    '''Clase de soporte para el acceso a la informacion del administrador '''
    def __init__(self, context):
        self.context = context

        sdm = self.context.session_data_manager
        self.session = sdm.getSessionData(create=True)

        self.admin = self._get_admin()

    def _get_admin(self):
        '''Devuelve los datos ldap para el usuario plone'''
        admin = self.session.get('usermanager:admin', None)

        if admin is None:
            uid = self.context.portal_membership.getAuthenticatedMember().getUserName()
            util = getUtility(IUserManagerUtil)
            admin = util.find(uid).next()

        return admin

    def has_permission(self, user):
        '''true si el administrador tiene permisos para actuar sobre el usuario'''
        if user is None:
            return False

        adminDomains = [self._domain_from_string(x)
                for x in self.admin.get('adminDomain', [])]
        userDomain = self._domain_from_string(
                user.get('accClass', ''))
        return self._any_subdomain(userDomain, adminDomains)

    def can_act(self, action):
        '''true si el administrador puede ejecutar la accion dada sobre el usuario'''
        return action in self.admin.get('adminAction', [])


    def _any_subdomain(self, sub, doms):
        '''true si sub es subdominio de algun elemento en doms'''
        return any((self._subdomain(sub, dom) for dom in doms))


    def _subdomain(self, sub, dom):
        '''true si sub es subdominio de dom'''
        return all([not x or x == y for (x,y) in zip(dom, sub)])

    def _domain_from_string(self, s):
        ''' Dado un string de dominio 'tu,dep1,dep2' devuelve
        la lista de dominio ['tu', 'dep1', 'dep2'] '''
        return (s.lower() + ',,,').split(',')[:3]


class SessionUsers:
    '''Clase de soporte para el acceso a los usuarios seleccionados'''
    LIST_KEYS = ['objectClass']

    def __init__(self, context):
        self.context = context
        sdm = self.context.session_data_manager
        self.session = sdm.getSessionData(create=True)

    def get_users(self):
        users = self.session.get('usermanager:users', [])
        return users

    def set_users(self, users):
        users = list(users)
        self.session['usermanager:users'] = users
        self.session['usermanager:idx'] = 0 if users else None

    def get_idx(self):
        idx = self.session.get('usermanager:idx', None)
        return idx

    def set_idx(self, idx):
        self.session['usermanager:idx'] = idx

    def current(self):
        idx = self.get_idx()
        if idx is None:
            return None

        user = self.get_users()[idx].clone()
        for k in user.keys():
            if k in self.LIST_KEYS:
                continue

            if type(user[k]) == list and len(user[k])==1:
                user[k] = user[k][0]
        return user

    def set_current(self, user):
        idx = self.get_idx()
        self.get_users()[idx] = user

    def next(self):
        pass

    def prev(self):
        pass

    def first(self):
        pass

    def last(self):
        pass


