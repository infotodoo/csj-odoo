function isNumber(evt) {
    evt = (evt) ? evt : window.event;
    var charCode = (evt.which) ? evt.which : evt.keyCode;
    if ( (charCode > 31 && charCode < 48) || charCode > 57) {
        return false;
    }
    return true;
}

$( function() {
  $( "#request_date" ).datepicker({
    dateFormat : 'yy-mm-dd',
    maxDate: new Date(),
  });
//  $('#room_id option[name="Sala Audiencia Virtual"]').attr('selected','selected');

var $select = $('#room_id');
$select.children().filter(function(){ 
  return this.text == "Sala Audiencia Virtual";
  }).prop('selected', true);

});


function convertNumToTime(number) {
    // Check sign of given number
    var sign = (number >= 0) ? 1 : -1;
    // Set positive value of number of sign negative
    number = number * sign;
    // Separate the int from the decimal part
    var hour = Math.floor(number);
    var decpart = number - hour;
    var min = 1 / 60;
    // Round to nearest minute
    decpart = min * Math.round(decpart / min);
    var minute = Math.floor(decpart * 60) + '';
    // Add padding if need
    if (minute.length < 2) {
    minute = '0' + minute;
    }
    // Add Sign in final result
    sign = sign == 1 ? '' : '-';
    // Concate hours and minutes
    time = sign + hour + ':' + minute;
    return time;
}

//$('#calendar_time').val(convertNumToTime(appointment.calendar_time));

odoo.define('calendar_csj.select_appointment_guest_csj', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var time = require('web.time');
var guest = 0;

publicWidget.registry.websiteGuestSelect = publicWidget.Widget.extend({
    selector: '.guest_add_form',
    events: {
        'click .btn-guest_add': '_onGuestAddIconClick',
    },
    _onGuestAddIconClick: function (ev) {
      guest++;
      var objTo = document.getElementById('guest_fields')
      var divguestlist = document.createElement("div");
       divguestlist.setAttribute("class", "form-group removeclass"+guest);
       var rdiv = 'guest_remove_form'+guest;
       var guestSelectedName = $(".appointment_submit_form input[id='nameguest']").val();
       var guestSelectedEmail = $(".appointment_submit_form input[id='emailguest']").val();
       $(".appointment_submit_form input[id='nameguest']").val('');
       $(".appointment_submit_form input[id='emailguest']").val('');
       divguestlist.innerHTML = '<div class="row guest_remove_form' + guest + '" style="width:100%"><div class="col-md-5"><input type="char" class="form-control  text-uppercase" name="nameguest' + guest + '" value="' + guestSelectedName + '"/></div><div class="col-md-5"><input type="email" class="form-control" name="emailguest' + guest + '" value="' + guestSelectedEmail + '"/></div><div class="col-md-2"><button class="btn btn-danger fa fa-remove btn-guest_remove" onclick="remove_guest_fields('+ guest +');" type="button"></button></div></div><div class="clear"></div>';
       objTo.appendChild(divguestlist)
       var guestSelectedCont = $(".appointment_submit_form input[name='guestcont']").val();
       $(".appointment_submit_form input[name='guestcont']").val(parseInt(guestSelectedCont)+1);
       $("#nameguest").focus();
    },
});
});


