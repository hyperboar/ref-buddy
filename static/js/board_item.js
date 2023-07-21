
const DraggableMixin =
{
    kNoInteractionClass:'inter-disable',
    kClassDraggable: 'draggable',

    left:0,
    top:0,

    _mvNode: null,
    _offsetX: 0,
    _offsetY: 0,

    _enabledMv: true,

    // "virtual methods"
    onMoveCompleted: function(left, top) { throw new Error('Not implemented') },
    isDragAllowed: function() { throw new Error('Not implemented') },

    initDraggable: function(node, proxyNode = null)
    {
        this._mvNode = node
        this._mvInter = proxyNode === null ? node : proxyNode

        this._mvNode.classList.add(this.kClassDraggable)
        this._mvInter.classList.add(this.kClassDraggable)

        this._tmp_startDrag = (event) => this.startDrag(event)
        this._tmp_drag      = (event) => this.drag(event)
        this._tmp_stopDrag  = (event) => this.stopDrag(event)

        this._mvInter.addEventListener("mousedown",  this._tmp_startDrag)
        this._mvInter.addEventListener("touchstart", this._tmp_startDrag, {passive: false})
    },

    setMovableEnabled(on)
    {
        if (this._enabledMv === on) { return }
        this._enabledMv = on

        if (on)
        {
            this._mvNode.classList.remove(this.kNoInteractionClass)
        }
        else
        {
            this._mvNode.classList.add(this.kNoInteractionClass)
        }
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
    kNoInteractionClass:'inter-disable',
    kMinScale: 0.3,
    kMaxScale: 7.0,

    scale: 1.0,

    _sclNode: null,
    _sclProxy: null,
    _startDistance: 0,
    _startScale:1.0,
    _wheelStepFactor:0.1,

    _enabledScl:true,


    // "virtual methods"
    onScaleCompleted: function(scale) { throw new Error("Not implemented") },
    isScaleAllowed: function () { { throw new Error("Not implemented") } },

    // Add scale listeners to an image
    initScalable: function(node, proxyNode = null)
    {
        this._sclNode = node
        this._sclInter = proxyNode === null ? node : proxyNode

        this._tmp_wheelZoom = (e) => { this.wheelZoom(e) }
        this._tmp_startTouchScale = (e) => { this.startTouchScale(e) }
        this._tmp_touchScaleImage = (e) => { this.touchScaleImage(e) }

        this._sclInter.addEventListener("wheel", this._tmp_wheelZoom, {passive: false})
        this._sclInter.addEventListener("touchstart", this._tmp_startTouchScale, {passive: false})
        this._sclInter.addEventListener("touchmove", this._tmp_touchScaleImage, {passive: false})
    },

    setScalableEnabled(on)
    {
        if (this._enabledScl === on) { return }
        this._enabledScl = on

        if (on)
        {
            this._sclNode.classList.remove(this.kNoInteractionClass)
        }
        else
        {
            this._sclNode.classList.add(this.kNoInteractionClass)
        }
    },

    setScale: function(scale)
    {
        this.scale = scale
        this._sclNode.style.transform = `scale(${this.scale})`
    },

    wheelZoom: function(e)
    {
        if (!this.isScaleAllowed()) { return }

        e.preventDefault()

        const deltaY = e.deltaY || e.wheelDelta

        if (deltaY < 0)
        {
            this.scale = Math.min(this.scale * (1.0 + this._wheelStepFactor), this.kMaxScale)
        }
        else
        {
            this.scale *= (1.0 - this._wheelStepFactor)
            this.scale = Math.max(this.scale, this.kMinScale) // Minimum scale limit
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
        this.scale = Math.max(this.scale, this.kMinScale) // Min scale limit
        this.scale = Math.min(this.scale, this.kMaxScale) // Max scale limit

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

    _imRNode: null,

    isRenderHigh: false,


    // "virtual methods"
    onRenderCompleted: function() { throw new Error("Not implemented") },

    /**
     * Renders THUMB of an image.
     */
    renderImage: function()
    {
        this._imRNode = new Image()
        this._imRNode.src = this.thumb_image_path
        this._imRNode.onload = () =>
        {
            this._imRNode.onload = null
            this._imRNode.style.width = `${this._imRNode.naturalWidth}px`;
            this._imRNode.style.height = `${this._imRNode.naturalHeight}px`;

            this.onRenderCompleted(this._imRNode)
        }
    },

    /**
     * Replaces THUMB with full resolution image.
     */
    renderFullImage: function()
    {
        const full = new Image()
        full.src = this.full_image_path
        full.onload = () =>
        {
            this._imRNode.src = this.full_image_path
            this.isRenderHigh = true
        }
    }
}

const VisibilityMixin =
{
    _visNode: null,
    _isDirty: true,

    initVisibility: function(node)
    {
        this._visNode = node
    },

    isVisible: function ()
    {
        const rect = this._visNode.getBoundingClientRect()
        const vh = window.innerHeight
        const vw = window.innerWidth

        return rect.bottom < 0 || rect.top > vh || rect.left < 0 || rect.right > vw
    },

    setVisDirty: function() { this._isDirty = true },

    sizeToViewport: function()
    {
        const rect = this._visNode.getBoundingClientRect()
        return [rect.width/window.innerWidth, rect.height/window.innerHeight]
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

    initRemove: function(node)
    {
        node.addEventListener('click', (e) =>
        {
            if (!this.isRemoveAllowed()) { return }

            node.classList.remove('op-fail')
            node.classList.add('loading')
            fetch(this.remove_url)
                .then(r =>
                {
                    if (!r.ok) { throw new Error("Node not removed") }
                    node.classList.add('vis-hide')

                    const clone = node.cloneNode(true)
                    node.parentNode.replaceChild(clone, node)
                })
                .catch(err =>
                {
                    node.classList.add('op-fail')
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
    kHighResThreshold = 0.2

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

    checkFullRes()
    {
        if (!this.isRenderHigh && this.isVisible()) { return }

        const p = this.sizeToViewport()
        if (p[0] < this.kHighResThreshold && p[1] < this.kHighResThreshold) { return }

        this.isRenderHigh = true
        this.renderFullImage()
    }
}
Object.assign(BoardImage.prototype, ImageRenderMixin)
Object.assign(BoardImage.prototype, VisibilityMixin)
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

    this.initVisibility(image)
    this.initRemove(image)
    this.initStudy(image)
    this.initDraggable(image)
    this.setPosition(this.data.tr.tx, this.data.tr.ty)
    this.initScalable(image)
    this.setScale(this.data.tr.s)

    document.getElementById("board").appendChild(image)

    this.checkFullRes()
}

BoardImage.prototype.onMoveCompleted = function(left, top)
{
    const imageId =  parseInt(this.data.image_id)
    const data = boardImages[imageId]
    data.tr.tx = left
    data.tr.ty = top
    saveImageTransform(data)

    this.setVisDirty()
    this.checkFullRes()
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

    this.setVisDirty()
    this.checkFullRes()
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
        this.boardInteract = document.querySelector(".board-interact-bg")

        this.initDraggable(this.board, this.boardInteract)
        this.setPosition(0, 0)
        this.initScalable(this.board, this.boardInteract)
        this.setScale(1)
    }
}
Object.assign(BoardBoard.prototype, DraggableMixin)
Object.assign(BoardBoard.prototype, ScalableMixin)

BoardBoard.prototype.onMoveCompleted = function(left, top)
{
    this.transform.tx = left
    this.transform.ty = top

    const items = Object.values(boardItems);
    items.forEach(item => { item.setVisDirty(); item.checkFullRes() })
}
BoardBoard.prototype.isDragAllowed = function()
{
    return hotkeys.isPressed('Space')
}

BoardBoard.prototype.onScaleCompleted = function(scale)
{
    this.transform.s = scale

    const items = Object.values(boardItems);
    items.forEach(item => { item.setVisDirty(); item.checkFullRes() })
}
BoardBoard.prototype.isScaleAllowed = function()
{
    return hotkeys.isPressed('Space')
}
