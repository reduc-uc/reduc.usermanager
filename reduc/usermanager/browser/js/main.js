// Main js file for reduc.usermanager
//
function usermanager_module() {
  // Inicializa los campos en el formulario new
  var today = new Date();
  var day = today.getDate();
  var month = today.getMonth();
  var year = today.getFullYear();

  var $uid = jq('#form-widgets-uid');
  var $dateCreationDay = jq('#form-widgets-dateCreation-day');
  var $dateExpirationDay = jq('#form-widgets-dateExpiration-day');
  var $dateCreationMonth = jq('#form-widgets-dateCreation-month');
  var $dateExpirationMonth = jq('#form-widgets-dateExpiration-month');
  var $dateCreationYear = jq('#form-widgets-dateCreation-year');
  var $dateExpirationYear = jq('#form-widgets-dateExpiration-year');
  var $accClass = jq('#form-widgets-accClass');
  var $accClassTipo = jq('#form-widgets-accClass-tipo');
  var $accClassUbicacion = jq('#form-widgets-accClass-ubicacion');

  function update_expiration_year() {
    // Fija el año de expiracion a la fecha de hoy + 5 o 30 años
    if ($accClass.val().match(/estudiante/)) {
      $dateExpirationYear.val(year + 5);
    } else {
      $dateExpirationYear.val(year + 30);
    }
  }

  function update_uid() {
    // Desactiva el campo uid si el usuario no es dependencia
    if ($accClass.val().match(/dependencia/)) {
      $uid.attr('disabled', false);
    } else {
      $uid.attr('disabled', true);
    }
  }

  function update_accClass() {
      // Actualiza el campo accClass. accClass contiene la clase de usuario
      // en el ldap, pero en el formulario depende de accClassTipo y 
      // accClassUbicacion
      var accClass = $accClassTipo.val() + ',' + $accClassUbicacion.val()
      $accClass.val(accClass)
  }

  function update_accClass_uid_and_expiration() {
      var accClass = $accClassTipo.val() + ',' + $accClassUbicacion.val()
      $accClass.val(accClass)
      update_uid();
      update_expiration_year();
  }

  function accClass_on_change() {
      update_uid();
      update_expiration_year();
  }

  function init_new_page() {
      // Inicializa los eventos en la pagina new
      $accClassTipo.change(update_accClass_uid_and_expiration);
      $accClassUbicacion.change(update_accClass_uid_and_expiration);
      update_uid();
      update_accClass();
      $dateCreationDay.val(day);  
      $dateExpirationDay.val(day);
      $dateCreationMonth.val(month);  
      $dateExpirationMonth.val(month);
      $dateCreationYear.val(year);
      $dateExpirationYear.val(year + 5);
  }

  function init_accClass_proxies() {
      // Inicializa los campos accClassTipo y accClassUbicacion al valor
      // de accClass
      var accClass = $accClass.val();
      var split = accClass.split(',');
      var accClassTipo = split.shift();
      var accClassUbicacion = split.join(',');
      $accClassTipo.val(accClassTipo);
      $accClassUbicacion.val(accClassUbicacion);
  }

  function init_edit_page() {
      // Inicializa los eventos en la pagina modify
      init_accClass_proxies();
      $accClassTipo.change(update_accClass);
      $accClassUbicacion.change(update_accClass);
  }

  return {
      init_new_page: init_new_page,
      init_edit_page: init_edit_page
  }
}

jq(function() {
  usermanager = usermanager_module();
  if (jq('#usermanager-add-form').length === 1) {
      usermanager.init_new_page();
  }
  if (jq('#usermanager-edit-form').length ===1) {
      usermanager.init_edit_page();
  }
});
