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
       divguestlist.innerHTML = '<div class="row guest_remove_form' + guest + '" style="width:100%"><div class="col-md-5"><input type="char" class="form-control" name="nameguest' + guest + '" value="' + guestSelectedName + '"/></div><div class="col-md-5"><input type="email" class="form-control" name="emailguest' + guest + '" value="' + guestSelectedEmail + '"/></div><div class="col-md-2"><button class="btn btn-danger fa fa-remove btn-guest_remove" onclick="remove_guest_fields('+ guest +');" type="button"></button></div></div><div class="clear"></div>';
       objTo.appendChild(divguestlist)
       var guestSelectedCont = $(".appointment_submit_form input[name='guestcont']").val();
       $(".appointment_submit_form input[name='guestcont']").val(parseInt(guestSelectedCont)+1);
       $("#nameguest").focus();
    },
});
});


odoo.define('calendar_csj.select_appointment_source_csj', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var time = require('web.time');
$('.legal_document').hide();

publicWidget.registry.websiteAppointmentSourceSelect = publicWidget.Widget.extend({
    selector: '.appointment_submit_form',
    events: {
        'change #appointment_source': '_onAppointmentSourceOnChange',
    },
    _onAppointmentSourceOnChange: function (ev) {
      var source_select = $(".appointment_source select option:selected").val();
      if (source_select === 'Oficio') {
        $('.legal_document').attr("require","True");
        $('.legal_document').show();
      } else {
        $('.legal_document').attr("require","False");
        $('.legal_document').hide();
      };
    },
});
});


odoo.define('calendar_csj.select_appointment_type_csj', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var time = require('web.time');

//$('#request_date').datetimepicker({inline: true,format: 'YYYY-MM-DD',sideBySide: true,});


$(".o_website_appointment_form").submit(function(){
  var core = require('web.core');
  var rpc = require('web.rpc');
  var Dialog = require('web.Dialog');
  var date_time = $(".o_website_appointment_form input[name='date_time']").val();
  var search_city = $(".o_website_appointment_form input[name='search_city']").val();
  var search_appointment = $(".o_website_appointment_form input[name='search_appointment']").val();

  if (search_city === '' || search_city === null || search_city === 'undefined'){
    Dialog.alert(this, 'Por favor selecione una ciudad!');
    return false;
  };
  if (search_appointment === '' || search_appointment === null || search_appointment === 'undefined'){
    Dialog.alert(this, 'Por favor seleccione un Juzgado!');
    return false;
  };
  if (date_time === '' || date_time === null || date_time === 'undefined'){
    Dialog.alert(this, 'Por favor registre una fecha correcta!');
    return false;
  };
});

$(".appointment_submit_form").submit(function(){
  var core = require('web.core');
  var rpc = require('web.rpc');
  var Dialog = require('web.Dialog');
  var phone = $(".appointment_submit_form input[name='phone']").val();
  var email = $(".appointment_submit_form input[name='email']").val();
  var types = $(".appointment_submit_form input[name='types']").val();
  var process_number = $(".appointment_submit_form input[name='process_number']").val();
  var destinationcont = $(".appointment_submit_form input[name='destinationcont']").val();
  var mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
  var res = email.split("@");

  if (phone === '' || phone === null || phone === 'undefined'){
    Dialog.alert(this, 'Por favor registre un número de teléfono!');
    return false;
  };
  if (!phone.match(/^-{0,1}\d+$/)){
    Dialog.alert(this, 'Por favor registre un número de teléfono sin caracteres, solo numerico!');
    return false;
  };
  if (phone.length != 10){
    Dialog.alert(this, 'Por favor registre un número de 10 caracteres!');
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
});

publicWidget.registry.websiteAppointmentSelect = publicWidget.Widget.extend({
    selector: '.o_website_calendar_appointment',
    events: {
        'click div.input-group span.fa-calendar': '_onCalendarIconClick',
        //'click buttom.submit': '_onFormSubmitButtomClick',
    },
    //_onFormSubmitButtomClick: function (ev) {
    //  console.log('llegando al submit');
    //},

    _onCalendarIconClick: function (ev) {
      $('.date_time').datetimepicker({
          format : 'YYYY-MM-DD HH:mm',
          formatTime:'H:i',
          step: 60,
          viewMode: 'months',
          startDate:'+2020/06/28',
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
    start: function () {
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
                    display: ["id","cita"],
                    template: '<span>' +
                                '<span>{{cita}}</span>' +
                                '</span>',
                    source:{ appointment:{ url: [{ type : "GET", url : url, data : { query : "{{query}}"},},"data.cita"] },},
                    callback: {
                      onClickAfter: function (node, a, item, event) {
                        var date_time = $(".o_website_appoinment_form select[name='date_time']").val();
                        //console.log(date_time);
                        var duration = $(".o_website_appoinment_form select[name='duration']").val();
                        var appointment = item['id'];
                        var postURL = '/website/calendar/' + appointment + '/info?date_time='+ date_time + '&amp;duration=' + duration;
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
                var appointment = item['id'];
                var postURL = '/website/calendar/' + appointment + '/info?date_time='+ date_time + '&amp;duration=' + duration;
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
               divdestinationlist.innerHTML = '<div class="col-md-12 row destination_remove_form' + dest + '"><div class="col-md-11"><input type="char" class="form-control" name="destino' + dest + '" required="1" value="' + destinationSelectedName + '"/></div><div class="col-md-1"><button class="btn btn-danger fa fa-remove btn-guest_remove" onclick="remove_destination_fields('+ dest +');" type="button"></button></div></div>';
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

});;
