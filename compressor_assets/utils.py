from django.contrib.staticfiles.finders import get_finders


def get_include_dirs(dirname):
    include_dirs = []

    for finder in get_finders():
        if hasattr(finder, 'storage'):
            include_dirs.append(finder.storage.path(dirname))
        elif hasattr(finder, 'storages'):
            for storage in finder.storages.values():
                include_dirs.append(storage.path(dirname))

    return include_dirs
