class Magnification
{
    _imgTarget = null
    _lastRawPos = []

    /**
     * selSourceImg is '.modal-img'
     * selTargetImg is '.magnification'
     * @param selSourceImg
     * @param selContainer
     * @param selTargetImg
     * @param getterIsFlipped
     */
    constructor(selSourceImg, selContainer, selTargetImg, getterIsFlipped)
    {
        this.sources = Array.from(selSourceImg)
        this.container = document.querySelector(selContainer)
        this.modalImages = Array.from(selSourceImg).map(sel => document.querySelector(sel))
        this.lastModalImage = null
        this.magnification = document.querySelector(selTargetImg)
        this.mhalf = {x:0, y:0}
        this.msize = {x:0, y:0}
        this.msizeScaled = {x:0, y:0}
        this.mpos = {x:0, y:0}
        this.scale = 1
        this.scaleStep = 0
        this.scaleAdd = 0.3
        this.maxScale = 25

        this.isZoomed = false

        this.getterIsFlipped = getterIsFlipped

        this.modalImages.forEach(mi=> mi.addEventListener('wheel', (evt) => this.onwheel(evt)))

        this.modalImages.forEach(mi => mi.addEventListener('mouseup', (evt) => this.onmouseup(evt)))

        this.modalImages.forEach(mi => mi.addEventListener('mousemove', (evt) => this.onmousemove(evt)))

        this.container.addEventListener('wheel', (evt) => this.onwheel(evt))
        this.container.addEventListener('mouseup', (evt) => this.onmouseup(evt))
        this.container.addEventListener('mousemove', (evt) => this.onmousemove(evt))

        this._imgTarget = this.magnification.querySelector('img')
    }

    setImage(url)
    {
        this._imgTarget.src = url
    }

    reset()
    {
        this.onmouseup({})
    }

    onwheel(evt)
    {
        // Prevent the default scrolling behavior
        evt.preventDefault()

        if (this.modalImages.some(node => node === evt.target))
            this.lastModalImage = evt.target

        this.msize.x = this.container.offsetWidth
        this.msize.y = this.container.offsetHeight

        const w = this.msize.x
        const h = this.msize.y
        this.ratio = w / h

        if (!this.isZoomed)
        {
            this.lastModalImage.classList.add('modal-img-darken')

            this.container.classList.remove('vis-hide')

            this.magnification.style.width  = `100%`
            this.magnification.style.height = `100%`
        }



        // Determine the direction of the scroll
        const delta = Math.sign(evt.deltaY) // -1 for scrolling up, 1 for scrolling down

        // Scrolling up
        if (delta === 1) { this.scaleStep-- }
        // Scrolling down
        else if (delta === -1) { this.scaleStep++ }

        this.scaleStep = Math.min(Math.max(this.scaleStep, 1), this.maxScale)

        if (!this.isZoomed)
        {
            this.scaleStep = 0
        }

        this.scale = 1 + this.scaleAdd * this.scaleStep

        this.isZoomed = true

        this.msizeScaled.x = this.msize.x * this.scale
        this.msizeScaled.y = this.msize.y * this.scale * (this.ratio)
        this.mhalf.x = this.msize.x * 0.5
        this.mhalf.y = this.msize.y * 0.5

        this.magnification.style.transform = `scale(${(this.getterIsFlipped() ? -1 : 1)}, 1)`
        // this._imgTarget.style.transform = `scale(${(this.getterIsFlipped() ? -1 : 1) * this.scale}, ${this.scale})`
        this._imgTarget.style.transform = `scale(${(this.getterIsFlipped() ? -1 : 1) * this.scale}, ${this.scale})`

        this._lastRawPos[0] = evt.clientX; this._lastRawPos[1] = evt.clientY;
        this.updateMagnifiedOffset(evt.clientX, evt.clientY)
    }

    onmousemove(evt)
    {
        if (!this.isZoomed) { return }

        this._lastRawPos[0] = evt.clientX; this._lastRawPos[1] = evt.clientY;
        this.updateMagnifiedOffset(evt.clientX, evt.clientY)
    }

    onmouseup(evt)
    {
        if (!this.isZoomed) { return }

        this.isZoomed = false
        this.lastModalImage .classList.remove('modal-img-darken')
        this.container.classList.add('vis-hide')

        this.scaleStep = 1
        this.scale = 1 + this.scaleAdd * this.scaleStep
    }

    updateMagnifiedOffset(cx, cy)
    {
        // Calculate the position within the image
        // offset from top left corner or container
        let x = cx
        let y = cy

        // clamp 0 to msize
        // range shift so 0 is in the middle
        x = Math.min(Math.max(x, 0), this.msize.x) - this.mhalf.x
        y = Math.min(Math.max(y, 0), this.msize.y) - this.mhalf.y

        x *= -this.scale //* (this.getterIsFlipped() ? -1 : 1)
        y *= -this.scale * this.ratio

        this._imgTarget.style.transform = `scale(${(this.getterIsFlipped() ? -1 : 1) * this.scale}, ${this.scale}) translate(${x}px, ${y}px)`
    }
}

export { Magnification }