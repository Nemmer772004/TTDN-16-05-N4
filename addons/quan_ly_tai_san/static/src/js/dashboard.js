odoo.define('quan_ly_tai_san.Dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var rpc = require('web.rpc');

var DashboardTaiSan = AbstractAction.extend({
    contentTemplate: 'quan_ly_tai_san.DashboardTaiSanMain',

    events: {
        'click .o_dashboard_action': 'onClickDashboardAction',
        'click button[data-action]': 'onClickDashboardAction',
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.data = {};
    },

    willStart: function() {
        var self = this;
        return this._super().then(function() {
            return self.fetchData();
        });
    },

    start: function() {
        var self = this;
        return this._super().then(function() {
            self.renderDashboard();
        });
    },

    fetchData: function() {
        var self = this;
        return rpc.query({
            model: 'dashboard.tai_san',
            method: 'get_dashboard_data',
            args: [],
        }).then(function(result) {
            self.data = result;
        });
    },

    renderDashboard: function() {
        var self = this;
        self.$el.html(core.qweb.render('quan_ly_tai_san.DashboardTaiSanMain', {
            widget: self,
            data: self.data,
        }));
    },

    onClickDashboardAction: function(ev) {
        ev.preventDefault();
        var $target = $(ev.currentTarget);
        var actionName = $target.data('action');
        var actionContext = $target.data('context') || {};
        
        if (actionName) {
            this.do_action(actionName, {
                additional_context: actionContext,
            });
        }
    },

    refreshDashboard: function() {
        var self = this;
        this.fetchData().then(function() {
            self.renderDashboard();
        });
    },
});

core.action_registry.add('dashboard_tai_san', DashboardTaiSan);

return DashboardTaiSan;

});
