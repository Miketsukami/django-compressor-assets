from compressor_assets.utils import get_include_dirs
from django.core.exceptions import ImproperlyConfigured


class AbstractPreprocessor:
    command_template = '{command} {parameters} {infile} {outfile}'
    command = None
    params = {}

    def __init__(self, **params):
        if not self.command:
            raise ImproperlyConfigured
        self.params.update({
            param.replace('_', '-'): value
            for param, value in params.items()
        })

    def get_parameters(self):
        tokens = []
        for param, value in self.params.items():
            if isinstance(value, bool):
                tokens.append(param)
            elif isinstance(value, (int, float, str)):
                tokens.append('{}={}'.format(param, value))
            elif isinstance(value, (list, tuple, set)):
                for item in value:
                    tokens.append('{}={}'.format(param, item))
            else:
                raise ImproperlyConfigured
        return ' '.join(map('--{}'.format, tokens))

    def get_command(self):
        return self.command_template.format(
            command=self.command,
            parameters=self.get_parameters(),
            infile='{infile}',
            outfile='{outfile}',
        )

    def register(self, mimetype):
        return mimetype, self.get_command()


class GenericPreprocessor(AbstractPreprocessor):
    def __init__(self, command, **params):
        self.command = command
        super().__init__(**params)


class SassPreprocessor(AbstractPreprocessor):
    command = 'sass'

    def __init__(self, include_folder_name=None, **kwargs):
        super().__init__(**kwargs)
        if include_folder_name:
            load_path = self.params.get('load-path') or []
            self.params['load-path'] = list(
                set([load_path] if isinstance(load_path, str) else [load_path]) |
                set(get_include_dirs(include_folder_name))
            )


Preprocessor = GenericPreprocessor