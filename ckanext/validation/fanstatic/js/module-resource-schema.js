 /* Image Upload
 *
 */
this.ckan.module('resource-schema', function($) {
  return {
    /* options object can be extended using data-module-* attributes */
    options: {
      is_url: false,
      is_upload: false,
      is_json: false,
      field_upload: 'schema_upload',
      field_url: 'schema_url',
      field_json: 'schema_json',
      field_schema: 'schema',
      field_clear: 'clear_upload',
      field_name: 'name',
      upload_label: ''
    },

    /* Should be changed to true if user modifies resource's name
     *
     * @type {Boolean}
     */
    _nameIsDirty: false,

    /* Initialises the module setting up elements and event listeners.
     *
     * Returns nothing.
     */
    initialize: function () {
      $.proxyAll(this, /_on/);
      var options = this.options;

      // firstly setup the fields
      // var field_upload = 'input[name="' + options.field_upload + '"]';
      var field_url = 'input[name="schema_url"]';
      var field_json = 'textarea[name="schema_json"]';

      this.input = $(field_url, this.el);
      this.field_url = $(field_url, this.el).parents('.form-group');
      this.field_json = $(field_json, this.el).parents('.form-group');
      this.field_url_input = $('input', this.field_url);
      this.field_json_input = $('textarea', this.field_json);
      this.field_schema_input = $('#field-schema');
      //this.field_name = this.el.parents('form').find(field_name);
      // this is the location for the upload/link data/image label
      this.buttons_div = $("#resource-schema-buttons");
      this.label = $('label', this.buttons_div);
      // determines if the resource is a data resource
      this.is_data_resource = (this.options.field_url === 'url') && (this.options.field_upload === 'upload');

      this.field_url_input.focus()
        .on('blur', this._onURLBlur);
      this.field_json_input.focus()
        .on('blur', this._onJSONBlur);


      // Is there a clear checkbox on the form already?
      /*
      var checkbox = $(field_clear, this.el);
      if (checkbox.length > 0) {
        checkbox.parents('.form-group').remove();
      }
      */

      // Adds the hidden clear input to the form
      /*
      this.field_clear = $('<input type="hidden" name="' + options.field_clear +'">')
        .appendTo(this.el);
      */

      // Button to set the field to be a JSON text
      this.button_json = $('<a href="javascript:;" class="btn btn-default">' +
                          '<i class="fa fa-code"></i>' +
                          this._('JSON') + '</a>')
        .prop('title', this._('Enter manually a Table Schema JSON object'))
        .on('click', this._onFromJSON);
      $('.controls', this.buttons_div).append(this.button_json);

      // Button to set the field to be a URL
      this.button_url = $('<a href="javascript:;" class="btn btn-default">' +
                          '<i class="fa fa-globe"></i>' +
                          this._('Link') + '</a>')
        .prop('title', this._('Link to a URL on the internet (you can also link to an API)'))
        .on('click', this._onFromWeb);
      $('.controls', this.buttons_div).append(this.button_url);

      /*
      // Button to attach local file to the form
      this.button_upload = $('<a href="javascript:;" class="btn btn-default">' +
                             '<i class="fa fa-cloud-upload"></i>' +
                             this._('Upload') + '</a>')
        .insertAfter(this.input);
      */

      var removeText = this._('Remove');

      // Button for resetting the form when there is a URL set
      $('<a href="javascript:;" class="btn btn-danger btn-remove-url">'
        + removeText + '</a>')
        .prop('title', removeText)
        .on('click', this._onRemoveURL)
        .insertBefore(this.field_url_input);

      // Button for resetting the form when there is a JSON text set
      $('<a href="javascript:;" class="btn btn-danger btn-remove-url">'
        + removeText + '</a>')
        .prop('title', removeText)
        .on('click', this._onRemoveJSON)
        .insertBefore(this.field_json_input);

      // Setup the file input
      /*
      this.input
        .on('mouseover', this._onInputMouseOver)
        .on('mouseout', this._onInputMouseOut)
        .on('change', this._onInputChange)
        .prop('title', this._('Upload a file on your computer'))
        .css('width', this.button_url.outerWidth());
      */

      // Fields storage. Used in this.changeState
      this.fields = $('<i />')
//        .add(this.button_upload)
        .add(this.button_url)
        .add(this.button_json)
        .add(this.field_url)
        .add(this.field_json);

      if (options.is_url) {
        this._showOnlyFieldUrl();

//        this._updateUrlLabel(this._('Data Schema URL'));
      } else if (options.is_json) {
        this._showOnlyFieldJSON();

//        this._updateUrlLabel(this._('Data Schema JSON Definition'));
      } else {
        this._showOnlyButtons();
      }
    },

    /* Update the `this.label` text
     *
     * If the upload/link is for a data resource, rather than an image,
     * the text for label[for="field-image-url"] will be updated.
     *
     * label_text - The text for the label of an uploaded/linked resource
     *
     * Returns nothing.
     */
    _updateUrlLabel: function(label_text) {
      if (! this.is_data_resource) {
        return;
      }

      this.label.text(label_text);
    },

    /* Event listener for when someone sets the field to URL mode
     *
     * Returns nothing.
     */
    _onFromWeb: function() {
      this._showOnlyFieldUrl();

      this.field_url_input.focus()
        .on('blur', this._onFromWebBlur);
      /*
      if (this.options.is_upload) {
        this.field_clear.val('true');
      }
      */

      this._updateUrlLabel(this._('URL'));
    },

    /* Event listener for when someone sets the field to JSON text mode
     *
     * Returns nothing.
     */
    _onFromJSON: function() {
      this._showOnlyFieldJSON();

      /*
      if (this.options.is_upload) {
        this.field_clear.val('true');
      }
      */
      this._updateUrlLabel(this._('JSON'));
    },

    /* Event listener for resetting the URL field back to the blank state
     *
     * Returns nothing.
     */
    _onRemoveURL: function() {
      this._showOnlyButtons();

      this.field_url_input.val('');
      this.field_url_input.prop('readonly', false);

      this.field_schema_input.val('');
    },

    /* Event listener for resetting the JSON text field back to the blank state
     *
     * Returns nothing.
     */
    _onRemoveJSON: function() {
      this._showOnlyButtons();

      this.field_json_input.val('');
      this.field_json_input.prop('readonly', false);

      this.field_schema_input.val('');
    },

    /* Event listener for when someone chooses a file to upload
     *
     * Returns nothing.
     */
    _onInputChange: function() {
      var file_name = this.input.val().split(/^C:\\fakepath\\/).pop();
      this.field_url_input.val(file_name);
      this.field_url_input.prop('readonly', true);

      this.field_clear.val('');

      this._showOnlyFieldUrl();

      this._autoName(file_name);

      this._updateUrlLabel(this._('File'));
    },

    /* Show only the buttons, hiding all others
     *
     * Returns nothing.
     */
    _showOnlyButtons: function() {
      this.fields.hide();
      this.label.show();
      this.button_url.show()
      this.button_json.show()
    },

    _showOnlyFieldUrl: function() {
      this.fields.hide();
      this.label.hide();
      this.field_url.show();
    },

    _showOnlyFieldJSON: function() {
      this.fields.hide();
      this.label.hide();
      this.field_json.show();
    },

    /* Event listener for when a user mouseovers the hidden file input
     *
     * Returns nothing.
     */
    _onInputMouseOver: function() {
//      this.button_upload.addClass('hover');
    },

    /* Event listener for when a user mouseouts the hidden file input
     *
     * Returns nothing.
     */
    _onInputMouseOut: function() {
//      this.button_upload.removeClass('hover');
    },

    _onURLBlur: function() {
      var url = this.field_url_input.val();
      if (url) {
        this.field_schema_input.val(url);
      }
    },

    _onJSONBlur: function() {
      var json = this.field_json_input.val();
      if (json) {
        this.field_schema_input.val(json);
      }
    }

  };
});
