import {ImageLazyLoad} from '/static/js/image_lazy_load.js'

document.addEventListener('DOMContentLoaded', function()
{
    new ImageLazyLoad('.bg-thumb', true, '300px')
})