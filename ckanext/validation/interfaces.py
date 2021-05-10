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
