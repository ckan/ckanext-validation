this.ckan.module('validation-report', function (jQuery) {
  return {
    options: {
      report: null
    },
    initialize: function() {
      goodtablesUI.render(
        goodtablesUI.Report,
        {report: this.options.report},
        this.el[0]
      )
    }
  }
});
