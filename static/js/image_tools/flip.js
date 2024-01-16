class ImageFlip
{
    flip = false
    images = []

    constructor(selImgs)
    {
        Array.from(selImgs).forEach(selImg =>
        {
            this.images.push(document.querySelector(selImg))
        })
    }

    toggleFlip()
    {
        this.setFlipped(!this.flip)

        // updateMagnifiedOffset(event.clientX, event.clientY)
    }

    setFlipped(value)
    {
        if (this.flip === value) return

        this.flip = value
        this.images.forEach(im =>
        {
            if (this.flip) {im.classList.add('image-flip')}
            else im.classList.remove('image-flip')
        })
    }

    get isFlipped()
    {
        return this.flip
    }

    resetFlip()
    {
        this.setFlipped(false)
    }
}

export { ImageFlip }