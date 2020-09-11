$(function () {
  $("#container_datetime_filter").hide();
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
      timeFormat: 'H:mm',
      interval: 60,
      minTime: '0',
      maxTime: '8:00pm',
      defaultTime: '0',
      startTime: '0',
      dynamic: false,
      dropdown: true,
      scrollbar: true
  });

  $( "#date_begin").datepicker({
    dateFormat : 'yy-mm-dd',
  });

  $( "#date_end").datepicker({
    dateFormat : 'yy-mm-dd',
  });
  
  var dateNow = new Date();

  $(".o_portal_search_panel_csj input[name='date_begin']").datetimepicker({
    inline: true,
    format : 'YYYY-MM-DD HH:mm',
    formatTime:'H:i',
    defaultDate:moment(dateNow).hours(0).minutes(0),
    sideBySide: false,
  });
 
  $(".o_portal_search_panel_csj input[name='date_end']").datetimepicker({
    inline: true,
    format : 'YYYY-MM-DD HH:mm',
    formatTime:'H:i',
    defaultDate:moment(dateNow).hours(23).minutes(59),
    sideBySide: false
  });

  $(".o_portal_search_panel_csj input[name='date_begin']").val('')
  $(".o_portal_search_panel_csj input[name='date_end']").val('')


  $("#datetime_filter_icon").on('click', function(e){
    $("#container_datetime_filter").toggle();
  });

  //$("#container_datetime_filter").on('mouseleave', function(e){
  //  $("#container_datetime_filter").hide();
  //});

});

