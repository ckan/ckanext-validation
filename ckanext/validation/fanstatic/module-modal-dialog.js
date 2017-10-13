this.ckan.module('modal-dialog', function (jQuery) {
  return {

    /* holds the loaded lightbox */
    modal: null,

    options: {
      /* id of the modal dialog div */
      div: null
    },

    /* Sets up the module.
     *
     * Returns nothing.
     */
    initialize: function () {
      jQuery.proxyAll(this, /_on/);

      this.el.on('click', this._onClick);
      this.modal = $('#' + this.options.div)
    },

    /* Displays the API info box.
     *
     * Examples
     *
     *   module.show()
     *
     * Returns nothing.
     */
    show: function () {

      if (this.modal) {
        return this.modal.modal('show');
      }
    },

    /* Hides the modal.
     *
     * Examples
     *
     *   module.hide();
     *
     * Returns nothing.
     */
    hide: function () {
      if (this.modal) {
        this.modal.modal('hide');
      }
    },

    /* Event handler for clicking on the element */
    _onClick: function (event) {
      event.preventDefault();
      this.show();
    }
  };
});