odoo.define('calendar_csj.select_appointment_type_csj', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var time = require('web.time');
var rpc = require('web.rpc');
//$('#request_date').datetimepicker({inline: true,format: 'YYYY-MM-DD',sideBySide: true,});

$("#button_submit_appointment").on('click', function(e){
  var core = require('web.core');
  var rpc = require('web.rpc');
  var Dialog = require('web.Dialog');
  var date_time = $(".o_website_appointment_form input[name='date_time']").val();
  var duration = $(".o_website_appointment_form select[name='duration']").val();
  var search_city = $(".o_website_appointment_form input[name='search_city']").val();
  var calendar_appointment_type_id = $(".o_website_appointment_form input[name='calendar_appointment_type_id']").val();

  if (search_city === '' || search_city === null || search_city === 'undefined'){
    Dialog.alert(this, 'Por favor selecione una ciudad!');
    return false;
  };
  if (calendar_appointment_type_id === '' || calendar_appointment_type_id === null || calendar_appointment_type_id === 'undefined' || calendar_appointment_type_id === '1'){
    Dialog.alert(this, 'Por favor seleccione un Juzgado!');
    return false;
  };
  if (date_time === '' || date_time === null || date_time === 'undefined'){
    Dialog.alert(this, 'Por favor registre una fecha correcta!');
    return false;
  };

  $("#button_submit_appointment").prop('disabled', true);
  rpc.query({
    model: 'calendar.appointment',
    method: 'fetch_calendar_verify_availability',
    args: [this, calendar_appointment_type_id, date_time, duration],
  }).then(function (data)
  {
    if (data === true){
      $(".o_website_appointment_form").submit();
      return true;
    } else if (data === false) {
      Dialog.alert(this, 'Ya existe un Agendamiento programado para esta misma Fecha y Hora, consulte la Agenda y seleccione un espacio de tiempo diferente!');
      $("#button_submit_appointment").prop('disabled', false);
      return false;
    }
    // unespect event fetch, process restart is necessary
    $("#button_submit_appointment").prop('disabled', true);
    return false;
  });
  return false;
});;


$("#button_submit_confirm_appointment").on('click', function(e){
  var core = require('web.core');
  var rpc = require('web.rpc');
  var Dialog = require('web.Dialog');
  var phone = $(".appointment_submit_form input[name='phone']").val();
  var email = $(".appointment_submit_form input[name='email']").val();
  var types = $(".appointment_submit_form input[name='types']").val();
  var appointment_type = $(".appointment_submit_form input[name='appointment_type']").val();
  var datetime = $(".appointment_submit_form input[name='datetime']").val();
  var duration = $(".appointment_submit_form input[name='duration']").val();
  var request_date = $(".appointment_submit_form input[name='request_date']").val();
  var process_number = $(".appointment_submit_form input[name='process_number']").val();
  var destinationcont = $(".appointment_submit_form input[name='destinationcont']").val();
  var mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
  var res = email.split("@");

  if (request_date === '' || request_date === null || request_date === 'undefined'){
    Dialog.alert(this, 'Por favor registre la fecha de solicitud!');
    return false;
  };
  if (phone === '' || phone === null || phone === 'undefined'){
    Dialog.alert(this, 'Por favor registre un número de teléfono!');
    return false;
  };
  if (!phone.match(/^-{0,1}\d+$/)){
    Dialog.alert(this, 'Por favor registre un número de teléfono sin caracteres, solo numérico!');
    return false;
  };
  if (types == 'Audiencia' && process_number.length != 23){
    Dialog.alert(this, 'El tipo de Agendamiento es "Audiencia", por favor registre un número valido, debe tener 23 caracteres!');
    return false;
  };
  if (phone.length > 10 || phone.length < 7){
    Dialog.alert(this, 'Por favor registre un número telefónico valido entre 7 y 10 digitos!');
    return false;
  };
  if (res[1] != 'cendoj.ramajudicial.gov.co' && res[1] != 'cortesuprema.ramajudicial.gov.co' && res[1] != 'consejoestado.ramajudicial.gov.co' && res[1] != 'consejosuperior.ramajudicial.gov.co' && res[1] != 'deaj.ramajudicial.gov.co' && res[1] != 'fiscalia.gov.co' && res[1] != 'axede.com.co' && res[1] != 'corteconstitucional.gov.co'){
    Dialog.alert(this, "Por favor registre un correo valido. Estos son los dominios autorizados:\ncendoj.ramajudicial.gov.co\ncortesuprema.ramajudicial.gov.co\nconsejoestado.ramajudicial.gov.co\nconsejosuperior.ramajudicial.gov.co\ndeaj.ramajudicial.gov.co\nfiscalia.gov.co\naxede.com.co\ncorteconstitucional.gov.co");
    return false;
  };
  if (destinationcont < 2){
    Dialog.alert(this, 'Por favor seleccione al menos un Destino!');
    return false;
  };
  if (types == 'Audiencia' && process_number.length != 23){
    Dialog.alert(this, 'El tipo de Agendamiento es "Audiencia", por favor registre un número valido, debe tener 23 caracteres!');
    return false;
  };
  $(".appointment_submit_form input[name='types']").val().replace(/[^A-Z0-9]/ig, "");
  $("#button_submit_confirm_appointment").prop('disabled', true);
  rpc.query({
    model: 'calendar.appointment',
    method: 'fetch_calendar_verify_availability',
    args: [this, appointment_type, datetime, duration],
  }).then(function (data)
  {
    if (data === true){
      $(".appointment_submit_form").submit();
      return false;
    } else if (data === false) {
      Dialog.alert(this, 'Ya existe un Agendamiento programado para esta misma Fecha y Hora, consulte la Agenda, inicie el proceso de nuevo y seleccione un espacio de tiempo diferente!');
      $("#button_submit_confirm_appointment").prop('disabled', false);
      return false;
    }
    // unespect event fetch, process restart is necessary
    $("#button_submit_confirm_appointment").prop('disabled', true);
    return false;
  });
  return false;
});

// fix date to calc correct minDate in datetimepicker widget
var oldDateObj = new Date();
var newDateObj = new Date();
newDateObj.setTime(oldDateObj.getTime() - (90 * 24 * 60 * 60 * 1000));

publicWidget.registry.websiteAppointmentSelect = publicWidget.Widget.extend({
    selector: '.o_website_calendar_appointment',
    events: {
      'click div.input-group span.fa-calendar': '_onCalendarIconClick',
      'focus div.input-group input.date_time': '_onCalendarIconFocus',
    },
    _onCalendarIconFocus: function (ev) {
      $('.date_time').datetimepicker({
        format : 'YYYY-MM-DD HH:mm',
        formatTime:'H:i',
        step: 60,
        viewMode: 'months',
        minDate: newDateObj,
        inline: true,
        dayViewHeaderFormat: 'YYYY-MM',
        sideBySide: true,
        //daysOfWeekDisabled: [0, 6],
        lang:'es',
        icons: {
          time: 'fa fa-clock-o',
          date: 'fa fa-calendar',
          up: 'fa fa-chevron-up',
          down: 'fa fa-chevron-down',
        },
        i18n:{
          es:{
           months:[
            'Enero','Febrero','Marzo','Abril',
            'Mayo','Junio','Julio','Agosto',
            'Septiembre','Octubre','Noviembre','Diciembre',
           ],
           dayOfWeek:[
            "Lun", "Mar", "Mie", "Jue",
            "Vie", "Sáb", "Dom",
           ]
          }
        },
      });
      $(".o_website_appointment_form input[name='date_time']").attr('readonly', 'True');
    },
    _onCalendarIconClick: function (ev) {
      /*
      $('.date_time').datetimepicker({
        format : 'YYYY-MM-DD HH:mm',
        formatTime:'H:i',
        step: 60,
        viewMode: 'months',
        minDate: newDateObj,
        inline: true,
        dayViewHeaderFormat: 'YYYY-MM',
        sideBySide: true,
        //daysOfWeekDisabled: [0, 6],
        lang:'es',
        icons: {
          time: 'fa fa-clock-o',
          date: 'fa fa-calendar',
          up: 'fa fa-chevron-up',
          down: 'fa fa-chevron-down',
        },
        i18n:{
          es:{
           months:[
            'Enero','Febrero','Marzo','Abril',
            'Mayo','Junio','Julio','Agosto',
            'Septiembre','Octubre','Noviembre','Diciembre',
           ],
           dayOfWeek:[
            "Lun", "Mar", "Mie", "Jue",
            "Vie", "Sáb", "Dom",
           ]
          }
        },
      });
      $(".o_website_appointment_form input[name='date_time']").attr('readonly', 'True');
      */
    },
});



});

