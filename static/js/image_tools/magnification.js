class Magnification
{
    /**
     * selSourceImg is '.modal-img'
     * selTargetImg is '.magnification'
     * @param selSourceImg
     * @param selTargetImg
     * @param getterIsFlipped
     */
    constructor(selSourceImg, selTargetImg, getterIsFlipped)
    {
        // magnification
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
    }

    setImage(url)
    {
        this.magnification.style.backgroundImage = `url('${url}')`
    }

    reset()
    {
        this.onmouseup({})
    }

    onwheel(evt)
    {
        // Prevent the default scrolling behavior
        evt.preventDefault()

        this.lastModalImage = evt.target

        // Determine the direction of the scroll
        const delta = Math.sign(evt.deltaY) // -1 for scrolling up, 1 for scrolling down

        // Scrolling up
        if (delta === 1) { this.scaleStep-- }
        // Scrolling down
        else if (delta === -1) { this.scaleStep++ }

        this.scaleStep = Math.min(Math.max(this.scaleStep, 1), this.maxScale)

        this.scale = 1 + this.scaleAdd * this.scaleStep

        this.isZoomed = true

        this.mpos.x = this.lastModalImage .getBoundingClientRect().left
        this.mpos.y = this.lastModalImage .getBoundingClientRect().top
        this.msize.x = this.lastModalImage .offsetWidth
        this.msize.y = this.lastModalImage .offsetHeight
        this.msizeScaled.x = this.msize.x * this.scale
        this.msizeScaled.y = this.msize.y * this.scale
        this.mhalf.x = this.msize.x * 0.5
        this.mhalf.y = this.msize.y * 0.5

        this.lastModalImage .classList.add('modal-img-darken')
        this.magnification.style.display = 'block'
        this.magnification.style.width  = `${this.msize.x}px`
        this.magnification.style.height = `${this.msize.y}px`

        // this.magnification.style.backgroundImage = `url('${this.lastModalImage .src}')`
        this.magnification.style.backgroundSize = `${100 * this.scale}% auto`

        // Set the magnification container position
        this.magnification.style.left = `${this.mpos.x}px`
        this.magnification.style.top = `${this.mpos.y}px`

        this.updateMagnifiedOffset(evt.clientX, evt.clientY)
    }

    onmousemove(evt)
    {
        if (!this.isZoomed) { return }

        this.updateMagnifiedOffset(evt.clientX, evt.clientY)
    }

    onmouseup(evt)
    {
        if (!this.isZoomed) { return }

        this.isZoomed = false
        this.lastModalImage .classList.remove('modal-img-darken')
        this.magnification.style.display = 'none'

        this.scaleStep = 1
        this.scale = 1 + this.scaleAdd * this.scaleStep
    }

    updateMagnifiedOffset(cx, cy)
    {
        // Calculate the position within the image
        let x = cx - this.mpos.x
        let y = cy - this.mpos.y
        // clamp 0 to msize
        x = Math.min(Math.max(x, 0), this.msize.x) - this.mhalf.x
        y = Math.min(Math.max(y, 0), this.msize.y) - this.mhalf.y
        x /= this.msize.x * (this.getterIsFlipped() ? -1 : 1); y /= this.msize.y

        x *= -this.msizeScaled.x; y *= -this.msizeScaled.y

        x -= (this.msizeScaled.x - this.msize.x) * 0.5
        y -= (this.msizeScaled.y - this.msize.y) * 0.5

        this.magnification.style.backgroundPosition = `${x}px ${y}px`
    }
}

export { Magnification }