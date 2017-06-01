from django.core.exceptions import ImproperlyConfigured


class AbstractPreprocessor:
    command_template = '{command} {parameters} {infile} {outfile}'
    command = None

    @staticmethod
    def get_initial_params():
        return {}

    def __init__(self, **params):
        if not self.command:
            raise ImproperlyConfigured

        self.params = self.get_initial_params()
        self.params.update({
            param.replace('_', '-'): value
            for param, value in params.items()
        })

    def get_parameters(self, delimiter='='):
        tokens = []
        for param, value in self.params.items():
            if isinstance(value, bool):
                tokens.append(param)
            elif isinstance(value, (int, float, str)):
                tokens.append('{}{}{}'.format(param, delimiter, value))
            elif isinstance(value, (list, tuple, set)):
                for item in value:
                    tokens.append('{}{}{}'.format(param, delimiter, item))
            else:
                raise ImproperlyConfigured
        return ' '.join(map('--{}'.format, tokens))

    def get_command(self, delimiter='='):
        return self.command_template.format(
            command=self.command,
            parameters=self.get_parameters(delimiter=delimiter),
            infile='{infile}',
            outfile='{outfile}',
        )

    def register(self, mimetype, delimiter='='):
        return mimetype, self.get_command(delimiter)


class Preprocessor(AbstractPreprocessor):
    def __init__(self, command, **params):
        self.command = command
        super().__init__(**params)


class SassPreprocessor(AbstractPreprocessor):
    command = 'sass'


class TypeScriptPreprocessor(AbstractPreprocessor):
    command = 'tsc'
    command_template = '{command} {parameters} --outFile {outfile} {infile}'
