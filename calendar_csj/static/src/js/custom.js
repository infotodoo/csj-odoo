odoo.define('website_calendar.select_appointment_type_csj', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.websiteCalendarSelect = publicWidget.Widget.extend({
    selector: '.o_website_calendar_appointment',
    events: {
        'change .o_website_appoinment_form select[id="calendarType"]': '_onAppointmentTypeChange'
    },

    /**
     * @constructor
     */
    init: function () {
        this._super.apply(this, arguments);
        // Check if we cannot replace this by a async handler once the related
        // task is merged in master
        this._onAppointmentTypeChange = _.debounce(this._onAppointmentTypeChange, 250);
    },
    /**
     * @override
     * @param {Object} parent
     */
    start: function (parent) {
        // set default timezone
        var timezone = jstz.determine();
        $(".o_website_appoinment_form select[name='timezone']").val(timezone.name());
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * On appointment type change: adapt appointment intro text and available
     * employees (if option enabled)
     *
     * @override
     * @param {Event} ev
     */
    _onAppointmentTypeChange: function (ev) {
        var appointmentID = $(ev.target).val();
        var previousSelectedEmployeeID = $(".o_website_appoinment_form select[name='employee_id']").val();
        var previousSelectedDateTime = $(".o_website_appoinment_form select[name='date_time']").val();
        var postURL = '/website/calendar/' + appointmentID + '/info?date_time=#{date_time}';
        $(".o_website_appoinment_form").attr('action', postURL);
        this._rpc({
            route: "/website/calendar/get_appointment_info",
            params: {
                appointment_id: appointmentID,
                prev_emp: previousSelectedEmployeeID,
                date_time: previousSelectedDateTime,
            },
        }).then(function (data) {
            if (data) {
                $('.o_calendar_intro').html(data.message_intro);
                if (data.assignation_method === 'chosen') {
                    $(".o_website_appoinment_form div[name='employee_select']").replaceWith(data.employee_selection_html);
                } else {
                    $(".o_website_appoinment_form div[name='employee_select']").addClass('o_hidden');
                    $(".o_website_appoinment_form select[name='employee_id']").children().remove();
                }
            }
        });
    },
});
});


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
		    var self = this;
		    this.$target.attr("autocomplete","off");
            this.$target.parent().addClass("typeahead__container");
            this.$target.typeahead({
            	minLength: 1,
				maxItem: 15,
				//group: ["category", "{{group}}"],
				delay: 500,
				order: "asc",
				//hint: true,
				accent: true,
				//dynamic: false,
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


              console.log("pasando",this.$target)
              console.log("pasando","{{query}}")


		},
		debug: true

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
