"use strict";

ckan.module('validation-report', function (jQuery) {
  return {
    options: {
      report: null
    },
    initialize: function() {
      let element = document.getElementById('report')
      let report = JSON.parse(this.options.report)
      frictionlessComponents.render(frictionlessComponents.Report, { report }, element)
    }
  }
});
