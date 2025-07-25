blueprints = custom_target('blueprints',
  input: files(
    'navigation.blp',
    'mod-button.blp',
    'top-mod.blp',
    'window.blp',
    'mod-page-dialog.blp',
    'search-page.blp',
    'mod-page.blp',
    'home-page.blp',
    'sidebar-mod.blp',
    'screenshot.blp',
    'wip-page.blp',
    'home-page.blp',
    'page-bar.blp'
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)