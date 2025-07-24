gnome = import('gnome')

moduledir = pkgdatadir / meson.project_name() / 'data'

subdir('ui')

gnome.compile_resources(
    'banana',
    'banana.gresource.xml',
    gresource_bundle: true,
    dependencies: blueprints,
    install: true,
    install_dir: moduledir
)