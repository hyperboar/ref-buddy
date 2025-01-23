import {waitForCondition}    from "/static/js/discover/utils.js"
import {OSInfo}    from "/static/js/main.js"

/*
Source: https://stackoverflow.com/questions/2368784/draw-on-html5-canvas-using-a-mouse
 */
class DrawCanvas
{
    kActionMove = 0
    kActionDown = 1
    kActionUp   = 2
    kHistoryLength = 50

    _imgId
    _canvas
    _ctx

    _theMediaSel
    _theMedia = null

    isDrawingMode
    _isDrawing
    _isErasing

    _resizeTarget

    _brushColors = [
        "#ffffffff",
        "#ab0649",
        "#05a3b7ff",
        "#80e81b",
    ]

    _brushSizes = [
        1,
        1, 2, 3, 4,
        8, 16, 32, 64, 128, 256
    ]

    _brushes = [] // buttons

    _selectedColor = 1
    _lineWeight = 4
    _eraseWeight = 7

    _history = []
    _totalHistoryWrites = 0
    _lastStrokeCount = 0
    _undoSeq = false
    _tmpImg = new Image()

    prevX = 0
    currX = 0
    prevY = 0
    currY = 0

    constructor(selCnvId, selResizeTarget, selTheMedia, selControls, imgId)
    {
        this._imgId = imgId
        this._canvas = document.querySelector(selCnvId)
        this._ctrls = document.querySelector(selControls)
        this._ctx = this._canvas.getContext("2d")

        this._resizeTarget = document.querySelector(selResizeTarget)

        this._theMediaSel = selTheMedia

        this.initCanvas()
        this.initControls()
        // this.restoreFromSave()

        this._lastStrokeCount = 1
        this.recordHistory()
    }

    updateCanvas(selImg)
    {
        const img = document.querySelector(selImg)

        waitForCondition(() => img.width > 0 && img.height > 0)(img).then(initImg => {
            this._canvas.width = initImg.width
            this._canvas.height = initImg.height

            this.fillMark()

            this.initResizing()
        })
    }

    this

    initCanvas()
    {
        // console.log(`initializing canvas`)

        this._canvas.addEventListener('dragstart', (evt) => {
            evt.preventDefault()
            evt.stopPropagation()
        })

        if (OSInfo.isMobile)
        {
            // mobile
            this._canvas.addEventListener("touchmove", (evt) => {this.drawByCoord(this.kActionMove, evt)}, { passive: false })
            this._canvas.addEventListener("touchstart", (evt) => {this.drawByCoord(this.kActionDown, evt)}, { passive: false })
            this._canvas.addEventListener("touchend",   (evt) => {this.drawByCoord(this.kActionUp,   evt)}, { passive: false })
            this._canvas.addEventListener("touchcancel",   (evt) => {this.drawByCoord(this.kActionUp,   evt)}, { passive: false })

            this._canvas.addEventListener('contextmenu', (evt) => {
                evt.preventDefault()
                evt.stopPropagation()
            })

            // Prevent scrolling when touching the canvas
            document.body.addEventListener("touchstart", function (e) {
                if (e.target == this._canvas) {
                    e.preventDefault()
                }
            }, {passive: false})
            document.body.addEventListener("touchend", function (e) {
                if (e.target == this._canvas) {
                    e.preventDefault()
                }
            }, {passive: false})
            document.body.addEventListener("touchmove", function (e) {
                if (e.target == this._canvas) {
                    e.preventDefault()
                }
            }, {passive: false })
                    document.body.addEventListener("touchcancel", function (e) {
                if (e.target == this._canvas) {
                    e.preventDefault()
                }
            }, {passive: false })
        }
        else
        {
            // desktop
            this._canvas.addEventListener("mousemove", (evt) => {this.drawByCoord(this.kActionMove, evt)}, false)
            this._canvas.addEventListener("mousedown", (evt) => {this.drawByCoord(this.kActionDown, evt)}, false)
            this._canvas.addEventListener("mouseup",   (evt) => {this.drawByCoord(this.kActionUp,   evt)}, false)
            this._canvas.addEventListener("mouseout",  (evt) => {this.drawByCoord(this.kActionUp,  evt)}, false)
        }

        this.setColor(this._selectedColor)
        this.setLineWeight(this._lineWeight)
    }

    initResizing()
    {
        const resizeCanvasToParent = () => {

            if (this._resizeTarget.clientWidth === 0 || this._resizeTarget.clientHeight === 0) return

            // Save current canvas content
            const tempCanvas = document.createElement('canvas')
            const tempCtx = tempCanvas.getContext('2d')
            tempCanvas.width = this._canvas.width
            tempCanvas.height = this._canvas.height
            tempCtx.drawImage(this._canvas, 0, 0)

            // Resize canvas to match parent element
            this._canvas.width = this._resizeTarget.clientWidth
            this._canvas.height = this._resizeTarget.clientHeight

            // Restore content
            this._ctx.drawImage(tempCanvas, 0, 0, this._canvas.width, this._canvas.height)
        }

        // Observe parent size changes
        const resizeObserver = new ResizeObserver(() => {
            resizeCanvasToParent()
        });

        // Start observing the parent element
        resizeObserver.observe(this._resizeTarget)
    }

