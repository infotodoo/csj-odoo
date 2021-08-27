$(function () {
    var dateNow = new Date();
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
    $(".date_time").datetimepicker({
      inline: true,
      format : 'YYYY-MM-DD HH:mm',
      sideBySide: true
    });
    $(".date_time_content").datetimepicker({
      inline: true,
      format : 'YYYY-MM-DD HH:mm',
      sideBySide: true,
      maxDate: new Date()
    });
    $( ".appointment_portal_edit_form input[name='request_date']").datepicker({
      dateFormat : 'yy-mm-dd',
      defaultDate:moment(dateNow),
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

  var dateNow = new Date();
  $(".o_portal_search_panel_csj input[name='date_begin']").datepicker({
    //inline: true,
    //format : 'YYYY-MM-DD',
    dateFormat : 'yy-mm-dd',
    //formatTime:'H:i',
    //defaultDate:moment(dateNow).hours(23).minutes(59),
    //sideBySide: false
  });
    
  $(".o_portal_search_panel_csj input[name='date_end']").datepicker({
    //inline: true,
    //format : 'YYYY-MM-DD',
    dateFormat : 'yy-mm-dd',
    formatTime:'H:i',
    //defaultDate:moment(dateNow).hours(23).minutes(59),
    //sideBySide: false
  });

    let url = window.location.href;
    var url_words = ["/public", "/my/appointments"];
    var url_public = new RegExp(url_words.join('|')).test(url);
    if (url_public == true) {
        $(".container").css('max-width', '1920px');
    }

    var rest_form_ctl = $(".o_website_recording_add_content_form input[name='rest_form_ctl']").val();
    if (rest_form_ctl === ''){
        $('.rest_form_ctl').hide();
    }
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
            'click .download_appointment_report': '_onSearchDownloadClick',
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
            search['time_begin'] = this.$('input[name="time_begin"]').val();
            search['date_end'] = this.$('input[name="date_end"]').val();
            search['time_end'] = this.$('input[name="time_end"]').val();
            search['export'] = this.$('input[name="export"]').val();
            window.location.search = $.param(search);
        },
        _onSearchSubmitClick: function () {
            this.$("input[name='export']").val("false");
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
        _onSearchDownloadClick: function (ev) {
            ev.preventDefault();

                this.$("input[name='export']").val("true");
                this._search();
                /*
                Dialog.confirm(this, 'Máximo se descargarán 20.000 registros', {
                    confirm_callback: function() {

                      //var url = '/public';
                      //window.location.href = url;

                      },
                      title: _t('Descargar Reporte en Excel'),
                  });
                */

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
      Dialog.confirm(this, 'El agendamiento será marcado como Duplicado', {
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


    $(".treescroll2").scroll(function(){
        $(".treescroll1")
            .scrollLeft($(".treescroll2").scrollLeft());
    });
    $(".treescroll1").scroll(function(){
        $(".treescroll2")
            .scrollLeft($(".treescroll1").scrollLeft());
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

odoo.define('calendar_csj.calendar_portal_csj_recording_add_content', function(require) {
    "use strict";

    var ajax = require('web.ajax');
	var core = require('web.core');
    var recordingJudgeAnimation = require('website.content.snippets.animation');



    /*
    $("#button_submit_recording_add_content").on('click', function(e){
        var core = require('web.core');
        var rpc = require('web.rpc');
        var Dialog = require('web.Dialog');
        //var date_time = $(".o_website_appointment_form input[name='date_time']").val();
        //var duration = $(".o_website_appointment_form select[name='duration']").val();
        var search_city = $(".o_website_recording_add_content_form input[name='search_city']").val();
        var calendar_appointment_type_id = $(".o_website_recording_add_content_form input[name='calendar_appointment_type_id']").val();

        if (search_city === '' || search_city === null || search_city === 'undefined'){
            Dialog.alert(this, 'Por favor selecione una ciudad!');
            return false;
        };
        if (calendar_appointment_type_id === '' || calendar_appointment_type_id === null || calendar_appointment_type_id === undefined || calendar_appointment_type_id === '1'){
            Dialog.alert(this, 'Por favor seleccione un Juzgado!');
            return false;
        };

        $(".o_website_recording_add_content_form").submit();
        return false;
    });
    */




    $(".add-recording-process-number-btn").on('click', function(e){
        var core = require('web.core');
        var rpc = require('web.rpc');
        var Dialog = require('web.Dialog');
        var process_number = $(".o_website_recording_add_content_form input[name='process_number']").val();

        function hide_process_void_alert(){
            $('.process_void').addClass('d-none');
            $('.process_void').removeClass('d-print-inline');
            $('.process_void').hide();
        }
        function hide_process_none_alert(){
            $('.process_none').addClass('d-none');
            $('.process_none').removeClass('d-print-inline');
            $('.process_none').hide();
        }
        function hide_process_ok_alert(){
            $('.process_ok').addClass('d-none');
            $('.process_ok').removeClass('d-print-inline');
            $('.process_ok').hide();
        }
        function hide_rest_form(){
            $('.rest_form_ctl').addClass('d-none');
            $('.rest_form_ctl').removeClass('d-print-inline');
            $('.rest_form_ctl').show();
        }
        function show_process_void_alert(){
            $('.process_void').removeClass('d-none');
            $('.process_void').addClass('d-print-inline');
            $('.process_void').show();
            hide_process_none_alert();
            hide_process_ok_alert();
            hide_rest_form();
        }
        function show_process_none_alert(){
            $('.process_none').removeClass('d-none');
            $('.process_none').addClass('d-print-inline');
            $('.process_none').show();
            hide_process_void_alert();
            hide_process_ok_alert();
        }
        function show_process_ok_alert(){
            $('.process_ok').removeClass('d-none');
            $('.process_ok').addClass('d-print-inline');
            $('.process_ok').show();
            hide_process_void_alert();
            hide_process_none_alert();
        }
        function show_rest_form(){
            $('.rest_form_ctl').removeClass('d-none');
            $('.rest_form_ctl').addClass('d-print-inline');
            $('.rest_form_ctl').show();
            hide_process_void_alert();
        }

        if (process_number === '' || process_number === null || process_number === 'undefined'){
            //Dialog.alert(this, 'Digite un número de proceso!');
            show_process_void_alert();
            return false;
        }
        rpc.query({
            model: 'process.process',
            method: 'fetch_process_exist',
            args: [process_number],
        }).then(function (data)
        {
            if (data[0] === true){
                if (data[1] !== false){
                    $(".o_website_recording_add_content_form input[name='search_city']").val(data[1]);
                    $(".o_website_recording_add_content_form input[name='city_id']").val(data[2]);
                    $(".city-container .typeahead__container").addClass('cancel');
                }
                if (data[2] !== false){
                    $(".o_website_recording_add_content_form input[name='search_appointment']").val(data[3]);
                    $(".appointment-container .typeahead__container").addClass('cancel');
                }
                if (data[3] !== false){
                    $(".o_website_recording_add_content_form input[name='tag_number']").val(data[4]);
                    //$(".appointment-container .typeahead__container").addClass('cancel');
                }
                /*
                if (data[3] !== false){
                    $(".o_website_recording_add_content_form input[name='search_judge']").val(data[3]);
                    $(".judge-container .typeahead__container").addClass('cancel');
                }*/
              hide_process_none_alert();
              show_process_ok_alert();
              show_rest_form();
            //} else if (data[0] === false || data[0] === undefined || data[0] === '' || data[0] === null) {
            } else {
              //Dialog.alert(this, 'Este número de proceso no existe aún. Continue registrando su información');
                if (data[1] === 'failed length'){
                    Dialog.alert(this, 'Longitud del número de proceso no valida, debe contener 23 digitos!');
                    return false;
                }
                if (data[1] === 'failed composition'){
                    Dialog.alert(this, 'Número de proceso mal formado!');
                    return false;
                }
                hide_process_ok_alert();
                hide_process_void_alert();
                show_process_none_alert();
                show_rest_form();
                rpc.query({
                    model: 'process.process',
                    method: 'fetch_scheduler_default_data',
                    //args: [process_number],
                }).then(function (data)
                {
                    //alert(data)
                    if (data[0] === true){
                        if (data[1] !== false){
                            $(".o_website_recording_add_content_form input[name='search_city']").val(data[1]);
                            $(".o_website_recording_add_content_form input[name='city_id']").val(data[2]);
                            $(".city-container .typeahead__container").addClass('cancel');
                        }
                        if (data[2] !== false){
                            $(".o_website_recording_add_content_form input[name='search_appointment']").val(data[3]);
                            $(".appointment-container .typeahead__container").addClass('cancel');
                        }
                    }

                });
            }
        });
    });

    $(".o_website_recording_add_content_form input[name='prepareFile']").on('change', function(e){
        let Dialog = require('web.Dialog');
        var fileInput = $(".o_website_recording_add_content_form input[name='prepareFile']");
        var filePath = fileInput.val();
        var allowedExtensions = /(\.avi|\.mp3|\.mp4|\.mkv|\.flv|\.mov|\.wmv|\.divx|\.h.264|\.wma)$/i;
        if (!allowedExtensions.exec(filePath)) {
            Dialog.alert(this, 'Extensión de archivo no valido!, por favor seleccione un video');
            fileInput.val('');
            return false;
        }
    });

    $(".button_submit_recording_add_content").on('click', function(e){
        let core = require('web.core');
        let rpc = require('web.rpc');
        let Dialog = require('web.Dialog');
        let process_number = $(".o_website_recording_add_content_form input[name='process_number']").val();
        let city_id = $(".o_website_recording_add_content_form input[name='city_id']").val();
        let search_appointment = $(".o_website_recording_add_content_form input[name='search_appointment']").val();
        let calendar_appointment_type_id = $(".o_website_recording_add_content_form input[name='calendar_appointment_type_id']").val();
        let process_datetime = $(".o_website_recording_add_content_form input[name='date_time_content']").val();
        let judge_name = $(".o_website_recording_add_content_form input[name='judge_name']").val();
        let prepare_file = $(".o_website_recording_add_content_form input[name='prepareFile']").val();
        let tag_number = $(".o_website_recording_add_content_form input[name='tag_number']").val();
        let request_type = $(".o_website_recording_add_content_form select[name='request_type'] option:selected").text();
        let judged_name = $(".o_website_recording_add_content_form input[name='judged_name']").val();

        //prepare_file = prepare_file.substring(8);



        if (process_number === '' || process_number === null || process_number === 'undefined'){
             Dialog.alert(this, 'Por favor registre un número de proceso!');
            return false;
        }

        if (city_id === '' || city_id === null || city_id === undefined){
            Dialog.alert(this, 'Por favor selecione una ciudad!');
            return false;
        };
        if (search_appointment === '' || search_appointment === null || search_appointment === undefined || search_appointment === '1'){
            Dialog.alert(this, 'Por favor seleccione un Juzgado!');
            return false;
        };

        if (process_datetime === '' || process_datetime === null || process_datetime === undefined){
            Dialog.alert(this, 'Por favor registre una fecha y hora de realización!');
            return false;
        };

        if (judge_name === '' || judge_name === null || judge_name === undefined){
            Dialog.alert(this, 'Por favor registre el nombre del Juez!');
            return false;
        };

        if (prepare_file === '' || prepare_file === null || prepare_file === undefined){
            Dialog.alert(this, 'Por favor selecione un archivo!');
            return false;
        };

        //$(".o_website_recording_add_content_form").submit();

        //alert('sdsdsds');
        //tag_number = 'asdasd';

        rpc.query({
            model: 'process.process',
            method: 'process_create_from_add_content',
            args: [process_number, city_id, calendar_appointment_type_id, judge_name, process_datetime, tag_number, request_type, prepare_file],
        }).then(function (data)
        {
            if (data[0] === true){
                //se creó o actualizó correctamente el proceso
                $(".o_website_recording_add_content_form input[name='process_number']").attr('readonly', true);
                $(".o_website_recording_add_content_form input[name='search_city']").attr('readonly', true);
                $(".o_website_recording_add_content_form input[name='calendar_appointment_type_id']").attr('readonly', true);
                $(".o_website_recording_add_content_form input[name='date_time_content']").attr('readonly', true);
                $(".o_website_recording_add_content_form input[name='judge_name']").attr('readonly', true);
                let process_number = $(".o_website_recording_add_content_form input[name='process_number']").val();
                //$(".mycloud_todoo_co_frame").show();
                //var url = 'http://181.57.153.122:8027/index.php/s/eSWsegnHWncagpP'
                //var url = 'http://181.57.153.122:8027/index.php/s/eSWsegnHWncagpP'
                var url = '/data/recordings/add/content/api?process_number=' + process_number + '&prepare_file=' + prepare_file;
                $(".button_submit_recording_add_content").prop('disabled', true);
                window.location.href = url;
                //window.open(url, '_blank', 'location=no,height=570,width=520,scrollbars=no,status=no');
            } else {
                Dialog.alert(this, data[1]);
                return false;
            }
        });
        return false;
    });


    $("#add_content_url").on('click', function(e){
        let url = 'http://51.222.114.252:8027/index.php/s/eSWsegnHWncagpP'
        window.open(url, '_blank', 'height=570,width=520,directories=0,titlebar=0,toolbar=0,location=0,status=0,menubar=0,scrollbars=no,resizable=no');
    });

    /*
    var calendar_appointment_type_id = $(".o_website_recording_add_content_form input[name='calendar_appointment_type_id']").val();
    //val .search-query-judge
    //alert(calendar_appointment_type_id);


    $('.search-query-judge').typeahead({source: []});



    $(".search-query-judge ul.typeahead.dropdown-menu").find('li.active').data(29179);

    */

    //$('.search-query-judge').val('sadfsdfsdf');



});
