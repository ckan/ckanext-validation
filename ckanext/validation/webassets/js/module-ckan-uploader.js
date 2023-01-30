"use strict";

ckan.module('ckan-uploader', function (jQuery) {
  return {
    options: {
      dataset_id: '',
      resource_id: '',
      // The CKAN instance base URL
      upload_url: '',
    },
    afterUpload: (resource_id) => (evt) => {
      let resource = evt.detail
      let resource_id = resource.id
      
      // Next step set automatically some fields (name based on 
      // the filename, mime type and the ckanext-validation schema
      // field, infered using frictionless) in the form
      // based in the uploaded file

      // Set `name` field
      let field_name = document.getElementById('field-name')
      let url_parts = resource.url.split('/')
      let resource_name = url_parts[url_parts.length - 1]
      field_name.value = resource_name
      
      // Set `mime type` field
      let resource_type = document.getElementById('field-format')
      jQuery('#field-format').select2("val", resource.format)
      resource_type.value = resource.format
      
      // Set `schema` ckanext-validation field
      let json_schema_field = document.getElementById('field-schema-json')
      if ('schema' in resource) {
        // If there is a schema, we open the JSON
        json_schema_field.value = JSON.stringify(resource.schema, null, 2)
        let json_button = document.getElementById('open-json-button')
        json_button.dispatchEvent(new Event('click'))
      } else {
        json_schema_field.value = '' 
        let json_clear_button = document.querySelector('[title=Clear]')
        json_clear_button.dispatchEvent(new Event('click'))
      }
  
      // Set the form action to save the created resource
      let hidden_resource_id = document.getElementById('resource_id').value

      let resource_form = document.getElementById('resource-edit')
      let current_action = resource_form.action

      if (hidden_resource_id == '') {
        let lastIndexNew = current_action.lastIndexOf('new')
        resource_form.action = current_action.slice(0, lastIndexNew) + `${resource.id}/edit`
      }

      // Function to redirect the user to add another resource
      // if "Save & Add another" button is clicked

      let save_add_another = function (evt) {
        if (evt.submitter.value == 'again') {
          evt.preventDefault();
          resource_form = document.getElementById('resource-edit')
          let form_data = $('form#resource-edit')

          // We need to add this because jquery .serialize don't 
          // serialize input of type submit. CKAN used this information
          // to choose where to redirect an user after a new resource is 
          // created
          let save_input = document.createElement('input') 
          save_input.setAttribute('type', 'hidden')
          save_input.setAttribute('name', 'save')
          save_input.setAttribute('value', 'again')
          form_data.append(save_input)

          // new_action: the URL to a new resource creation form
          let new_action = resource_form.action
          let lastIndexNew = new_action.lastIndexOf('new')
          // edit_action: the URL to update an already existing form
          let edit_action = new_action.slice(0, lastIndexNew) + `${resource_id}/edit`

          // Here we send the form using ajax and redirect the user again to 
          // a new resource create form
          $.ajax({
            url: new_action, 
            type: 'post',
            data: form_data.serialize(), 
            success: function(data) {
              location.href = current_action 
            }
          })
        }
      }

      resource_form = document.getElementById("resource-edit")
      resource_form.addEventListener('submit', save_add_another)

    },
    initialize: function() {
      let resource_id = this.options.resource_id
      let dataset_id = this.options.dataset_id
      let current_url = document.getElementById('current_url').value
      let url_type = document.getElementById('url_type').value
      let update = document.getElementById('update').value

      console.log(resource_id, dataset_id, update, 'DEBUG')

      // Add the upload widget
      CkanUploader('ckan_uploader', 
                    this.options.upload_url,
                    dataset_id,
                    resource_id,
                    url_type,
                    current_url,
                    update)
      // Event handler for when a resource file is uploaded
      document.getElementById('ckan_uploader').addEventListener('fileUploaded', this.afterUpload(resource_id))
    }
  }
});
