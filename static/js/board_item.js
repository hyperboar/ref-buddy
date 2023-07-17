
const DraggableMixin =
{
    kClassDraggable: 'draggable',

    left:0,
    top:0,

    _mvNode: null,
    _offsetX: 0,
    _offsetY: 0,

    // "virtual methods"
    onMoveCompleted: function(left, top) { throw new Error('Not implemented') },
    isDragAllowed: function() { throw new Error('Not implemented') },

    initDraggable: function(node)
    {
        this._mvNode = node

        this._mvNode.classList.add(this.kClassDraggable)

        this._tmp_startDrag = (event) => this.startDrag(event)
        this._tmp_drag      = (event) => this.drag(event)
        this._tmp_stopDrag  = (event) => this.stopDrag(event)

        this._mvNode.addEventListener("mousedown",  this._tmp_startDrag)
        this._mvNode.addEventListener("touchstart", this._tmp_startDrag, {passive: false})
    },

    setPosition: function(x, y)
    {
        this.left = x
        this.top = y

        this._mvNode.style.left = `${this.left}px`
        this._mvNode.style.top  = `${this.top}px`
    },

    startDrag: function(e)
    {
        if (!this.isDragAllowed()) { return }

        e.preventDefault()

        if (e.type === "touchstart")
        {
            this._offsetX = e.touches[0].clientX - this._mvNode.offsetLeft
            this._offsetY = e.touches[0].clientY - this._mvNode.offsetTop
            window.addEventListener("touchmove", this._tmp_drag, {passive: false})
            window.addEventListener("touchend", this._tmp_stopDrag)
        }
        else
        {
            this._offsetX = e.clientX - this._mvNode.offsetLeft
            this._offsetY = e.clientY - this._mvNode.offsetTop
            window.addEventListener("mousemove", this._tmp_drag)
            window.addEventListener("mouseup", this._tmp_stopDrag)
        }
    },

    drag: function(e)
    {
        e.preventDefault()

        if (e.type === "touchmove")
        {
            this.setPosition(
                e.touches[0].clientX - this._offsetX,
                e.touches[0].clientY - this._offsetY)
        }
        else
        {
            this.setPosition(
                e.clientX - this._offsetX,
                e.clientY - this._offsetY)
        }
    },

    stopDrag: function(e)
    {
        if (e.type === "touchend")
        {
            window.removeEventListener("touchmove", this._tmp_drag)
            window.removeEventListener("touchend", this._tmp_stopDrag)
        }
        else
        {
            window.removeEventListener("mousemove", this._tmp_drag)
            window.removeEventListener("mouseup", this._tmp_stopDrag)
        }

        this.left = parseInt(this._mvNode.style.left)
        this.top = parseInt(this._mvNode.style.top)

        this.onMoveCompleted(this.left, this.top)
    }
}

const ScalableMixin =
{
    scale: 1.0,

    _node: null,
    _startDistance: 0,
    _startScale:1.0,

    // "virtual methods"
    onScaleCompleted: function(scale) { throw new Error("Not implemented") },
    isScaleAllowed: function () { { throw new Error("Not implemented") } },

    // Add scale listeners to an image
    initScalable: function(node)
    {
        this._node = node
        this._tmp_wheelZoom = (e) => { this.wheelZoom(e) }
        this._tmp_startTouchScale = (e) => { this.startTouchScale(e) }
        this._tmp_touchScaleImage = (e) => { this.touchScaleImage(e) }

        node.addEventListener("wheel", this._tmp_wheelZoom, {passive: false})
        node.addEventListener("touchstart", this._tmp_startTouchScale, {passive: false})
        node.addEventListener("touchmove", this._tmp_touchScaleImage, {passive: false})
    },

    setScale: function(scale)
    {
        this.scale = scale
        this._node.style.transform = `scale(${this.scale})`
    },

    wheelZoom: function(e)
    {
        if (!this.isScaleAllowed()) { return }

        e.preventDefault()

        const node = e.currentTarget

        const zoomSpeed = 0.1
        const deltaY = e.deltaY || e.wheelDelta

        if (deltaY < 0)
        {
            this.scale = Math.min(this.scale + zoomSpeed, 10)
        }
        else
        {
            this.scale -= zoomSpeed
            this.scale = Math.max(this.scale, 0.1) // Minimum scale limit
        }

        this.setScale(this.scale)

        this.onScaleCompleted(this.scale)
    },

    startTouchScale: function(event)
    {
        if (!this.isScaleAllowed()) { return }
        if (event.touches.length < 2) { return }

        const touch1 = event.touches[0]
        const touch2 = event.touches[1]

        const dx = touch1.clientX - touch2.clientX
        const dy = touch1.clientY - touch2.clientY
        this._startDistance = Math.hypot(dx, dy)
        this._startScale = this.scale
    },

    touchScaleImage: function(event)
    {
        if (!this.isScaleAllowed()) { return }
        if (event.touches.length < 2) { return }

        const touch1 = event.touches[0]
        const touch2 = event.touches[1]

        const dx = touch1.clientX - touch2.clientX
        const dy = touch1.clientY - touch2.clientY
        const distance = Math.hypot(dx, dy)

        this.scale = (distance / this._startDistance) * this._startScale
        this.scale = Math.max(this.scale, 0.1) // Min scale limit
        this.scale = Math.min(this.scale, 10) // Max scale limit

        this.setScale(this.scale)

        this.onScaleCompleted(this.scale)
    }
}

