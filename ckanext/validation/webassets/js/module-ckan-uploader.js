"use strict";

ckan.module('ckan-uploader', function (jQuery) {
  return {
    options: {
      upload_url: '',
      resource_id: '',
    },
    afterUpload: (resource_id) => (evt) => {
      let resource = evt.detail
      let resource_id = resource.id
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
      if (resource_id != '') {
        let resource_form = document.getElementById('resource-edit')
        let current_action = resource_form.action
        let lastIndexNew = current_action.lastIndexOf('new')
        resource_form.action = current_action.slice(0, lastIndexNew) + `${resource.id}/edit`
      }

      let save_add_another = function (evt) {
        if (evt.submitter.value == 'again') {
          evt.preventDefault();
          let resource_form = document.getElementById('resource-edit')
          let form_data = $('form#resource-edit')
          let save_input = document.createElement('input') 
          save_input.setAttribute('type', 'hidden')
          save_input.setAttribute('name', 'save')
          save_input.setAttribute('value', 'again')
          form_data.append(save_input)

          let new_action = resource_form.action
          let lastIndexNew = new_action.lastIndexOf('new')
          let edit_action = new_action.slice(0, lastIndexNew) + `${resource_id}/edit`

          $.ajax({
            url: edit_action, 
            type: 'post',
            data: form_data.serialize(), 
            success: function(data) {
              location.href = new_action 
            }
          })
        }
      }

      let resource_form = document.getElementById("resource-edit")
      resource_form.addEventListener('submit', save_add_another)

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
