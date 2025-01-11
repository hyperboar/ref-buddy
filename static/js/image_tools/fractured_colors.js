
class FracturedColors
{
    _container
    _containerSel
    _node

    _width
    _height

    constructor(selContainer)
    {
        if (selContainer)
        {
            this._containerSel = selContainer
        }
        else
        {
            this._container = document.createElement('div')
            this._container.classList.add('fractured-colors')
            this._container.id = 'frac-color-totally-not-occupied-name-' + Math.round(Math.random() * 1000)
            // this._container.classList.add('hidden')
            document.querySelector('body').appendChild(this._container)

            this._containerSel = '#' + this._container.id
        }

        this._container = document.querySelector(this._containerSel)

        this._node = document.createElement('canvas');
        this._node.id = 'fractured-colors-image'
        this._container.appendChild(this._node)
    }

    render(selImg)
    {
        console.log('rendering!')
        const ctx = this._node.getContext("2d")
        const img = document.querySelector(selImg)
        this._width = img.naturalWidth
        this._height = img.naturalHeight
        const w = this._width
        const h = this._height
        ctx.canvas.width = w
        ctx.canvas.height = h

        console.log(`${w} ${h}`)

        ctx.drawImage(img, 0, 0, w, h, 0, 0, w, h)

        this.processFilter(ctx)
    }

    // processFilter(ctx)
    // {
    //     let id = -1
    //     let color = null
    //
    //     for (let x = 0; x < this._width; x++)
    //     {
    //         for (let y = 0; y < this._height; y++)
    //         {
    //             id = this.getPixId(x, y)
    //             color = getClrById(id)
    //
    //             ctx.setP
    //             this.setColor(x, y, color)
    //         }
    //     }
    // }

    getPixId(x, y)
    {

    }

    getClrById(id)
    {
        return
    }
}

export {FracturedColors}