odoo.define('calendar_csj.calendar_portal_csj', function(require) {
    "use strict";

    var publicWidget = require('web.public.widget');


    publicWidget.registry.portalSearchPanelCSJ = publicWidget.Widget.extend({
        selector: '.o_portal_search_panel_csj',
        events: {
            'click .search-submit-csj': '_onSearchSubmitClick',
            'click .dropdown-item': '_onDropdownItemClick',
            'keyup input[name="search"]': '_onSearchInputKeyup',
        },
        start: function () {
            var def = this._super.apply(this, arguments);
            this._adaptSearchLabel(this.$('.dropdown-item.active'));
            return def;
        },
        _adaptSearchLabel: function (elem) {
            var $label = $(elem).clone();
            $label.find('span.nolabel').remove();
            this.$('input[name="search"]').attr('placeholder', $label.text().trim());
        },
        _search: function () {
            var search = $.deparam(window.location.search.substring(1));
            search['search_in'] = this.$('.dropdown-item.active').attr('href').replace('#', '');
            search['search'] = this.$('input[name="search"]').val();
            search['date_begin'] = this.$('input[name="date_begin"]').val();
            search['date_end'] = this.$('input[name="date_end"]').val();
            search['export'] = this.$('input[name="export"]:checked').val();
            window.location.search = $.param(search);
        },
        _onSearchSubmitClick: function () {
            this._search();
        },
        _onDropdownItemClick: function (ev) {
            ev.preventDefault();
            var $item = $(ev.currentTarget);
            $item.closest('.dropdown-menu').find('.dropdown-item').removeClass('active');
            $item.addClass('active');

            this._adaptSearchLabel(ev.currentTarget);
        },
        _onSearchInputKeyup: function (ev) {
            if (ev.keyCode === $.ui.keyCode.ENTER) {
                this._search();
            }
        },
    });


    var ajax = require('web.ajax');
  	var core = require('web.core');
  	var qweb = core.qweb;
    var _t = core._t;
    var ajax = require('web.ajax');
    var time = require('web.time');
    var Dialog = require('web.Dialog');
    var appointment_state =  $("#appointment_state").text();
    var appointment_id = $("#appointment_id").val();
    $("#appointment_state").hide();
    //$("#appointment_id").hide();
    function removeActiveDisabledButton(){
      $("#state_draft_btn").removeClass('active');
      $("#state_open_btn").removeClass('active');
      $("#state_realized_btn").removeClass('active');
      $("#state_unrealized_btn").removeClass('active');
      $("#state_postpone_btn").removeClass('active');
      $("#state_assist_postpone_btn").removeClass('active');
      $("#state_assist_cancel_btn").removeClass('active');
      $("#state_cancel_btn").removeClass('active');
      $("#state_draft_btn").removeClass('disabled');
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


    //$("#state_open_btn").on('click', function(e){
    //  var url = '/my/appointment/' + appointment_id + '/update/state/cancel';
    //  window.location.href = url;
    //});


    var type = $(".appointment_portal_edit_form input[name='hidden_type']").val();
    var request_type = $(".appointment_portal_edit_form input[name='hidden_request_type']").val();
    //$(".appointment_portal_edit_form input[name='request_type']").children("option:selected")[0].getAttribute('data') || '';
    $(".appointment_portal_edit_form input[name='request_type']").val(type)
    $(".appointment_portal_edit_form input[name='request_type']").val(request_type)


    $("#state_cancel_btn").on('click', function(e){
      Dialog.confirm(this, 'El agendamiento se cancelará y un correo electrónico será enviado a los invitados notificando esta cancelación', {
          confirm_callback: function() {
            var url = '/my/appointment/' + appointment_id + '/update/state/cancel';
            window.location.href = url;
          },
          title: _t('Cancelción de Agendamiento'),
      });
    });

    $("#state_realized_btn").on('click', function(e){
      Dialog.confirm(this, 'El agendamiento será marcado como realizado y se actualizará la fecha y usuario de cierre', {
          confirm_callback: function() {
            var url = '/my/appointment/' + appointment_id + '/update/state/realized';
            window.location.href = url;
          },
          title: _t('Confirmación de Realización de Agendamiento'),
      });
    });

    $("#state_unrealized_btn").on('click', function(e){
      Dialog.confirm(this, 'El agendamiento será marcado como NO realizado y se actualizará la fecha y usuario de cierre', {
          confirm_callback: function() {
            var url = '/my/appointment/' + appointment_id + '/update/state/unrealized';
            window.location.href = url;
          },
          title: _t('Confirmación de NO Realización de Agendamiento'),
      });
    });

    $("#state_postpone_btn").on('click', function(e){
      Dialog.confirm(this, 'El agendamiento será marcado como Pospuesto y se actualizará la fecha y usuario de cierre', {
          confirm_callback: function() {
            var url = '/my/appointment/' + appointment_id + '/update/state/postpone';
            window.location.href = url;
          },
          title: _t('Confirmación para posponer el Agendamiento'),
      });
    });

    $("#state_assist_postpone_btn").on('click', function(e){
      Dialog.confirm(this, 'El agendamiento será marcado como Pospuesto y se actualizará la fecha y usuario de cierre', {
          confirm_callback: function() {
            var url = '/my/appointment/' + appointment_id + '/update/state/assist_postpone';
            window.location.href = url;
          },
          title: _t('Confirmación para posponer el Agendamiento'),
      });
    });

    $("#state_assist_cancel_btn").on('click', function(e){
      Dialog.confirm(this, 'El agendamiento será marcado como Pospuesto y se actualizará la fecha y usuario de cierre', {
          confirm_callback: function() {
            var url = '/my/appointment/' + appointment_id + '/update/state/assist_cancel';
            window.location.href = url;
          },
          title: _t('Confirmación para posponer el Agendamiento'),
      });
    });
	
    $("#state_draft_btn").on('click', function(e){
      Dialog.confirm(this, 'El agendamiento será marcado erecomo Duplicado', {
          confirm_callback: function() {
            var url = '/my/appointment/' + appointment_id + '/update/state/draft';
            window.location.href = url;
          },
          title: _t('Confirmación para posponer el Agendamiento'),
      });
    });

    $(".portal_appointment_edit").on('click', function(e){
      var url = '/my/appointment/' + appointment_id + '/update/all';
      window.location.href = url;
    });

    $(".portal_appointment_edit_cancel").on('click', function(e){
      var appointment_id = $(".appointment_portal_edit_form input[name='appointment_id']").val();
      url = '/my/appointment/' + appointment_id;
      window.location.href = url;
    });


    $(".portal_appointment_reschedule").on('click', function(e){
      var url = '/my/appointment/' + appointment_id + '/update/reschedule';
      window.location.href = url;
    });

    $(".portal_appointment_reschedule_cancel").on('click', function(e){
      var appointment_id = $(".appointment_portal_reschedule_form input[name='appointment_id']").val();
      url = '/my/appointment/' + appointment_id;
      window.location.href = url;
    });


    $(".portal_appointment_judged_change").on('click', function(e){
      var url = '/my/appointment/' + appointment_id + '/update/judged';
      window.location.href = url;
    });

    $(".portal_appointment_judged_change_cancel").on('click', function(e){
      var appointment_id = $(".appointment_portal_judged_change_form input[name='appointment_id']").val();
      var url = '/my/appointment/' + appointment_id;
      window.location.href = url;
    });
	
    $(".portal_appointment_confirm_update").on('click', function(e){
      var url = '/my/appointment/' + appointment_id + '/update/state/open';
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

    $(".portal_appointment_judgedchange_save").on('click', function(e){
      var appointment_type = $(".appointment_portal_judged_change_form input[name='appointment_type']").val();
      if (appointment_type === '' || appointment_type === null || appointment_type === 'undefined'){
        Dialog.alert(this, 'Por favor selecione un Despacho!');
        return false;
      };
      $(".appointment_portal_judged_change_form").submit();
    });

});



odoo.define('calendar_csj.calendar_portal_csj_edit_judged', function(require) {
    "use strict";

	var ajax = require('web.ajax');
	var core = require('web.core');
	var sAnimation = require('website.content.snippets.animation');
	var sAnimation2 = require('website.content.snippets.animation');
	var sAnimation3 = require('website.content.snippets.animation');

	var qweb = core.qweb;
  var _t = core._t;
  var ajax = require('web.ajax');

  var dest = 0

	sAnimation.registry.OdooWebsitePortalSearchAppointment = sAnimation.Class.extend({
		selector: ".search-portal-query-appointment",
    //xmlDependencies: ['/calendar_csj/static/src/xml/calendar_csj_utils.xml'],
    autocompleteMinWidth: 300,
		start: function () {
		    var self = this;
        var previousSelectedCityID = $(".appointment_portal_judged_change_form input[name='city_id']").val();
        var url = '/search/suggestion';
        if (previousSelectedCityID){
          var url = '/search/suggestion/'.concat(previousSelectedCityID);
        }
		    this.$target.attr("autocomplete","off");
        this.$target.parent().addClass("typeahead__container");
        this.$target.typeahead({
        	minLength: 1,
		      maxItem: 15,
		      delay: 500,
		      order: "asc",
          cache: false,
          searchOnFocus: true,
		      hint: true,
		      accent: true,
          emptyTemplate: 'No results found "{{query}}"',
		      //display: ["id","cita"],
          display: ["cita"],
          template: '<span>' +
                      '<span>{{cita}}</span>' +
                      '</span>',
          source:{ appointment:{ url: [{ type : "GET", url : url, data : { query : "{{query}}"},},"data.cita"] },},
          callback: {
              onClickAfter: function (node, a, item, event) {
                var calendar_appointment_type_id = item['id'];
                $(".appointment_portal_judged_change_form input[name='appointment_type']").val(calendar_appointment_type_id);
              }
            }
        });
		},
		debug: true,
	});

});
