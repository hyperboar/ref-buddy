class ImageCursor
{
    _img
    _zoom

    constructor(selImg, selMag)
    {
        this._img = document.querySelector(selImg)
        this._zoom = document.querySelector(selMag)
    }

    toggle(keycode)
    {
        const stops = ['cursor-stop-m2', 'cursor-stop-m1', 'cursor-stop-0', 'cursor-stop-p1', 'cursor-stop-p2']

        // numpad "5" is 50% brightness or "0 exposure stops" or 18% gray
        let idx = parseInt(keycode.replace('Numpad', '').replace('Digit', ''))
        // hit 0, bring default cursor back
        if (idx === 0)
        {
            this.disableAllBut(this._img, '', stops)
            return
        }
        idx -= 3 // we start from 3 and go up.
        if (idx < 0 || stops.length <= idx) { return }

        this.toggleCssClass(this._img, stops[idx])
        this.disableAllBut(this._img, stops[idx], stops)
    }

    disableAllBut(elem, oneName, allNames)
    {
        allNames.forEach((n) => { if (n === oneName) { return } elem.classList.remove(n) })
    }

    toggleCssClass(elem, className)
    {
        if (elem.classList.contains(className)) { elem.classList.remove(className) }
        else { elem.classList.add(className) }
    }
}

export { ImageCursor }