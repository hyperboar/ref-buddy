class ImageGrayscale
{
    images = []
    contrast = false
    level = 0

    targets
    // image
    // mImage // magnified
    // bg

    constructor(selectors)
    {
        this.targets = Array.from(selectors).map(sel => document.querySelector(sel))
        // this.image = document.querySelector(selImg)
        // // this.mImage = document.querySelector(selMag)
        // this.bg = document.querySelector(selBg)
    }

    get isContrast()
    {
        return this.contrast
    }

    toggleContrastKeycode(keycode)
    {
        let idx = parseInt(keycode.replace('Numpad', '').replace('Digit', ''))
        // hit 0, bring default cursor back
        this.toggleContrast(idx)
    }

    toggleGrayscale()
    {
        this.toggleContrast(5)
    }

    toggleContrast(level)
    {
        if (this.level === level || level === 0)
        {
            this.level = level = 0
            this.contrast = false
        }
        else
        {
            this.contrast = !this.contrast
            this.level = level
        }


        const contrastGray = [
            'modal-img-gray',
            'modal-img-gray-contrast-150',
            'modal-img-gray-contrast-200',
            'modal-img-gray-contrast-300',
            'modal-img-gray-contrast-1000']

        this.targets.forEach(t => this.disableAllBut(t, '', contrastGray))
        let idx = -1
        switch (level) {

            case 0:
                break
            case 5:
                idx = 0
                break
            case 4:
                idx = 1
                break
            case 3:
                idx = 2
                break
            case 2:
                idx = 3
                break
            case 1:
                idx = 4
                break
        }
        if (idx !== -1)
        {
            this.targets.forEach(t => this.toggleCssClass(t, contrastGray[idx]))
        }
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

export { ImageGrayscale }