// Main js file for reduc.usermanager
//
require([
  'jquery',
  'pat-registry',
  'reduc.usermanager.forms'
], function($, Registry, um) {

  $(function() {
    umm = um;
    if ($('#usermanager-add-form').length === 1) {
        console.log('um new');
        um.init_new_page();
    }
    if ($('#usermanager-edit-form').length === 1) {
        console.log('um edit');
        um.init_edit_page();
    }
  });
});
