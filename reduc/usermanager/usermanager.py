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
from datetime import datetime

from five import grok
from zope import schema
from Acquisition import aq_inner
from z3c.form import field, button, interfaces
from Products.statusmessages.interfaces import IStatusMessage
#from z3c.form.ptcompat import ViewPageTemplateFile
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from zope.component import getMultiAdapter, getUtility
from zope.interface import invariant, Invalid, implements
from plone.directives import form, dexterity

from reduc.user.command import PasswordException
from reduc.usermanager import MyMessageFactory as _
from reduc.usermanager.umutil import IUserManagerUtil
from reduc.usermanager.support import SessionUsers, AdminUtil
from reduc.usermanager.vocabularies import suspend_vocabulary

class IUserManager(form.Schema):
    '''Administrador de Usuarios'''


class UcBaseView:
    def uc_update(self):
        self.users = SessionUsers(self.context)
        self.current_user = self.users.current()
        self.admin = AdminUtil(self.context)
        self.util = getUtility(IUserManagerUtil)
        self._status = IStatusMessage(self.request)

    def has_permission(self):
        if not self.current_user:
            return True
        return self.admin.has_permission(self.current_user)

        if self.current_user and \
                not self.admin.has_permission(self.current_user):
            self.set_status(u'Usted no tiene permisos para actuar sobre este usuario.', u'error')
        else:
            self.clear_status()

    def clear_status(self):
        return self._status.show()

    def add_status(self, msg, kind):
        self._status.add(msg, kind)

    def set_status(self, msg, kind=u''):
        self.clear_status()
        self.add_status(msg, kind)

    def entry_from_user(self, dct):
        entry = dict(**dct)
        for k, v in entry.items():
            if 'date' in k :
                entry[k] = self._string_from_date(v)
                continue
            entry[k] = entry[k].encode('ascii') if entry[k] else ''

        # Consolidamos givenName2 y surname2 en givenname y surname
        self._attributes_to_list(entry, 'givenName')
        self._attributes_to_list(entry, 'sn')
        if 'uid' in entry:
            entry['uid'] = entry['uid'].lower()
        return entry

    def _attributes_to_list(self, dct, k):
        '''Convierte {k='a', k2='b'} en {k=['a', 'b']}'''
        k2 = k + '2'
        if not k2 in dct:
            return
        if not dct[k2]:
            del(dct[k2])
            return
        dct[k] = [dct[k], dct[k2]]
        del(dct[k2])

    def _date_or_empty_from_entry(self, entry, key):
        date_string = entry.first(key, '')
        if not date_string:
            return ''
        return self._date_from_string(date_string)

    def user_from_entry(self, entry):
        entry['dateCreation'] = self._date_or_empty_from_entry(entry, 'dateCreation')
        entry['dateExpiration'] = self._date_or_empty_from_entry(entry, 'dateExpiration')
        self._list_to_attributes(entry, 'givenName')
        self._list_to_attributes(entry, 'sn')
        return entry

    def _list_to_attributes(self, dct, k):
        '''Convierte {k=['a', 'b']} en {k='a', k2='b'}'''
        k2 = k + '2'
        if type(dct[k]) <> list:
            return
        elif len(dct[k]) == 1:
            dct[k2] = ''
            dct[k] = dct[k][0]
        else:
            dct[k2] = dct[k][1]
            dct[k] = dct[k][0]

    def _date_from_string(self, strdate):
        return datetime.strptime(strdate, '%Y%m%d')

    def _string_from_date(self, date):
        return date.strftime('%Y%m%d')


class View(grok.View, UcBaseView):
    '''Vista por defecto del UserManager'''
    grok.context(IUserManager)
    grok.require('usermanager.view')
    grok.name('view')

    def update(self):
        self.uc_update()


class Search(grok.View):
    '''Vista que ejecuta la busqueda'''
    grok.context(IUserManager)
    grok.require('usermanager.view')
    grok.name('search')

    def update(self):
        util = getUtility(IUserManagerUtil)
        users = util.find(self.request.uid_or_ci)
        self.users = SessionUsers(self.context)
        self.users.set_users(users)

    def render(self):
        self.response.redirect(self.context.absolute_url())
        return u''


