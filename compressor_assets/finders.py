from collections import OrderedDict

from django.conf import settings
from django.contrib.staticfiles.finders import FileSystemFinder, AppDirectoriesFinder
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage

from compressor.storage import CompressorFileStorage


class AbstractAssetFinder(FileSystemFinder):
    def __init__(self, app_names=None, *args, **kwargs):
        super().__init__(app_names, *args, **kwargs)

        self.locations = []
        self.storages = OrderedDict()

        try:
            paths = self.get_paths()
        except AttributeError as e:
            raise ImproperlyConfigured(e)

        for root in paths:
            if ('', root) not in self.locations:
                self.locations.append(('', root))

        for _, root in self.locations:
            filesystem_storage = FileSystemStorage(location=root)
            filesystem_storage.prefix = ''
            self.storages[root] = filesystem_storage

    def list(self, ignore_patterns):
        return []

    def get_paths(self):
        raise NotImplemented


class BowerFinder(AbstractAssetFinder):
    def get_paths(self):
        return [settings.BOWER_COMPONENTS_ROOT]


class NpmFinder(AbstractAssetFinder):
    def get_paths(self):
        return [settings.NPM_COMPONENTS_ROOT]


class AssetFinder(AbstractAssetFinder):
    def get_paths(self):
        return [settings.COMPRESS_SOURCE_ROOT]


class GlobalAssetFinder(AbstractAssetFinder):
    def get_paths(self):
        return [settings.ASSETS_DIRS]


class AppAssetFinder(AppDirectoriesFinder):
    storage_class = CompressorFileStorage
    source_dir = 'assets'

    def list(self, ignore_patterns):
        return []
