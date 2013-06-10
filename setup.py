from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='reduc.usermanager',
      version=version,
      description="RedUC UserManager",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['reduc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'plone.app.dexterity [grok]',
          'plone.app.referenceablebehavior',
          'plone.app.relationfield',
          'plone.namedfile [blobs]',
          'archetypes.schemaextender',
          'plone.app.registry',
          'reduc.ldap',
          'reduc.user',
          #'collective.z3cform.datepicker',
          'jyu.z3cform.datepicker',
      ],
      extras_require = {
          'test' : ['plone.testing',],
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
