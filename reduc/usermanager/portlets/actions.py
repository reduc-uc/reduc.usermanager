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
from zope.formlib import form
from zope.interface import implements
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from reduc.usermanager.usermanager import SessionUsers, AdminUtil

class IUserManagerActions(IPortletDataProvider):
    '''UserManager Actions Interface'''


class Assignment(base.Assignment):
    '''Implementa la interface que define al portlet'''
    implements(IUserManagerActions)

    title = _(u'UserManager: Acciones')


class Renderer(base.Renderer):
    '''Renderer del portlet'''
    render = ViewPageTemplateFile('actions.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        self.users = SessionUsers(self.context)
        self.current_user = self.users.current()
        self.admin = AdminUtil(self.context)

        self.has_permission = self.admin.has_permission(self.current_user)
        self.can_add = self.admin.can_act('new')

        can_modify = self.admin.can_act('modify')
        self.can_modify = self.has_permission and can_modify
        #can_change_password = self.admin.can_act('password')
        #self.can_change_password = self.has_permission and can_change_password

    def can_change_password(self):
        if self.current_user is None:
            return False
        _can_act = self.admin.can_act('password')
        is_suspended = self._is_suspended()
        return self.has_permission and _can_act and not is_suspended

    def can_suspend(self):
        if self.current_user is None:
            return False
        _can_act = self.admin.can_act('suspend')
        is_suspended = self._is_suspended()
        return self.has_permission and _can_act and not is_suspended

    def can_reactivate(self):
        if self.current_user is None:
            return False
        _can_act = self.admin.can_act('reactivate')
        is_suspended = self._is_suspended()
        return self.has_permission and _can_act and is_suspended

    def _is_suspended(self):
        pwd = self.current_user.get('userPassword', None)
        if pwd is None:
            return None
        return '*' in pwd

class AddForm(base.NullAddForm):
    '''Formulario para agregar el portlet'''
    def create(self):
        return Assignment()


class EditForm(base.EditForm):
    '''Formulario para editar el portlet'''
    form_fields = form.Fields(IUserManagerActions)
    label = _(u"Editar Portlet de Acciones del UserManager")
    description = _(u"Este portlet muestra las acciones sobre el usuario actual")
