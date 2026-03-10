class Magnification
{
    _imgTarget = null
    _lastPivotPos = [0, 0]

    _deltaPos = [0, 0]
    _startPos = []

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
        this.container.addEventListener('mousedown', (evt) => this.onmousedown(evt))
        this.container.addEventListener('mouseup', (evt) => this.onmouseup(evt))
        this.container.addEventListener('mousemove', (evt) => this.onmousemove(evt))
        this.container.addEventListener('contextmenu', (evt) => this.onmouseright(evt))

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

            this.container.classList.remove('hidden')

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

        let scaleChange = this.scale
        this.scale = 1 + this.scaleAdd * this.scaleStep
        scaleChange = scaleChange / this.scale

        this.isZoomed = true

        this.msizeScaled.x = this.msize.x * this.scale
        this.msizeScaled.y = this.msize.y * this.scale * (this.ratio)
        this.mhalf.x = this.msize.x * 0.5
        this.mhalf.y = this.msize.y * 0.5

        if (this._lastPivotPos > 0)
        {
            this._lastPivotPos[0] *= scaleChange; this._lastPivotPos[1] *= scaleChange
        }


        this.magnification.style.transform = `scale(${(this.getterIsFlipped() ? -1 : 1)}, 1)`
        // this._imgTarget.style.transform = `scale(${(this.getterIsFlipped() ? -1 : 1) * this.scale}, ${this.scale})`
        // this._imgTarget.style.transform = `scale(${(this.getterIsFlipped() ? -1 : 1) * this.scale}, ${this.scale})`
        this._imgTarget.style.transform = `scale(${(this.getterIsFlipped() ? -1 : 1) * this.scale}, ${this.scale})`
    }

    onmousedown(evt)
    {
        if (!this.isZoomed) { return }
        if (evt.button !== 0) { return }

        this.isMoving = true

        this._startPos = this.absToCenter(evt.clientX, evt.clientY)
    }

    onmouseup(evt)
    {
        if (!this.isZoomed) { return }
        if (evt.button !== 0) { return }
        this.isMoving = false

        this._lastPivotPos[0] = this._lastPivotPos[0] + this._deltaPos[0]
        this._lastPivotPos[1] = this._lastPivotPos[1] + this._deltaPos[1]

        // console.log("up")
        // console.log(this._lastPivotPos)
        // console.log([this.mhalf.x * this.scale, this.mhalf.y * this.scale])
    }

    onmousemove(evt)
    {
        if (!this.isZoomed) { return }
        if (!this.isMoving) { return }

        console.log("move")
        this.updateMagnifiedOffset(evt.clientX, evt.clientY)
    }

    onmouseright(evt)
    {
        evt.preventDefault()
        evt.stopPropagation()

        this.cancelMagnification(evt)
    }

    cancelMagnification(evt)
    {
        if (!this.isZoomed) { return }

        this.isZoomed = false
        this.lastModalImage .classList.remove('modal-img-darken')
        this.container.classList.add('hidden')

        this.scaleStep = 1
        this.scale = 1 + this.scaleAdd * this.scaleStep

        this._lastPivotPos = [0, 0]
        this._deltaPos = [0, 0]
    }

    updateMagnifiedOffset(cx, cy)
    {
        // Calculate the position within the image
        // offset from top left corner or container
        const pos = this.absToCenter(cx, cy)
        this._deltaPos[0] = pos[0] - this._startPos[0]; this._deltaPos[1] = pos[1] - this._startPos[1]
        let x = this._lastPivotPos[0] + this._deltaPos[0]
        let y = this._lastPivotPos[1] + this._deltaPos[1]

        // console.log(this._lastPivotPos)
        // let x = cx
        // let y = cy

        // clamp 0 to msize
        // range shift so 0 is in the middle

        // const sSize = [this.msize.x * this.scale, this.msize.y * this.scale]
        // const sHalf = [sSize[0] * 0.5, sSize[1] * 0.5]
        //
        // x = Math.min(Math.max(x, 0), sSize[0]) - sHalf[0]
        // y = Math.min(Math.max(y, 0), sSize[1]) - sHalf[1]

        // const limitX = this.mhalf.x / this.scale
        // const limitY = this.mhalf.y / this.scale
        // x = Math.min(Math.max(x, -limitX), limitX)
        // y = Math.min(Math.max(y, -limitY), limitY)

        // x = Math.min(Math.max(x, 0), this.msize.x) - this.mhalf.x
        // y = Math.min(Math.max(y, 0), this.msize.y) - this.mhalf.y

        // const limitX = (0.7 * this.mhalf.x) / this.scale
        // const limitY = (0.7 * this.mhalf.y) / (this.scale)
        // x = Math.min(Math.max(x, -limitX), limitX)
        // y = Math.min(Math.max(y, -limitY), limitY)

        // x *= 0.5
        // y *= 0.5

        x /= this.scale//* (this.getterIsFlipped() ? -1 : 1)
        y /= this.scale

        // console.log([x,y])


        this._imgTarget.style.transform = `scale(${(this.getterIsFlipped() ? -1 : 1) * this.scale}, ${this.scale}) translate(${x}px, ${y}px)`

        // this._startPos[0] = cx; this._startPos[1] = cy;
    }

    absToCenter(absX, absY)
    {
        const sSize = [this.msize.x * this.scale, this.msize.y * this.scale]
        const sHalf = [sSize[0] * 0.5, sSize[1] * 0.5]

        let x = Math.min(Math.max(absX, 0), sSize[0]) - sHalf[0]
        let y = Math.min(Math.max(absY, 0), sSize[1]) - sHalf[1]

        return [x, y]
    }
}

export { Magnification }