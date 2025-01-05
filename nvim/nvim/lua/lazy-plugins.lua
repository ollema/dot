require('lazy').setup({ import = 'custom/plugins' }, {
  dev = {
    path = '~/repos',
  },
  change_detection = {
    notify = false,
  },
})
