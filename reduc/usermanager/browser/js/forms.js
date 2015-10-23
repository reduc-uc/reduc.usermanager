// Form related js for reduc.usermanager
//
define([
  'jquery',
], function($) {
  // Inicializa los campos en el formulario new
  var today = new Date();
  var day = today.getDate();
  var month = today.getMonth();
  var year = today.getFullYear();

  var $uid = $('#form-widgets-uid');
  var $dateCreationDay = $('#form-widgets-dateCreation-day');
  var $dateExpirationDay = $('#form-widgets-dateExpiration-day');
  var $dateCreationMonth = $('#form-widgets-dateCreation-month');
  var $dateExpirationMonth = $('#form-widgets-dateExpiration-month');
  var $dateCreationYear = $('#form-widgets-dateCreation-year');
  var $dateExpirationYear = $('#form-widgets-dateExpiration-year');
  var $accClass = $('#form-widgets-accClass');
  var $accClassTipo = $('#form-widgets-accClass-tipo');
  var $accClassUbicacion = $('#form-widgets-accClass-ubicacion');

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
      var accClass = $accClassTipo.val() + ',' + $accClassUbicacion.val();
      $accClass.val(accClass)
  }

  function update_accClass_uid_and_expiration() {
      update_accClass();
      update_uid();
      update_expiration_year();
  }

  function accClass_on_change() {
      // evento en caso de cambio en accClass
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
      var accClassTipo = split.shift().toLowerCase();
      var accClassUbicacion = split.join(',').toLowerCase();
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
  };
});
