moduledir = pkgdatadir / meson.project_name() / 'ui'

modules_sources = [
    '__init__.py',
    'window.py',
    'screenshot.py',
    'nav.py',
    'mod.py',
    'page_bar.py'
]

install_data(modules_sources, install_dir: moduledir)
subdir('pages')