    initControls()
    {
        let elem = this._ctrls.querySelector('#draw-eraser')
        elem.addEventListener("click", (evt) =>
        {
            this._isErasing = true
            this.setColor(0)
            this.updateBrushesUI(evt.target)
        })
        this._brushes.push(elem)

        elem = this._ctrls.querySelector('#draw-clear')
        elem.addEventListener("click", (evt) => { this.clear() })

        elem = this._ctrls.querySelector('#draw-weight')
        elem.value = this._lineWeight
        elem.addEventListener("change", (evt) => { this.setLineWeight(parseInt(evt.target.value)) })

        elem = this._ctrls.querySelector('#erase-weight')
        elem.value = this._eraseWeight
        elem.addEventListener("change", (evt) => { this.setEraseWeight(parseInt(evt.target.value)) })

        elem = this._ctrls.querySelector('#layer-opacity')
        elem.value = 100
        elem.addEventListener("change", (evt) => { this.setDrawLayerOpacity(parseInt(evt.target.value)) })

        elem = this._ctrls.querySelector('#orig-opacity')
        elem.value = 100
        elem.addEventListener("change", (evt) => { this.setOrigLayerOpacity(parseInt(evt.target.value)) })

        elem = this._ctrls.querySelector('#draw-undo')
        elem.addEventListener("click", (evt) => { this.undo() })

        elem = this._ctrls.querySelector('#draw-panel-hide')
        elem.addEventListener("click", (evt) => { this.toggle() })

        // color buttons
        elem = this._ctrls.querySelector('#tlp-draw-clr')
        for (let i = 1; i < this._brushColors.length; i++)
        {
            let clr = elem.cloneNode()
            clr.value = i
            clr.textContent = "C" + i
            clr.id = clr.textContent
            clr.style.backgroundColor = this._brushColors[i]
            clr.addEventListener("click", (evt) =>
            {
                this._isErasing = false
                this.updateBrushesUI(evt.target)
                this.setColor(evt.target.value)
            })
            clr.classList.remove("hidden")
            elem.before(clr)
            this._brushes.push(clr)
        }
        this.updateBrushesUI(this._brushes[1])
    }

    toggle()
    {
        this.setDrawingMode(this._canvas.classList.contains('hidden'))
    }

    setDrawingMode(isOn)
    {
        if (isOn)
        {
            this._canvas.classList.remove('hidden')
            this._ctrls.classList.remove('hidden')
            this._canvas.parentElement.parentElement.classList.add('bg-drawing')
            this.isDrawingMode = true
            document.querySelector('body').classList.add('draw-disable-touch')
        }
        else
        {
            this._canvas.classList.add('hidden')
            this._ctrls.classList.add('hidden')
            this._canvas.parentElement.parentElement.classList.remove('bg-drawing')
            this.isDrawingMode = false
            document.querySelector('body').classList.remove('draw-disable-touch')
            this._theMedia?.style.removeProperty('opacity')
        }
    }

    // 0 is eraser
    setColor(id)
    {
        this._selectedColor = id

        if (id === 0)
        {
            this._ctx.globalCompositeOperation = 'destination-out'
        }
        else
        {
            this._ctx.globalCompositeOperation = 'source-over'
        }

        this.updateWeightSlidersUI(id)
    }

    setLineWeight(w)
    {
        this._lineWeight = w

        this._ctrls.querySelector('label[for="draw-weight"] .size').textContent = this._brushSizes[w]
    }

    setEraseWeight(w)
    {
        this._eraseWeight = w

        this._ctrls.querySelector('label[for="erase-weight"] .size').textContent = this._brushSizes[w]
    }

    fillMark()
    {
        this._ctx.rect(0, 0, this._canvas.width * 0.01, this._canvas.width * 0.01)
        this._ctx.fillStyle = "#509336"
        this._ctx.fill()
    }

    clear() {
        if (!confirm("Want to clear")) return

        this._ctx.clearRect(0, 0, this._canvas.width, this._canvas.height)
    }

    updateBrushesUI(selected)
    {
        selected.classList.add('draw-selected')
        for (const b of this._brushes)
        {
            if (selected === b) continue
            b.classList.remove('draw-selected')
        }
    }

    // save()
    // {
    //     document.getElementById("canvasimg").style.border = "2px solid";
    //     var dataURL = canvas.toDataURL();
    //     document.getElementById("canvasimg").src = dataURL;
    //     document.getElementById("canvasimg").style.display = "inline";
    // }

