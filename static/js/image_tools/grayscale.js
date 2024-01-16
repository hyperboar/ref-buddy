class ImageGrayscale
{
    images = []
    contrast = false
    level = 0

    image
    mImage // magnified
    bg

    constructor(selImg, selMag, selBg)
    {
        this.image = document.querySelector(selImg)
        this.mImage = document.querySelector(selMag)
        this.bg = document.querySelector(selBg)
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
        const contrastGrayBg = [
            'modal-bg-gray']

        this.disableAllBut(this.image, '', contrastGray)
        this.disableAllBut(this.mImage, '', contrastGray)
        this.disableAllBut(this.bg, '', contrastGrayBg)
        switch (level) {

            case 0:
                break
            case 5:
                this.toggleCssClass(this.image, contrastGray[0])
                this.toggleCssClass(this.mImage, contrastGray[0])
                this.toggleCssClass(this.bg, contrastGrayBg[0])
                break
            case 4:
                this.toggleCssClass(this.image, contrastGray[1])
                this.toggleCssClass(this.mImage, contrastGray[1])
                this.toggleCssClass(this.bg, contrastGrayBg[0])
                break
            case 3:
                this.toggleCssClass(this.image, contrastGray[2])
                this.toggleCssClass(this.mImage, contrastGray[2])
                this.toggleCssClass(this.bg, contrastGrayBg[0])
                break
            case 2:
                this.toggleCssClass(this.image, contrastGray[3])
                this.toggleCssClass(this.mImage, contrastGray[3])
                this.toggleCssClass(this.bg, contrastGrayBg[0])
                break
            case 1:
                this.toggleCssClass(this.image, contrastGray[4])
                this.toggleCssClass(this.mImage, contrastGray[4])
                this.toggleCssClass(this.bg, contrastGrayBg[0])
                break
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