class IPassword(form.Schema):
    '''Formulario para el cambio de passwords'''
    userPassword = schema.Password(
            title = _(u'Password'),
            min_length = 8,
            )

    userPassword2 = schema.Password(
            title = _(u'Repita Password'),
            min_length = 8,
            )

    @invariant
    def passwords_equal(data):
        if data.userPassword <> data.userPassword2:
            raise Invalid(_(u'Los password introducidos deben sr iguales.'))


class Password(form.SchemaForm, UcBaseView):
    '''Cambio de Password'''
    grok.context(IUserManager)
    grok.require('usermanager.password')
    grok.name('password')

    schema = IPassword
    ignoreContext = True

    def update(self):
        self.uc_update()
        form.SchemaForm.update(self)

        self.users = SessionUsers(self.context)
        user = self.users.current()
        uid = user.get('uid', '???')
        cn = user.get('cn', '???')
        accClass = user.get('accClass', '???')

        self.label = "Cambiar password para '{0}'".format(uid)
        self.description = '{0}: {1}'.format(cn, accClass)

    @button.buttonAndHandler(u'Ok')
    def handleApply(self, action):
        '''Boton OK'''
        if not self.admin.has_permission(self.current_user):
            return

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.users = SessionUsers(self.context)
        user = self.users.current()
        util = getUtility(IUserManagerUtil)

        try:
            user = util.password(user, data['userPassword'])
            self.users.set_current(user)
            self.status = 'Password cambiado.'
            self.response.redirect(self.context.absolute_url())

        except PasswordException as e:
            self.context.plone_utils.addPortalMessage(e.message, 'error')


    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        '''Boton cancelar'''
        self.response.redirect(self.context.absolute_url())


class IUser(form.Schema):
    '''Representa a un usuario para las vista de creacion, edicion y
    despliegue'''

    givenName  = schema.TextLine(
            title = _(u'Primer Nombre'),
            )

    givenName2  = schema.TextLine(
            title = _(u'Segundo Nombre'),
            required = False,
            )

    sn  = schema.TextLine(
            title = _(u'Primer Apellido'),
            )

    sn2  = schema.TextLine(
            title = _(u'Segundo Apellido'),
            required = False,
            )

    accClass = schema.TextLine(
            title = _(u'Clasificacion del Usuario'),
            )

    uid = schema.TextLine(
            title = _(u'Login'),
            required = False
            )

    uniqueIdentifier  = schema.TextLine(
            title = _(u'Cedula de Identidad'),
            description = _(u'Ej. V11222333'),
            )

    dateCreation = schema.Date(
            title = _(u'Fecha de Creacion'),
            )

    dateExpiration = schema.Date(
            title = _(u'Fecha de Expiracion'),
            )

class User:
    implements(IUser)

    def __init__(self, **kargs):
        self.uid = kargs['uid']
        self.givenName = kargs['givenName']
        self.sn = kargs['sn']
        self.uniqueIdentifier = kargs['uniqueIdentifier']
        self.accClass = kargs['accClass']
        self.dateCreation = kargs['dateCreation']
        self.dateExpiration = kargs.get('dateExpiration', '')


class New(form.SchemaAddForm, UcBaseView):
    '''Nuevo Usuario'''
    grok.context(IUserManager)
    grok.require('usermanager.new')
    grok.name('new')

    schema = IUser
    ignoreContext = True
    label = 'Crear un nuevo Usuario'
    name = 'usermanager-add-form'

    def updateWidgets(self):
        form.SchemaAddForm.updateWidgets(self)
        widget = self.widgets['accClass']
        widget.template = ViewPageTemplateFile("browser/acc_class_widget.pt")

    def create(self, data):
        entry = self.entry_from_user(data)
        return entry

    def add(self, entry):
        self.users = SessionUsers(self.context)
        util = getUtility(IUserManagerUtil)
        entry = util.new(entry)
        users = util.find(entry['uniqueIdentifier'])
        self.users = SessionUsers(self.context)
        self.users.set_users(users)

    @button.buttonAndHandler(_('Crear'), name='save')
    def handleAdd(self, action):
        self.uc_update()

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        try:
            obj = self.createAndAdd(data)
        except Exception as err:
            self.set_status(str(err), u'error')
            return

        if obj is not None:
            self._finishedAdd = True
            self.set_status('Usuario creado.', u'info')

    @button.buttonAndHandler(_(u'Cancelar'), name='cancel')
    def handleCancel(self, action):
        self.uc_update()
        self.set_status('Accion cancelada.', u'info')
        self.request.response.redirect(self.nextURL())


