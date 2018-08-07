
this.ckan.module('validation-report', function (jQuery) {
  return {
    options: {
      report: null
    },
    initialize: function() {
      function loadScript(url, callback)
      {
          var head = document.getElementsByTagName('head')[0];
          var script = document.createElement('script');
          script.type = 'text/javascript';
          script.src = url;

          script.onreadystatechange = callback;
          script.onload = callback;

          head.appendChild(script);
      }
      var scriptLoaded = function() {
        goodtablesUI.render(
          goodtablesUI.Report,
          {report: this.options.report},
          this.el[0]
        )
     }.bind(this);

     // Dynamically load the goodtables-ui script so that strings located there can be translated
     loadScript('/goodtables-ui.js', scriptLoaded) 
    }
  }
});
