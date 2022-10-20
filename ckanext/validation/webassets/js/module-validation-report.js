"use strict";

ckan.module('validation-report', function (jQuery) {
  return {
    options: {
      report: null
    },
    initialize: function() {
      let element = document.getElementById('report')
      frictionlessComponents.render(frictionlessComponents.Report, { options.report }, element)
    }
  }
});
