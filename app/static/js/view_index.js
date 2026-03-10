import {ImageLazyLoad} from '/static/js/image_lazy_load.js'

document.addEventListener('DOMContentLoaded', function()
{
    fetch('/json/overview')
        .then(r => {
            if (!r.ok) {
                throw new Error(r.statusText)
            }

            return r.json()
        })
        .then(data => {
            createAllTiles(data)
        })
})

function createAllTiles(data)
{
    const secMenu = document.querySelector('.secondary-menu')
    const container = document.querySelector('main')
    const tplAnchor = document.querySelector('template#menu-anchor').content
    const tplTileContainer = document.querySelector('template#tile-section').content
    const tplTileHeader = document.querySelector('template#tile-header').content
    const tplTile = document.querySelector('template#tile').content

    const sections = []
    for (let i in data)
    {
        if (sections.includes(data[i].type)) continue
        sections.push(data[i].type)
    }

    for (let i in sections) {
        const s = sections[i]
        const header = tplTileHeader.cloneNode(true)
        header.querySelector('h2').textContent = s
        header.querySelector('h2').id = s
        container.append(header)

        const anchor = tplAnchor.cloneNode(true)
        anchor.querySelector('a').href = '#' + s
        anchor.querySelector('a').textContent = s
        secMenu.append(anchor)

        const tileCont = tplTileContainer.cloneNode(true)
        const cont = tileCont.querySelector('.tiles-container')
        container.append(tileCont)

        for (let k in data) {
            const d = data[k]
            if (s !== d.type ) continue

            const tile = tplTile.cloneNode(true)

            tile.querySelector('.thumb-bg').setAttribute('data-src', d.thumb)
            tile.querySelector('h3').textContent = d.path_dir
            tile.querySelector('a').href = d.path_link

            cont.append(tile)
        }
    }

    new ImageLazyLoad('.thumb-bg', true, '300px')
}