class Edit(form.SchemaEditForm, UcBaseView):
    '''Modificar Usuario'''
    grok.context(IUserManager)
    grok.require('usermanager.modify')
    grok.name('modify')

    schema = IUser
    ignoreContext = False
    label = 'Modificar Usuario'
    name = 'usermanager-edit-form'

    def getContent(self):
        entry = SessionUsers(self.context).current()
        user = self.user_from_entry(entry)
        return user

    def update(self):
        self.uc_update()
        if not self.has_permission():
            self.set_status(u'Usted no tiene permisos para actuar sobre este usuario.', u'warn')

        form.SchemaEditForm.update(self)
        widget = self.widgets['accClass']
        widget.template = ViewPageTemplateFile("browser/acc_class_widget.pt")

    @button.buttonAndHandler(_(u'Modificar'), name='save')
    def handleApply(self, action):
        if not self.has_permission():
            self.set_status(u'Usted no tiene permisos para actuar sobre este usuario.', u'error')
            return

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        entry = self.entry_from_user(data)

        try:
            new = self.util.modify(self.current_user, entry)
            self.users.set_current(new)
            form.SchemaEditForm.applyChanges(self, entry)
            self.set_status(u'Usuario modificado satisfactoriamente')
            self.response.redirect(self.context.absolute_url())
        except Exception as err:
            self.set_status(str(err), u'error')


    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        form.SchemaEditForm.handleCancel(self, action)


class IVoid(form.Schema):
    '''Interface vacía'''


class ISuspend(form.Schema):
    '''Interface para la suspension'''
    motive = schema.Choice(vocabulary=suspend_vocabulary,
                           title=_(u"Motivo"))


class Suspend(form.SchemaForm, UcBaseView):
    '''Suspende un Usuario'''
    grok.context(IUserManager)
    grok.require('usermanager.suspend')
    grok.name('suspend')

    schema = ISuspend
    ignoreContext = True
    label = 'Suspender Usuario'

    def update(self):
        super(Suspend, self).update()
        self.uc_update()

    @button.buttonAndHandler(u'Suspender')
    def handleApply(self, action):
        self.uc_update()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        new = self.current_user.clone()
        new['userPassword'] = data['motive'] + new.get('userPassword')

        try:
            new = self.util.modify(self.current_user, new)
            self.users.set_current(new)
            self.set_status('Usuario suspendido.', u'info')
        except Exception as err:
            self.set_status(str(err), u'error')

        self.request.response.redirect(self.context.absolute_url_path())

    @button.buttonAndHandler(u"Cancelar")
    def handleCancel(self, action):
        '''Cancelar. Regresar a pagina principal.'''
        self.uc_update()
        self.set_status('Accion cancelada.', u'info')
        self.request.response.redirect(self.context.absolute_url_path())


class Reactivate(form.SchemaForm, UcBaseView):
    '''Reactiva un Usuario'''
    grok.context(IUserManager)
    grok.require('usermanager.reactivate')
    grok.name('reactivate')

    #schema = IPassword
    ignoreContext = True
    label = 'Reactivar Usuario'

    def update(self):
        super(Reactivate, self).update()
        self.uc_update()

    @button.buttonAndHandler(u'Reactivar')
    def handleApply(self, action):
        self.uc_update()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        new = self.current_user.clone()
        new['userPassword'] = '{SSHA5}setme'
        new['zimbraMailStatus'] = 'enabled'
        new['zimbraAccountStatus'] 'active'

        try:
            new = self.util.modify(self.current_user, new)
            self.users.set_current(new)
            self.set_status('Usuario reactivado. Cambie su password', u'info')
        except Exception as err:
            self.set_status(str(err), u'error')

        self.request.response.redirect(self.context.absolute_url_path())

    @button.buttonAndHandler(u"Cancelar")
    def handleCancel(self, action):
        '''Cancelar. Regresar a pagina principal.'''
        self.uc_update()
        self.set_status('Accion cancelada.', u'info')
        self.request.response.redirect(self.context.absolute_url_path())
