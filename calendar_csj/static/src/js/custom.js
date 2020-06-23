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
        var previousSelectedCityID = $(".o_website_appoinment_form input[name='city_id']").val();
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
                //var previousSelectedCityID = $(".o_website_appoinment_form input[name='city_id']").val();
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
        var previousSelectedCityID = $(".o_website_appoinment_form input[name='city_id']").val();
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
                    onResult: function (node, query, result, resultCount, resultCountPerGroup) {
                        console.log(node, query, result, resultCount, resultCountPerGroup);
                    },
                    onClickBefore: function (node, a, item, event) {
                        console.log(item.id);
                        $('#calendarType').val(item.id).change();
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
