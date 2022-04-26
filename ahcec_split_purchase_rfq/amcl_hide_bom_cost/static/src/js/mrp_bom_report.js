/** @odoo-module **/
alert('11111111222')
import core from 'web.core';
import framework from 'web.framework';
import stock_report_generic from 'stock.stock_report_generic';

var QWeb = core.qweb;
var _t = core._t;


var MrpBomReport = stock_report_generic.include({

    _onChangeType: function (ev) {
        alert('222222222222')
        var report_type = $("option:selected", $(ev.currentTarget)).data('type');
        this.given_context.report_type = report_type;
        this._reload_report_type();
    },

});
//
//core.action_registry.add('mrp_bom_report', MrpBomReport);
//export default MrpBomReport;