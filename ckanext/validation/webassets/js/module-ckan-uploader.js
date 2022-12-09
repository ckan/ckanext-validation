"use strict";

ckan.module('ckan-uploader', function (jQuery) {
  return {
    options: {
      upload_url: '',
      dataset_id: ''
    },
    afterUpload: (evt) => {
      let resource = evt.detail
      // Set name
      let field_name = document.getElementById('field-name')
      let url_parts = resource.url.split('/')
      let resource_name = url_parts[url_parts.length - 1]
      field_name.value = resource_name
      
      // Set mime type
      let resource_type = document.getElementById('field-format')
      jQuery('#field-format').select2("val", resource.format)
      resource_type.value = resource.format
      
      // Set schema
      let json_schema_field = document.getElementById('field-schema-json')
      json_schema_field.value = JSON.stringify(resource.schema, null, 2)
      let json_button = document.getElementById('open-json-button')
      json_button.dispatchEvent(new Event('click'))

      // Set the form action to save the created resource
      let resource_form = document.getElementById('resource-edit')
      let current_action = resource_form.action
      let lastIndexNew = current_action.lastIndexOf('new')

      resource_form.action = current_action.slice(0, lastIndexNew) + `${resource.id}/edit`
    },
    initialize: function() {
      CkanUploader('ckan_uploader', this.options.upload_url, this.options.dataset_id)
      document.getElementById('ckan_uploader').addEventListener('fileUploaded', this.afterUpload)
    }
  }
});
