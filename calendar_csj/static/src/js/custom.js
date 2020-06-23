odoo.define('calendar_csj.select_appointment_type_csj', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var time = require('web.time');

publicWidget.registry.websiteAppointmentSelect = publicWidget.Widget.extend({
    selector: '.o_website_calendar_appointment',
    events: {
        'click div.input-group span.fa-calendar': '_onCalendarIconClick',
    },
    _onCalendarIconClick: function (ev) {
      $('.date_time').datetimepicker({
          format : 'YYYY-MM-DD HH:mm:ss',
          inline: true,
          daysOfWeekDisabled: [0, 6],
          lang:'co',
          icons: {
              time: 'fa fa-clock-o',
              date: 'fa fa-calendar',
              up: 'fa fa-chevron-up',
              down: 'fa fa-chevron-down',
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

  sAnimation.registry.OdooWebsiteSearchCity = sAnimation.Class.extend({
    selector: ".search-query-city",
    autocompleteMinWidth: 300,
    init: function () {
      $('.search-query-appointment').typeahead({source: []});
    },
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
          display: ["id","city"],
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
    init: function () {
        console.log('pasando por aca mijo');
    },
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
		      display: ["id","cita"],
          template: '<span>' +
                      '<span>{{cita}}</span>' +
                      '</span>',
          source:{ appointment:{ url: [{ type : "GET", url : url, data : { query : "{{query}}"},},"data.cita"] },},
          callback: {
              onClickAfter: function (node, a, item, event) {
                var date_time = $(".o_website_appoinment_form select[name='date_time']").val();
                var duration = $(".o_website_appoinment_form select[name='duration']").val();
                var appointment = item['id'];
                //appointment = appointment.toLowerCase();
                //appointment = appointment.replace(/[^a-zA-Z0-9]+/g,'-')
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
				order: "asc",
				hint: true,
				display: ["id","destino"],
                template: '<span>' +
                          '<span>{{destino}}</span>' +
                          '</span>',
                source:{ city:{ url: [{ type : "GET", url : "/search/destino", data : { query : "{{query}}"},},"data.destino"] },},
                callback: {
                    onResult: function (node, query, result, resultCount, resultCountPerGroup) {
                      console.log("luego de seleccionado")
                    },
                    onClickBefore: function (node, a, item, event) {
                        console.log(item.id);

                            $('#destination_id').val(item.id).change();
                    },
                    onClickAfter: function (node, a, item, event) {
                      console.log("luego de seleccionado")
                    }
                  }
              });
		},
		debug: true

	});

});;
