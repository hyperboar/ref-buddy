class ColorPicker
{
    imageId
    imageTag
    palletTag
    isAltPressed
    cursorSel
    frameTag

    attrHex = 'data-hex'
    attrX   = 'data-x'
    attrY   = 'data-y'
    attrGs  = 'data-gs'

    frameSize = 0

    colors = []

    constructor(imageId, imageSel, palletSel, modeOnCursorClass, frameSel)
    {
        this.imageId = imageId
        this.cursorSel = modeOnCursorClass[0] === '.' ? modeOnCursorClass.substring(1) : modeOnCursorClass
        this.imageTag = document.querySelector(imageSel)

        this.palletTag = document.querySelector(palletSel)
        this.palletTag.setAttribute(this.attrGs, '0')

        this.frameTag = document.querySelector(frameSel)
        this.frameSize = parseInt(window.getComputedStyle(this.frameTag).width.replace('px', ''))

        this.imageTag.addEventListener('click', e =>
        {
            if (!this.isAltPressed) { return }

            const rect = this.imageTag.getBoundingClientRect()

            // Get the click coordinates relative to the image
            const x = (e.pageX - this.imageTag.offsetLeft) / rect.width
            const y = (e.pageY - this.imageTag.offsetTop) / rect.height

            // Send the AJAX request using fetch and promises
            this.getColorAt(this.imageId, x, y)
        })

        // init
        document.querySelectorAll('.pallet-cell').forEach(cell =>
        {
            this.setupCellEvents(cell)
        })

        // grayscale
        document.addEventListener('keydown', e =>
        {
            if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) { return }

            if (e.code !== 'KeyG' || !this.isAltPressed) { return }
            this.toggleGrayscale()
        })
        document.addEventListener('keypress', e =>
        {
            if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) { return }

            if (e.code !== 'KeyX' || this.isAltPressed) { return }
            this.isAltPressed = true
            this.onPickerModeChanged(this.isAltPressed)
        })
        document.addEventListener('keyup', e =>
        {
            if (e.code !== 'KeyX' || !this.isAltPressed) { return }
            this.isAltPressed = false
            this.onPickerModeChanged(this.isAltPressed)
        })
    }

    onPickerModeChanged(isOn)
    {
        console.log(`picker mode ${isOn}`)
        if (isOn) {this.imageTag.classList.add(this.cursorSel)}
        else { this.imageTag.classList.remove(this.cursorSel) }
    }

    getColorAt(imageId, x, y)
    {
        return fetch(`/color-at-coord?image-id=${imageId}&x=${x}&y=${y}`)
            .then(response => response.text())
            .then(hexColor =>
            {
                this.appendColor(hexColor, x, y)
                console.log('Average color:', hexColor)
            })
            .catch(error =>
            {
                console.log('Error: ' + error)
            })
    }

    appendColor(hexColor, x, y)
    {
        const exists = this.colors.filter(c => c.getAttribute(this.attrHex) === hexColor)

        // already have this color in the list
        if (exists.length > 0)
        {
            exists[0].classList.remove('op-success')
            setTimeout(() => exists[0].classList.add('op-success'), 100)
            return
        }

        // Create a new DOM element to append
        const cell = document.createElement('div')
        cell.setAttribute(this.attrHex, hexColor)
        cell.setAttribute(this.attrX, x)
        cell.setAttribute(this.attrY, y)
        cell.classList.add('pallet-cell')
        cell.style.backgroundColor = hexColor
        cell.textContent = hexColor

        this.colors.push(cell)

        this.setupCellEvents(cell)

        const save = document.createElement('button')
        save.classList.add('pallet-save-btn', 'btn-bg-blend')
        save.addEventListener('click', (e) =>
        {
            const btn = e.currentTarget
            btn.setAttribute('disabled', true)
            btn.classList.remove('op-success', 'op-fail')

            const cell = btn.nextSibling
            const hex = cell.getAttribute(this.attrHex).replace('#', '')
            const x = cell.getAttribute(this.attrX)
            const y = cell.getAttribute(this.attrY)

            console.log(cell)
            console.log(hex)

            fetch(`/save-image-color?image-id=${this.imageId}&x=${x}&y=${y}&hex=${hex}`)
                .then(response =>
                {
                    if (!response.ok)
                    {
                        btn.removeAttribute('disabled')
                        btn.classList.add('op-fail')
                        return
                    }

                    btn.classList.add('op-success')
                    setTimeout(btn.remove(), 1000)
                })
                .catch(error =>
                {
                    btn.removeAttribute('disabled')
                    btn.classList.add('op-fail')
                    console.log('Error: ' + error)
                })
        })

        const wrap = document.createElement('div')
        wrap.classList.add('pallet-wrap')
        wrap.appendChild(save)
        wrap.appendChild(cell)

        // Append the new element to the div
        this.palletTag.appendChild(wrap)

        this.palletTag.classList.remove('vis-hide')
    }

    toggleGrayscale()
    {
        let isGs = this.isGrayscale()
        this.palletTag.setAttribute(this.attrGs, isGs ? '0' : '1')
        isGs = this.isGrayscale()

        // switch colors
        Array.from(this.colors).forEach(elem =>
        {
            const hex = isGs ? this.hexToGrayscale(elem.getAttribute(this.attrHex)) : elem.getAttribute(this.attrHex)
            elem.style.backgroundColor = hex
            elem.textContent = hex
        })
    }

    isGrayscale()
    {
        return parseInt(this.palletTag.getAttribute(this.attrGs)) > 0
    }

    hexToGrayscale(hexColor) {
        // Remove the "#" symbol from the hex color
        hexColor = hexColor.replace("#", "")

        // Convert the hex color to RGB values
        const red = parseInt(hexColor.substr(0, 2), 16)
        const green = parseInt(hexColor.substr(2, 2), 16)
        const blue = parseInt(hexColor.substr(4, 2), 16)

        // Calculate the grayscale value using the formula
        const grayscaleValue = Math.round(0.299 * red + 0.587 * green + 0.114 * blue)

        // Convert the grayscale value to a hex color
        return "#" + grayscaleValue.toString(16).padStart(2, "0").repeat(3)
    }

    setupCellEvents(cell)
    {
        cell.addEventListener('click', e =>
        {
            const elem = e.currentTarget
            const content = e.currentTarget.textContent
            document.copyToClipboard(content, () =>
            {
                elem.classList.remove('op-success')
                setTimeout(() => elem.classList.add('op-success'), 100)
            })
        })

        cell.addEventListener('mouseenter', () =>
        {
            this.placeFrame(cell)
            this.frameTag.classList.remove('vis-hide')
        })

        cell.addEventListener('mouseleave', () =>
        {
            this.frameTag.classList.add('vis-hide')
        })
    }

    placeFrame(cell)
    {
        const normalizedX = parseFloat(cell.getAttribute(this.attrX))
        const normalizedY = parseFloat(cell.getAttribute(this.attrY))

        const imgRect = this.imageTag.getBoundingClientRect()

        const x = normalizedX * imgRect.width  + this.imageTag.offsetLeft
        const y = normalizedY * imgRect.height + this.imageTag.offsetTop

        // Position the frame element
        this.frameTag.style.left = x - this.frameSize  * 0.5 + 'px'
        this.frameTag.style.top  = y - this.frameSize * 0.5 + 'px'

        console.log(this.frameSize)
    }
}

