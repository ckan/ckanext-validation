from ckan.plugins.interfaces import Interface


class IDataValidation(Interface):

    def can_validate(self, context, data_dict):
        '''
        When implemented, this call can be used to control whether the
        data validation should take place or not on a specific resource.

        Implementations will receive a context object and the data_dict of
        the resource.

        If it returns False, the validation won't be performed, and if it
        returns True there will be a validation job started.

        Note that after this methods is called there are further checks
        performed to ensure the resource has one of the supported formats.
        This is controlled via the `ckanext.validation.formats` config option.

        Here is an example implementation:


        from ckan import plugins as p

        from ckanext.validation.interfaces import IDataValidation


        class MyPlugin(p.SingletonPlugin):

            p.implements(IDataValidation, inherit=True)

            def can_validate(self, context, data_dict):

                if data_dict.get('my_custom_field') == 'xx':
                    return False

                return True

        '''
        return True


class IPipeValidation(Interface):
    """
    Process data in a Data Pipeline.

    Inherit this to subscribe to events in the Data Pipeline and be able to
    broadcast the results for others to process next. In this way, a number of
    IPipes can be linked up in sequence to build up a data processing pipeline.

    When a resource is validated, it broadcasts its validation_report,
    perhaps triggering a process which transforms the data to another format,
    or loads it into a datastore. These processes can in turn put the resulting
    validation reports into the pipeline
    """

    def receive_validation_report(self, validation_report):
        pass