    drawByCoord(action, evt)
    {
        evt.preventDefault()
        evt.stopPropagation()

        if (!this.isDrawingMode) return

        const interactionsCount = this.getInteractionsCount(evt, action)

        if (action === this.kActionMove && this._isDrawing)
        {
            const currCoord = this.getCoord(evt)
            this.prevX = this.currX
            this.prevY = this.currY
            this.currX = currCoord[0]
            this.currY = currCoord[1]
            this.realDraw()
        }
        else if (action === this.kActionDown && !this._isDrawing)
        {
            const currCoord = this.getCoord(evt)
            this.prevX = currCoord[0]
            this.prevY = currCoord[1]
            this.currX = currCoord[0]
            this.currY = currCoord[1]

            this._isDrawing = interactionsCount > 0
            this._lastStrokeCount = 0
        }
        else if (interactionsCount < 1 && (action === this.kActionUp))
        {
            this._isDrawing = false

            this.recordHistory()
            this._lastStrokeCount = 0
        }
    }

    realDraw()
    {
        this._ctx.beginPath();
        this._ctx.lineCap = "round";
        this._ctx.moveTo(this.prevX, this.prevY);
        this._ctx.lineTo(this.currX, this.currY);
        this._ctx.strokeStyle = this._brushColors[this._selectedColor];
        this._ctx.lineWidth = this._brushSizes[this._isErasing ? this._eraseWeight : this._lineWeight];
        this._ctx.stroke();

        this._lastStrokeCount++
    }

    recordHistory()
    {
        if (!this.isDrawingMode) return
        if (this._lastStrokeCount === 0) return

        this._undoSeq = false
        this._canvas.toBlob((blob) =>
        {
            this._history.push(blob)

            if (this._history.length < this.kHistoryLength) return
            this._history.shift()
        })

        this._totalHistoryWrites++

        // this.saveHistory()
    }

    undo()
    {
        if (!this.isDrawingMode) return
        if (this._history.length === 0) return

        // I save stroke right after it has been done, so in order to undo,
        // first I have to remove CURRENT canvas
        if (!this._undoSeq)
        {
            this._undoSeq = true
            this._history.pop()
        }

        const blob = this._history.pop()
        const url = URL.createObjectURL(blob)
        this._tmpImg.onload = () =>
        {
            URL.revokeObjectURL(url)
            this._ctx.clearRect(0, 0, this._canvas.width, this._canvas.height)
            this._ctx.drawImage(this._tmpImg, 0, 0)
        }
        this._tmpImg.src = url

        // make sure we have at least 1 element in the undo
        if (this._history.length === 0) this._history.push(blob)

        // this.saveHistory()
    }

    getCoord(evt)
    {
        const x = evt.touches ? evt.touches[0].clientX : evt.clientX;
        const y = evt.touches ? evt.touches[0].clientY : evt.clientY;
        if (OSInfo.isMobile) {

            const rect = this._canvas.getBoundingClientRect();
            return [
                x - rect.left,
                y - rect.top
        ]
        }
        else {
            const rect = this._canvas.getBoundingClientRect();
            // return [
            //     x - this._canvas.offsetLeft,
            //     y - this._canvas.offsetTop
            // ]
            return [
                x - rect.left,
                y - rect.top
            ]
        }
    }

    getInteractionsCount(evt, action)
    {
        if (OSInfo.isMobile)
        {
            return evt.touches.length
        }
        else
        {
            switch (action) {
                case this.kActionUp:
                    return 0
                default:
                    return 1
            }
        }
    }

    updateWeightSlidersUI(id)
    {
        const er = this._ctrls.querySelector('#erase-weight')
        const dr = this._ctrls.querySelector('#draw-weight')

        if (id === 0)
        {
            er.parentElement.classList.remove('hidden')
            dr.parentElement.classList.add('hidden')
        }
        else
        {
            er.parentElement.classList.add('hidden')
            dr.parentElement.classList.remove('hidden')
        }
    }

    setDrawLayerOpacity(value)
    {
        this._canvas.style.opacity = (value / 100).toString()
    }

    setOrigLayerOpacity(value)
    {
        if (this._theMedia === null)
            this._theMedia = document.querySelector(this._theMediaSel)

        this._theMedia.style.opacity = (value / 100).toString()
    }

    // saveHistory()
    // {
    //     console.log('write1 '+ this._totalHistoryWrites)
    //     if (this._totalHistoryWrites <= 1) return
    //
    //     let reader = new FileReader();
    //     reader.readAsArrayBuffer(this._history[this._history.length-1]);
    //     reader.onloadend = function ()
    //     {
    //         let base64data = btoa(String.fromCharCode.apply(null, new Uint8Array(reader.result)))
    //         localStorage.setItem(`draw_history_${this._imgId}`, base64data)
    //     }
    // }

    // restoreFromSave()
    // {
    //     const url = localStorage.getItem(`draw_history_${this._imgId}`)
    //     if (url === null) return
    //
    //     console.log('read '+ url)
    //
    //     this._tmpImg.onload = () =>
    //     {
    //         this._ctx.clearRect(0, 0, this._canvas.width, this._canvas.height)
    //         this._ctx.drawImage(this._tmpImg, 0, 0)
    //     }
    //     this._tmpImg.src = url
    // }
}

export { DrawCanvas }