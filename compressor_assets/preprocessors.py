from pathlib import Path
from django.core.exceptions import ImproperlyConfigured


class AbstractPreprocessor:
    command = None
    args_template = '{parameters} {infile} {outfile}'

    def __init__(self, binary_path=None, interpreter=None, **params):
        if not self.command:
            raise ImproperlyConfigured

        self.command = Path(self.command)

        if binary_path:
            self.binary_path = Path(binary_path)

        if interpreter:
            self.interpreter = Path(interpreter)

        self.params = {
            param.replace('_', '-'): value
            for param, value in params.items()
        }

    def get_parameters(self, delimiter):
        tokens = []
        for param, value in self.params.items():
            if isinstance(value, bool):
                tokens.append(param)
            elif isinstance(value, (int, float, str, Path)):
                tokens.append(delimiter.join([param, str(value)]))
            elif isinstance(value, (list, tuple, set)):
                for item in value:
                    tokens.append(delimiter.join([param, str(item)]))
            else:
                raise ImproperlyConfigured
        return ' '.join(map('--{}'.format, tokens))

    def get_command(self):
        command = self.command
        if self.binary_path:
            command = self.binary_path / self.command
        if self.interpreter:
            command = ' '.join(map(str, [self.interpreter, command]))
        return str(command)

    def get_args(self, delimiter):
        return self.args_template.format(
            parameters=self.get_parameters(delimiter=delimiter),
            infile='{infile}',
            outfile='{outfile}',
        )

    def register(self, mimetype, delimiter='='):
        return mimetype, '{command} {args}'.format(
            command=self.get_command(),
            args=self.get_args(delimiter)
        )


class Preprocessor(AbstractPreprocessor):
    def __init__(self, command, args_template=None, **kwargs):
        self.command = command
        if args_template:
            self.args_template = args_template
        super().__init__(**kwargs)


class Sass(AbstractPreprocessor):
    command = 'sass'


class TypeScript(AbstractPreprocessor):
    command = 'tsc'
    args_template = '{parameters} --outFile {outfile} {infile}'


class Babel(AbstractPreprocessor):
    command = 'babel'
    args_template = '{parameters} -o {outfile} {infile}'


class Browserify(AbstractPreprocessor):
    command = 'browserify'
    args_template = '{infile} {parameters}'


TypeScriptPreprocessor = TypeScript
BabelPreprocessor = Babel
SassPreprocessor = Sass
BrowserifyPrerprocessor = Browserify