odoo.define('calendar_csj.calendar_csj', function(require) {
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

  sAnimation.registry.OdooWebsiteSearchCity = sAnimation.Class.extend({
    selector: ".search-query-city",
    autocompleteMinWidth: 300,
    init: function () {
      console.log('init: search_city');
    },
    start: function () {
        var calendar_appointment_type_id = $(".appointment_submit_form input[name='calendar_appointment_type_id']").val();
        $('.search-query-appointment').typeahead({source: []});
        var self = this;
        var previousSelectedCityID = $(".o_website_appointment_form input[name='city_id']").val();
        this.$target.attr("autocomplete","off");
        this.$target.parent().addClass("typeahead__container");
        this.$target.typeahead({
          minLength: 1,
          maxItem: 15,
          delay: 500,
          order: "asc",
          cache: false,
          autoFocus:true,
          hint: true,
          accent: true,
          mustSelectItem: true,
          item: 5334,
          //display: ["id","city"],
          display: ["city"],
          template: '<span>' +
                      '<span>{{city}}</span>' +
                      '</span>',
          source:{ city:{ url: [{ type : "GET", url : "/search/suggestion_city", data : { query : "{{query}}"},},"data.cities"] },},
          callback: {
              onClickAfter: function (node, a, item, event) {
                event.preventDefault;
                $('.search-query-city-id').val(item.id);
                //var previousSelectedCityID = $(".o_website_appointment_form input[name='city_id']").val();
                var url = '/search/suggestion';
                if (item.id){
                  var url = '/search/suggestion/'.concat(item.id);
                }
                $('.search-query-appointment').typeahead({source: []});
                $('.search-query-appointment').typeahead({
                    minLength: 1,
                    maxItem: 15,
                    delay: 500,
                    order: "asc",
                    cache: false,
                    searchOnFocus: true,
                    hint: true,
                    accent: true,
                    display: ["cita"],
                    template: '<span>' +
                                '<span>{{cita}}</span>' +
                                '</span>',
                    source:{ appointment:{ url: [{ type : "GET", url : url, data : { query : "{{query}}"},},"data.cita"] },},
                    callback: {
                      onClickAfter: function (node, a, item, event) {
                        var date_time = $(".o_website_appoinment_form select[name='date_time']").val();
                        var duration = $(".o_website_appoinment_form select[name='duration']").val();
                        var calendar_appointment_type_id = item['id'];
                        $(".o_website_appointment_form input[name='calendar_appointment_type_id']").val(calendar_appointment_type_id);
                        var postURL = '/website/calendar/' + calendar_appointment_type_id + '/info?date_time='+ date_time + '&amp;duration=' + duration;
                        $(".o_website_appointment_form").attr('action', postURL);
                      }
                    }
                });
                $('.appointment-container .typeahead__result').hide();
                //$('.appointment-container').addClass('visible');
              }
          }
        });
    },
    debug: true,
  });


	sAnimation.registry.OdooWebsiteSearchAppointment = sAnimation.Class.extend({
		selector: ".search-query-appointment",
    //xmlDependencies: ['/calendar_csj/static/src/xml/calendar_csj_utils.xml'],
    autocompleteMinWidth: 300,
		start: function () {
		    var self = this;
        var previousSelectedCityID = $(".o_website_appointment_form input[name='city_id']").val();
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
                var date_time = $(".o_website_appoinment_form select[name='date_time']").val();
                //console.log(date_time);
                var duration = $(".o_website_appoinment_form select[name='duration']").val();
                var calendar_appointment_type_id = item['id'];
                $(".o_website_appoinment_form input[name='calendar_appointment_type_id']").val(calendar_appointment_type_id);
                var postURL = '/website/calendar/' + calendar_appointment_type_id + '/info?date_time='+ date_time + '&amp;duration=' + duration;
                $(".o_website_appointment_form").attr('action', postURL);
              }
            }
        });
		},
		debug: true,
	});


	sAnimation2.registry.OdooWebsiteSearchSolicitante = sAnimation2.Class.extend({
		selector: ".search-prueba2",
		start: function () {
		    var self = this;
		    this.$target.attr("autocomplete","off");
            this.$target.parent().addClass("typeahead__container");
            this.$target.typeahead({
            	minLength: 1,
				maxItem: 15,
				delay: 500,
				order: "asc",
				hint: true,
				display: ["id","cita"],
                template: '<span>' +
                          '<span>{{cita}}</span>' +
                          '</span>',
                source:{ appointment:{ url: [{ type : "GET", url : "/search/suggestion2", data : { query : "{{query}}"},},"data.cita"] },},
                callback: {
                    onResult: function (node, query, result, resultCount, resultCountPerGroup) {
                    },
                    onClickBefore: function (node, a, item, event) {
                        $('#applicant_id').val(item.id).change();
                    }
                    }
              });
		},
		debug: true

	});

	sAnimation3.registry.OdooWebsiteSearchDestino = sAnimation3.Class.extend({
		selector: ".search-destino",
		start: function () {
		    var self = this;
		    this.$target.attr("autocomplete","off");
        this.$target.parent().addClass("typeahead__container");
        this.$target.typeahead({
        minLength: 1,
				maxItem: 15,
				delay: 500,
        cache: false,
        searchOnFocus: true,
        hint: true,
        accent: true,
        maxItemPerGroup: 6,


        emptyTemplate: 'Sin resultados para <strong> {{query}} </strong>',
        //groupOrder: ["code", "name"],
        correlativeTemplate: true,

        updater: function(item) {
            $setDestino.append(item, ' ');
            return '';
        },
				display: ["destino"],
        template: '<span>' +
                  '<span>{{id}}</span> - ' +
                  '<span>{{destino}}</span>' +
                  '</span>',
        source:{ city:{ url: [{ type : "GET", url : "/search/destino", data : { query : "{{query}}"},},"data.destino"] },},
        callback: {
            onResult: function (node, query, result, resultCount, resultCountPerGroup) {
            },
            onClickBefore: function (node, a, item, event) {
                $('#destination_id').val(item.id).change();
            },
            onClickAfter: function (node, a, item, event) {
               dest++;
               var objTo = document.getElementById('destination_fields')
               var divdestinationlist = document.createElement("div");
               divdestinationlist.setAttribute("class", "form-group removeclassdestination"+dest);
               var rdiv = 'destination_remove_form'+dest;
               var destinationSelectedName = $(".appointment_submit_form input[id='destino']").val();
               divdestinationlist.innerHTML = '<div class="col-md-12 row destination_remove_form' + dest + '"><div class="col-md-11"><input type="char" class="form-control  text-uppercase" name="destino' + dest + '" required="1" value="' + destinationSelectedName + '"/></div><div class="col-md-1"><button class="btn btn-danger fa fa-remove btn-guest_remove" onclick="remove_destination_fields('+ dest +');" type="button"></button></div></div>';
               objTo.appendChild(divdestinationlist)
               $(".linediv").show();
               var destinationSelectedCont = $(".appointment_submit_form input[name='destinationcont']").val();
               $(".appointment_submit_form input[name='destinationcont']").val(parseInt(destinationSelectedCont)+1);
               $(".appointment_submit_form input[id='destino']").val('');
               $("#destino").focus();
            }
          }
      });
		},
		debug: true

	});

});
