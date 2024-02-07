import {ApiImage} from 'api'
import {isActiveTextInput} from '/static/js/main.js'

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
    attrClrId = 'data-clr-id'
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

            this.getColorAt(this.imageId, x, y)
        })

        // init
        document.querySelectorAll('.pallet-cell').forEach(cell =>
        {
            this.colors.push(cell)
            this.setupCellEvents(cell)
        })

        this.initializeHotkeys()
    }

    initializeHotkeys()
    {
        // grayscale
        document.addEventListener('keydown', e =>
        {
            if (isActiveTextInput()) return

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

    reset(id)
    {
        this.imageId = id

        Array.from(this.palletTag.children).forEach(item =>
        {
            item.remove()
        })

        this.colors = []

        console.log('resetting palette')
        ApiImage.GetPalette(id)
            .then(plt =>
            {
                console.log(plt)
                plt.palette.forEach(color =>
                {
                    console.log(`${color.id}:${color.hex} `)
                    this.appendColor(color.hex, color.x, color.y, color.id)
                })
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
        return ApiImage.PickColorAt(imageId, x, y)
            .then(color =>
            {
                this.appendColor(color.hex, x, y)
            })
    }

    appendColor(hexColor, x, y, id = -1)
    {
        this.palletTag.classList.remove('vis-hide')

        const exists = this.colors.filter(c => this.isSameColor(c.getAttribute(this.attrHex), hexColor))

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
        cell.setAttribute(this.attrClrId, id)
        cell.classList.add('pallet-cell')
        cell.style.backgroundColor = hexColor
        cell.textContent = this.hex2hsv2str(hexColor)

        if (this.hex2grayscale(hexColor) < 0.4)
        {
            cell.classList.add('bright-text')
        }

        this.colors.push(cell)

        this.setupCellEvents(cell)

        const wrap = document.createElement('div')
        wrap.classList.add('pallet-wrap')
        if (id > 0) wrap.appendChild(this.createRemoveBtn())
        else wrap.appendChild(this.createSaveBtn())
        wrap.appendChild(cell)

        // Append the new element to the div
        this.palletTag.appendChild(wrap)
    }

    createSaveBtn()
    {
        const newBtn = document.createElement('button')
        newBtn.classList.add('pallet-save-btn', 'btn-bg-blend2')

        newBtn.addEventListener('click', (e) =>
        {
            const btn = e.currentTarget
            btn.setAttribute('disabled', true)

            const cell = btn.nextSibling
            const hex = cell.getAttribute(this.attrHex).replace('#', '')
            const x = cell.getAttribute(this.attrX)
            const y = cell.getAttribute(this.attrY)

            btn.classList.remove('op-success', 'op-fail')
            ApiImage.PaletteColorAdd(this.imageId, hex, x, y)
                .then((newColor) =>
                {
                    console.log(newColor)
                    cell.setAttribute(this.attrClrId, newColor.id)
                    const rm = this.createRemoveBtn()
                    btn.parentNode.insertBefore(rm, cell)
                    btn.remove()
                })
                .catch(e =>
                {
                    btn.classList.add('op-fail')
                    btn.removeAttribute('disabled')
                })
                .finally(() =>
                {

                })
        })

        return newBtn
    }

    createRemoveBtn()
    {
        const newBtn = document.createElement('button')
        newBtn.classList.add('pallet-remove-btn', 'btn-bg-blend2')

        newBtn.addEventListener('click', (e) =>
        {
            const btn = e.currentTarget
            btn.setAttribute('disabled', true)

            const colorId = btn.nextSibling.getAttribute(this.attrClrId)

            btn.classList.remove('op-success', 'op-fail')
            ApiImage.PaletteColorRemove(this.imageId, colorId)
                .then((_) => {
                    btn.classList.add('op-success')
                    setTimeout(() => { btn.parentNode.remove() }, 500)
                })
                .catch(e => btn.classList.add('op-fail'))
                .finally(() =>
                {
                    btn.removeAttribute('disabled')
                    setTimeout(() => btn?.remove(), 1000) // removes btn that used to add the color
                })
        })

        return newBtn
    }

    toggleGrayscale()
    {
        let isGs = this.isGrayscale()
        this.palletTag.setAttribute(this.attrGs, isGs ? '0' : '1')
        isGs = this.isGrayscale()

        // switch colors
        Array.from(this.colors).forEach(elem =>
        {
            if (isGs)
            {
                const value = this.hex2grayscale(elem.getAttribute(this.attrHex))
                const hex = this.grayscale2hex(value)
                elem.style.backgroundColor = hex
                elem.textContent = this.hex2hsv2str(hex)//`${Math.floor((value/255)*100)}% ${hex}`
            }
            else
            {
                const hex = elem.getAttribute(this.attrHex)
                elem.style.backgroundColor = hex
                elem.textContent = this.hex2hsv2str(hex)
            }
        })
    }

    isGrayscale()
    {
        return parseInt(this.palletTag.getAttribute(this.attrGs)) > 0
    }

    /**
     * @param hexColor
     * @returns {number} range [0, 1]
     */
    hex2grayscale(hexColor)
    {
        // Remove the "#" symbol from the hex color
        hexColor = hexColor.replace("#", "")

        // Convert the hex color to RGB values
        const red = parseInt(hexColor.substr(0, 2), 16)
        const green = parseInt(hexColor.substr(2, 2), 16)
        const blue = parseInt(hexColor.substr(4, 2), 16)

        // Calculate the grayscale value using the formula
        return Math.round(0.299 * red + 0.587 * green + 0.114 * blue) / 255.0
    }

    /**
     * @param grayscaleValue range [0, 1]
     * @returns {string}
     */
    grayscale2hex(grayscaleValue)
    {
        grayscaleValue = grayscaleValue * 255.0
        // Convert the grayscale value to a hex color
        return "#" + grayscaleValue.toString(16).padStart(2, "0").repeat(3)
    }

    /**
     * source https://stackoverflow.com/a/8023734
     * @returns {{h, s, v}}
     */
    hex2hsv (hex)
    {
        hex = hex.replace('#', '')
        const r = parseInt(hex.substr(0, 2), 16)
        const g = parseInt(hex.substr(2, 2), 16)
        const b = parseInt(hex.substr(4, 2), 16)
        let rabs, gabs, babs, rr, gg, bb, h, s, v, diff, diffc, percentRoundFn;
        rabs = r / 255;
        gabs = g / 255;
        babs = b / 255;
        v = Math.max(rabs, gabs, babs),
        diff = v - Math.min(rabs, gabs, babs);
        diffc = c => (v - c) / 6 / diff + 1 / 2;
        percentRoundFn = num => Math.round(num * 100) / 100;
        if (diff === 0) {
            h = s = 0;
        } else {
            s = diff / v;
            rr = diffc(rabs);
            gg = diffc(gabs);
            bb = diffc(babs);

            if (rabs === v) {
                h = bb - gg;
            } else if (gabs === v) {
                h = (1 / 3) + rr - bb;
            } else if (babs === v) {
                h = (2 / 3) + gg - rr;
            }
            if (h < 0) {
                h += 1;
            }else if (h > 1) {
                h -= 1;
            }
        }
        return {
            h: Math.round(h * 360),
            s: percentRoundFn(s * 100),
            v: percentRoundFn(v * 100)
        };
    }

    hex2hsv2str(hex)
    {
        const hsv = this.hex2hsv(hex)
        return `H:${hsv.h} S:${hsv.s} V:${hsv.v}`
    }

    isSameColor(hexColor1, hexColor2, threshold = 10)
    {
        // Remove the "#" symbol from the hex color
        hexColor1 = hexColor1.replace("#", "")
        hexColor2 = hexColor2.replace("#", "")

        // Convert the hex color to RGB values
        const red1 = parseInt(hexColor1.substr(0, 2), 16)
        const green1 = parseInt(hexColor1.substr(2, 2), 16)
        const blue1 = parseInt(hexColor1.substr(4, 2), 16)

        const red2 = parseInt(hexColor2.substr(0, 2), 16)
        const green2 = parseInt(hexColor2.substr(2, 2), 16)
        const blue2 = parseInt(hexColor2.substr(4, 2), 16)

        const diff = Math.abs(red1 - red2) + Math.abs(green1 - green2) + Math.abs(blue1 - blue2)
        return diff < threshold
    }

    setupCellEvents(cell)
    {
        cell.addEventListener('click', e =>
        {
            const elem = e.currentTarget
            const content = e.currentTarget.getAttribute(this.attrHex)
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
    }
}

export { ColorPicker }