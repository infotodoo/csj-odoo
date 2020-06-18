
//console.log("custom js caleedddddddddddddddddddddddddddddddddd")
odoo.define('calendar_csj.calendar_csj', function(require) {
    "use strict";

	var ajax = require('web.ajax');
	var core = require('web.core');
	//var base = require('web_editor.base');
	//var animation = require('web_editor.snippets.animation');
	var sAnimation = require('website.content.snippets.animation');
	var sAnimation2 = require('website.content.snippets.animation');
	var sAnimation3 = require('website.content.snippets.animation');

	var qweb = core.qweb;
    var _t = core._t;

    var ajax = require('web.ajax');
    //var oe_website_sale = this;

	sAnimation.registry.OdooWebsiteSearchCita = sAnimation.Class.extend({
		selector: ".search-query",
		start: function () {
		    //console.log("start caleedddddddddddddddddddddddddddddddddd")
		    var self = this;
		    //console.log("start caleedddddddddddddddddddddddddddddddddd",this.$target.typeahead)
		    this.$target.attr("autocomplete","off");
            this.$target.parent().addClass("typeahead__container");
            this.$target.typeahead({
            	minLength: 1,
				maxItem: 15,
				//group: ["category", "{{group}}"],
				delay: 500,
				order: "asc",
				hint: true,
				accent: true,
				dynamic: true,
				display: ["id","cita"],
				//maxItemPerGroup: 5,
                template: '<span>' +
                          '<span>{{cita}}</span>' +
                          '</span>',
                source:{ product:{ url: [{ type : "GET", url : "/search/suggestion", data : { query : "{{query}}"},},"data.cita"] },},
                callback: {
                    onResult: function (node, query, result, resultCount, resultCountPerGroup) {
                        console.log(node, query, result, resultCount, resultCountPerGroup);
                    },
                    onClickBefore: function (node, a, item, event) {
                        console.log(item.id);

                        //$('select[name=calendarType]').val(item.id).attr("selected",true);
                        $('#calendarType').val(item.id).change();
                    }
                    }
              });


              console.log("222222222222222222 caleedddddddddddddddddddddddddddddddddd",this.$target)


		},
		debug: true

	});

	sAnimation2.registry.OdooWebsiteSearchSolicitante = sAnimation2.Class.extend({
		selector: ".search-prueba2",
		start: function () {
		    //console.log("start caleedddddddddddddddddddddddddddddddddd")
		    var self = this;
		    //console.log("start caleedddddddddddddddddddddddddddddddddd",this.$target.typeahead)
		    this.$target.attr("autocomplete","off");
            this.$target.parent().addClass("typeahead__container");
            this.$target.typeahead({
            	minLength: 1,
				maxItem: 15,
				//group: ["category", "{{group}}"],
				delay: 500,
				order: "asc",
				hint: true,
				//dynamic:true,
				display: ["id","cita"],
				//maxItemPerGroup: 5,
                template: '<span>' +
                          '<span>{{cita}}</span>' +
                          '</span>',
                source:{ product:{ url: [{ type : "GET", url : "/search/suggestion2", data : { query : "{{query}}"},},"data.cita"] },},
                callback: {
                    onResult: function (node, query, result, resultCount, resultCountPerGroup) {
                        //console.log(node, query, result, resultCount, resultCountPerGroup);
                    },
                    onClickBefore: function (node, a, item, event) {
                    	console.log(item.id);

                        $('#applicant_id').val(item.id).change();
                    }
                    }
              });


              console.log("222222222222222222 caleedddddddddddddddddddddddddddddddddd",this.$target)


		},
		debug: true

	});

	sAnimation3.registry.OdooWebsiteSearchDestino = sAnimation3.Class.extend({
		selector: ".search-destino",
		start: function () {
		    //console.log("start caleedddddddddddddddddddddddddddddddddd")
		    var self = this;
		    //console.log("start caleedddddddddddddddddddddddddddddddddd",this.$target.typeahead)
		    this.$target.attr("autocomplete","off");
            this.$target.parent().addClass("typeahead__container");
            this.$target.typeahead({
            	minLength: 1,
				maxItem: 15,
				//group: ["category", "{{group}}"],
				delay: 500,
				order: "asc",
				hint: true,
				//dynamic:true,
				display: ["id","destino"],
				//maxItemPerGroup: 5,
                template: '<span>' +
                          '<span>{{destino}}</span>' +
                          '</span>',
                source:{ product:{ url: [{ type : "GET", url : "/search/destino", data : { query : "{{query}}"},},"data.destino"] },},
                callback: {
                    onResult: function (node, query, result, resultCount, resultCountPerGroup) {

                    },
                    onClickBefore: function (node, a, item, event) {
                        //console.log(item.id);

                            $('#destination_id').val(item.id).change();
                    }
                    }
              });


		},
		debug: true

	});


});;
