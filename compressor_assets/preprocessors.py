from django.core.exceptions import ImproperlyConfigured
from os import path


class AbstractPreprocessor:
    command_template = '{command} {parameters} {infile} {outfile}'
    command = None
    prefix = None

    @staticmethod
    def get_initial_params():
        return {}

    def __init__(self, binary_path=None, **params):
        if not self.command:
            raise ImproperlyConfigured

        if binary_path:
            self.prefix = binary_path

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
                tokens.append(delimiter.join([param, value]))
            elif isinstance(value, (list, tuple, set)):
                for item in value:
                    tokens.append(delimiter.join([param, item]))
            else:
                raise ImproperlyConfigured
        return ' '.join(map('--{}'.format, tokens))

    def get_command(self, delimiter='='):
        return self.command_template.format(
            command=path.join(self.prefix, self.command) if self.prefix else self.command,
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


class Sass(AbstractPreprocessor):
    command = 'sass'


class TypeScript(AbstractPreprocessor):
    command = 'tsc'
    command_template = '{command} {parameters} --outFile {outfile} {infile}'


class Babel(AbstractPreprocessor):
    command = 'babel'
    command_template = '{command} {parameters} -o {outfile} {infile}'


class Browserify(AbstractPreprocessor):
    command = 'browserify'
    command_template = '{command} {infile} {parameters} -o {outfile}'


TypeScriptPreprocessor = TypeScript
BabelPreprocessor = Babel
SassPreprocessor = Sass
BrowserifyPrerprocessor = Browserify
