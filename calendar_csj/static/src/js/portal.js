$(function () {
    $(".appointment_portal_edit_form input[name='calendar_datetime']").datetimepicker({
      inline: true,
      format : 'YYYY-MM-DD HH:mm',
      sideBySide: true
    });
    $(".appointment_portal_reschedule_form input[name='calendar_datetime']").datetimepicker({
      inline: true,
      format : 'YYYY-MM-DD HH:mm',
      sideBySide: true
    });
    $( ".appointment_portal_edit_form input[name='request_date']").datepicker({
      dateFormat : 'yy-mm-dd',
    });
    $( ".appointment_portal_edit_form input[name='appointment_date']").datepicker({
      dateFormat : 'yy-mm-dd',
    });
    $( ".appointment_portal_edit_form input[name='end_date']").datepicker({
      dateFormat : 'yy-mm-dd',
    });

    $( ".appointment_portal_edit_form input[name='end_hour']").timepicker({
      timeFormat: 'h:mm p',
      interval: 60,
      minTime: '10',
      maxTime: '6:00pm',
      defaultTime: '11',
      startTime: '10:00',
      dynamic: false,
      dropdown: true,
      scrollbar: true
  });

});

odoo.define('calendar_csj.calendar_portal_csj', function(require) {
    "use strict";

    var ajax = require('web.ajax');
  	var core = require('web.core');
  	var qweb = core.qweb;
    var _t = core._t;
    var ajax = require('web.ajax');
    var time = require('web.time');
    var Dialog = require('web.Dialog');


    var appointment_state =  $("#appointment_state").text();
    var appointment_id = $("#appointment_id").text();
    $("#appointment_state").hide();
    $("#appointment_id").hide();
    function removeActiveDisabledButton(){
      $("#state_draft_btn").removeClass('active');
      $("#state_open_btn").removeClass('active');
      $("#state_realized_btn").removeClass('active');
      $("#state_unrealized_btn").removeClass('active');
      $("#state_postpone_btn").removeClass('active');
      $("#state_assist_postpone_btn").removeClass('active');
      $("#state_assist_cancel_btn").removeClass('active');
      $("#state_cancel_btn").removeClass('active');
      $("#state_draft_btn_btn").removeClass('disabled');
      $("#state_open_btn").removeClass('disabled');
      $("#state_realized_btn").removeClass('disabled');
      $("#state_unrealized_btn").removeClass('disabled');
      $("#state_postpone_btn").removeClass('disabled');
      $("#state_assist_postpone_btn").removeClass('disabled');
      $("#state_cancel_btn").removeClass('disabled');
      $("#state_assist_cancel_btn").removeClass('disabled');
    }
    function addDisabledButton(){
      $("#state_draft_btn").removeClass('active');
      $("#state_open_btn").removeClass('active');
      $("#state_realized_btn").removeClass('active');
      $("#state_unrealized_btn").removeClass('active');
      $("#state_postpone_btn").removeClass('active');
      $("#state_assist_postpone_btn").removeClass('active');
      $("#state_assist_cancel_btn").removeClass('active');
      $("#state_draft_btn").addClass('disabled');
      $("#state_open_btn").addClass('disabled');
      $("#state_realized_btn").addClass('disabled');
      $("#state_unrealized_btn").addClass('disabled');
      $("#state_postpone_btn").addClass('disabled');
      $("#state_assist_postpone_btn").addClass('disabled');
      $("#state_assist_cancel_btn").addClass('disabled');
    }
    if (appointment_state == 'open'){
      removeActiveDisabledButton();
      $("#state_open_btn").addClass('active');
    } else if (appointment_state == 'draft'){
      removeActiveDisabledButton();
      $("#state_draft_btn").addClass('active');
    } else if (appointment_state == 'realized'){
      removeActiveDisabledButton();
      $("#state_realized_btn").addClass('active');
    } else if (appointment_state == 'unrealized'){
      removeActiveDisabledButton();
      $("#state_unrealized_btn").addClass('active');
    } else if (appointment_state == 'postpone'){
      removeActiveDisabledButton();
      $("#state_postpone_btn").addClass('active');
    } else if (appointment_state == 'postpone'){
      removeActiveDisabledButton();
      $("#state_assist_postpone_btn").addClass('active');
    } else if (appointment_state == 'assist_cancel'){
      removeActiveDisabledButton();
      $("#state_assist_cancel_btn").addClass('active');
    } else if (appointment_state == 'cancel'){
      addDisabledButton();
      $("#state_cancel_btn").addClass('active');
    }
    $("#state_open_btn").on('click', function(e){
      url = '/my/appointment/' + appointment_id + '/update/state/cancel';
      window.location.href = url;
    });


    var type = $(".appointment_portal_edit_form input[name='hidden_type']").val();
    var request_type = $(".appointment_portal_edit_form input[name='hidden_request_type']").val();
    //$(".appointment_portal_edit_form input[name='request_type']").children("option:selected")[0].getAttribute('data') || '';
    $(".appointment_portal_edit_form input[name='request_type']").val(type)
    $(".appointment_portal_edit_form input[name='request_type']").val(request_type)


    $("#state_cancel_btn").on('click', function(e){
      Dialog.confirm(this, 'El agendamiento se cancelará y un correo electrónico será enviado a los invitados notificando esta cancelación', {
          confirm_callback: function() {
            url = '/my/appointment/' + appointment_id + '/update/state/cancel';
            window.location.href = url;
          },
          title: _t('Cancelción de Agendamiento'),
      });
    });

    $("#state_realized_btn").on('click', function(e){
      Dialog.confirm(this, 'El agendamiento será marcado como realizado y se actualizará la fecha y usuario de cierre', {
          confirm_callback: function() {
            url = '/my/appointment/' + appointment_id + '/update/state/realized';
            window.location.href = url;
          },
          title: _t('Confirmación de Realización de Agendamiento'),
      });
    });

    $("#state_unrealized_btn").on('click', function(e){
      Dialog.confirm(this, 'El agendamiento será marcado como NO realizado y se actualizará la fecha y usuario de cierre', {
          confirm_callback: function() {
            url = '/my/appointment/' + appointment_id + '/update/state/unrealized';
            window.location.href = url;
          },
          title: _t('Confirmación de NO Realización de Agendamiento'),
      });
    });

    $("#state_postpone_btn").on('click', function(e){
      Dialog.confirm(this, 'El agendamiento será marcado como Pospuesto y se actualizará la fecha y usuario de cierre', {
          confirm_callback: function() {
            url = '/my/appointment/' + appointment_id + '/update/state/postpone';
            window.location.href = url;
          },
          title: _t('Confirmación para posponer el Agendamiento'),
      });
    });

    $("#state_assist_postpone_btn").on('click', function(e){
      Dialog.confirm(this, 'El agendamiento será marcado como Pospuesto y se actualizará la fecha y usuario de cierre', {
          confirm_callback: function() {
            url = '/my/appointment/' + appointment_id + '/update/state/assist_postpone';
            window.location.href = url;
          },
          title: _t('Confirmación para posponer el Agendamiento'),
      });
    });

    $("#state_assist_cancel_btn").on('click', function(e){
      Dialog.confirm(this, 'El agendamiento será marcado como Pospuesto y se actualizará la fecha y usuario de cierre', {
          confirm_callback: function() {
            url = '/my/appointment/' + appointment_id + '/update/state/assist_cancel';
            window.location.href = url;
          },
          title: _t('Confirmación para posponer el Agendamiento'),
      });
    });


    $(".portal_appointment_edit").on('click', function(e){
      url = '/my/appointment/' + appointment_id + '/update/all';
      window.location.href = url;
    });

    $(".portal_appointment_edit_cancel").on('click', function(e){
      var appointment_id = $(".appointment_portal_edit_form input[name='appointment_id']").val();
      url = '/my/appointment/' + appointment_id;
      window.location.href = url;
    });


    $(".portal_appointment_reschedule").on('click', function(e){
      url = '/my/appointment/' + appointment_id + '/update/reschedule';
      window.location.href = url;
    });

    $(".portal_appointment_reschedule_cancel").on('click', function(e){
      var appointment_id = $(".appointment_portal_reschedule_form input[name='appointment_id']").val();
      url = '/my/appointment/' + appointment_id;
      window.location.href = url;
    });


    $(".portal_appointment_judged_change").on('click', function(e){
      url = '/my/appointment/' + appointment_id + '/update/judged';
      window.location.href = url;
    });

    $(".portal_appointment_judged_change_cancel").on('click', function(e){
      var appointment_id = $(".appointment_portal_judged_change_form input[name='appointment_id']").val();
      url = '/my/appointment/' + appointment_id;
      window.location.href = url;
    });




    $(".portal_appointment_save").on('click', function(e){

      var calendar_datetime = $(".appointment_portal_edit_form input[name='calendar_datetime']").val();
      if (calendar_datetime === '' || calendar_datetime === null || calendar_datetime === 'undefined'){
        Dialog.alert(this, 'Por favor selecione una fecha de realización!');
        return false;
      };
      $(".appointment_portal_edit_form").submit();
    });



    $(".portal_appointment_reschedule_save").on('click', function(e){

      var calendar_datetime = $(".appointment_portal_reschedule_form input[name='calendar_datetime']").val();
      if (calendar_datetime === '' || calendar_datetime === null || calendar_datetime === 'undefined'){
        Dialog.alert(this, 'Por favor selecione una fecha de realización!');
        return false;
      };
      $(".appointment_portal_reschedule_form").submit();
    });

});
