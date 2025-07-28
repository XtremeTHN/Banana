pkgdatadir = get_option('prefix') / get_option('datadir')
moduledir = pkgdatadir / meson.project_name()

python = import('python')
python_i = python.find_installation('python3', modules: ['gi', 'requests'])

dependency('gtk4')
dependency('libadwaita-1')

conf = configuration_data()
conf.set('VERSION', meson.project_version())
conf.set('pkgdatadir', pkgdatadir)

configure_file(
    input: 'banana.in',
    output: 'banana',
    configuration: conf,
    install: true,
    install_dir: get_option('bindir'),
    install_mode: 'r-xr-xr-x'
)

banana_sources = [
    '__init__.py',
    'main.py'
]

install_data(banana_sources, install_dir: moduledir)

subdir('modules')
subdir('ui')