/**
 * Renders image on the board, and calls this.onRenderCompleted when image is loaded.
 * @type {{renderImage: ImageRenderMixin.renderImage, thumb_image_path: string, full_image_path: string, onRenderCompleted: ((function(): never)|*)}}
 */
const ImageRenderMixin =
{
    thumb_image_path: 'Not assigned',
    full_image_path:  'Not assigned',

    onRenderCompleted: function()
    {
        throw new Error("Not implemented")
    },
    renderImage: function()
    {
        const image = new Image()
        image.src = this.thumb_image_path
        image.onload = () => this.onRenderCompleted(image)
    }
}

/**
 * Opens image in a new tab for study.
 * @type {{initStudy: GoToImageStudyMixin.initStudy}}
 */
const GoToImageStudyMixin =
{
    // "virtual methods"
    isStudyAllowed: function () { throw new Error('Not implemented') },

    initStudy: function(image)
    {
        image.addEventListener('click', (e) =>
        {
            if (!this.isStudyAllowed()) { return }

            const url = image.getAttribute('data-study')
            window.open(url, '_blank')
        })
    }
}

/**
 * Removes the item from the board.
 * @type {{initRemove: RemoveItemMixin.initRemove, remove_url: string}}
 */
const RemoveItemMixin =
{
    remove_url: 'Not implemented',

    // "virtual methods"
    isRemoveAllowed: function () { throw new Error('Not implemented') },

    initRemove: function(image)
    {
        image.addEventListener('click', (e) =>
        {
            if (!this.isRemoveAllowed()) { return }

            // const image_id = image.getAttribute('data-id')

            image.classList.remove('op-fail')
            image.classList.add('loading')
            fetch(this.remove_url)
                .then(r =>
                {
                    if (!r.ok) { throw new Error("Image not removed") }
                    image.classList.add('vis-hide')

                    const imageClone = image.cloneNode(true)
                    image.parentNode.replaceChild(imageClone, image)
                })
                .catch(err =>
                {
                    image.classList.add('op-fail')
                    console.log(err)
                })
        })
    }
}

/**
 * Represents Image on the board, that can be dragged, scaled, removed, etc.
 */
class BoardImage
{
    data

    /**
     * @param image_data object {image_id, thumb_path, path, tr, study_url}
     */
    constructor(image_data)
    {
        this.data = image_data

        // remove mixin
        this.remove_url = this.data.remove_url

        // render image mixin
        this.thumb_image_path = this.data.thumb_path
        this.full_image_path = this.data.full_path
        this.renderImage()
    }
}
Object.assign(BoardImage.prototype, ImageRenderMixin)
Object.assign(BoardImage.prototype, GoToImageStudyMixin)
Object.assign(BoardImage.prototype, RemoveItemMixin)
Object.assign(BoardImage.prototype, DraggableMixin)
Object.assign(BoardImage.prototype, ScalableMixin)

BoardImage.prototype.onRenderCompleted = function(image)
{
    image.id = `image-${this.data.image_id}`
    image.setAttribute('data-id', this.data.image_id)
    image.setAttribute('data-study', this.data.study_url)

    image.classList.add('image')

    this.initRemove(image)
    this.initStudy(image)
    this.initDraggable(image)
    this.setPosition(this.data.tr.tx, this.data.tr.ty)
    this.initScalable(image)
    this.setScale(this.data.tr.s)

    document.getElementById("board").appendChild(image)
}

BoardImage.prototype.onMoveCompleted = function(left, top)
{
    const imageId =  parseInt(this.data.image_id)
    const data = boardImages[imageId]
    data.tr.tx = left
    data.tr.ty = top
    saveImageTransform(data)
}
BoardImage.prototype.isDragAllowed = function()
{
    return hotkeys.isPressed('KeyCtrl')
}

BoardImage.prototype.onScaleCompleted = function(scale)
{
    const imageId =  parseInt(this.data.image_id)
    const data = boardImages[imageId]
    data.tr.s = scale
    saveImageTransform(data)
}
BoardImage.prototype.isScaleAllowed = function()
{
    return hotkeys.isPressed('KeyCtrl')
}

BoardImage.prototype.isRemoveAllowed = function()
{
    return hotkeys.isPressed('KeyX')
}
BoardImage.prototype.isStudyAllowed = function()
{
    return hotkeys.isPressed('KeyS')
}


class BoardBoard
{
    transform = {tx:0.0, ty:0.0, rx:0.0, ry:0.0, s:1.0}
    board = null

    constructor()
    {
        this.board = document.getElementById("board")

        this.initDraggable(this.board)
        this.setPosition(100, 0)
        this.initScalable(this.board)
        this.setScale(1)
    }
}
Object.assign(BoardBoard.prototype, DraggableMixin)
Object.assign(BoardBoard.prototype, ScalableMixin)

BoardBoard.prototype.onMoveCompleted = function(left, top)
{
    this.transform.tx = left
    this.transform.ty = top
}
BoardBoard.prototype.isDragAllowed = function()
{
    return hotkeys.isPressed('Space')
}

BoardBoard.prototype.onScaleCompleted = function(scale)
{
    this.transform.s = scale
}
BoardBoard.prototype.isScaleAllowed = function()
{
    return hotkeys.isPressed('Space')
}
