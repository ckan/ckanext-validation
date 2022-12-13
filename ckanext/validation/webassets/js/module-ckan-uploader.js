"use strict";

ckan.module('ckan-uploader', function (jQuery) {
  return {
    options: {
      upload_url: '',
    },
    afterUpload: (resource_id) => (evt) => {
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
      if (resource_id == '' || resource_id == true) {
        let resource_form = document.getElementById('resource-edit')
        let current_action = resource_form.action
        let lastIndexNew = current_action.lastIndexOf('new')
        resource_form.action = current_action.slice(0, lastIndexNew) + `${resource.id}/edit`
      }
    },
    initialize: function() {
      let resource_id = document.getElementById('resource_id').value
      let dataset_id = document.getElementById('dataset_id').value
      let current_url = document.getElementById('current_url').value
      let url_type = document.getElementById('url_type').value
      let update = document.getElementById('update').value

      CkanUploader('ckan_uploader', 
                    this.options.upload_url,
                    dataset_id,
                    resource_id,
                    url_type,
                    current_url,
                    update)
      document.getElementById('ckan_uploader').addEventListener('fileUploaded', this.afterUpload(resource_id))
    }
  }
});
