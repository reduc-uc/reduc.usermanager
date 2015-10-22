
def uninstall(portal, reinstall=False):
    setup_tool = portal.portal_setup
    setup_tool.runAllImportStepsFromProfile(
        'profile-reduc.usermanager:uninstall')

