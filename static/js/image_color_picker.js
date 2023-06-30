class ColorPicker
{
    imageId
    imageTag
    palletTag
    isAltPressed
    cursorSel

    attrHex = 'data-hex'
    attrGs = 'data-gs'

    colors = []

    constructor(imageId, imageSel, palletSel, modeOnCursorClass)
    {
        this.imageId = imageId
        this.cursorSel = modeOnCursorClass[0] === '.' ? modeOnCursorClass.substring(1) : modeOnCursorClass
        this.imageTag = document.querySelector(imageSel)

        this.palletTag = document.querySelector(palletSel)
        this.palletTag.setAttribute(this.attrGs, '0')

        this.imageTag.addEventListener('click', e =>
        {
            if (!this.isAltPressed) { return }

            const rect = this.imageTag.getBoundingClientRect();

            // Get the click coordinates relative to the image
            const x = (e.pageX - this.imageTag.offsetLeft) / rect.width
            const y = (e.pageY - this.imageTag.offsetTop) / rect.height

            // Send the AJAX request using fetch and promises
            this.getColorAt(this.imageId, x, y)
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
        return fetch(`/color-at-coord?image_id=${imageId}&x=${x}&y=${y}`)
            .then(response => response.text())
            .then(hexColor =>
            {
                this.appendColor(hexColor)
                console.log('Average color:', hexColor)
            })
            .catch(error =>
            {
                console.log('Error: ' + error)
            });
    }

    appendColor(hexColor)
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
        const newElem = document.createElement('div');
        newElem.setAttribute(this.attrHex, hexColor)
        newElem.classList.add('pallet-cell')
        newElem.style.backgroundColor = hexColor
        newElem.textContent = hexColor

        this.colors.push(newElem)

        // clipboard
        newElem.addEventListener('click', e =>
        {
            const elem = e.currentTarget
            const content = e.currentTarget.innerHTML
            navigator.clipboard.writeText(content)
                .then(function ()
                {
                    elem.classList.remove('op-success')
                    setTimeout(() => elem.classList.add('op-success'), 100)
                })
                .catch(function (error)
                {
                    console.error('Error copying content:', error)
                });
        })

        // Append the new element to the div
        this.palletTag.appendChild(newElem);
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
        hexColor = hexColor.replace("#", "");

        // Convert the hex color to RGB values
        const red = parseInt(hexColor.substr(0, 2), 16);
        const green = parseInt(hexColor.substr(2, 2), 16);
        const blue = parseInt(hexColor.substr(4, 2), 16);

        // Calculate the grayscale value using the formula
        const grayscaleValue = Math.round(0.299 * red + 0.587 * green + 0.114 * blue);

        // Convert the grayscale value to a hex color
        return "#" + grayscaleValue.toString(16).padStart(2, "0").repeat(3)
    }
}

