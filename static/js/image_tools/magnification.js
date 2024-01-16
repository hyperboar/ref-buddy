class Magnification
{

    /**
     * selSourceImg is '.modal-img'
     * selTargetImg is '.magnification'
     * @param selSourceImg
     * @param selTargetImg
     * @param getterIsFlipped
     */
    constructor(selSourceImg, selTargetImg, getterIsFlipped)
    {
        // magnification
        const modalImage = document.querySelector('.modal-img')
        const magnification = document.querySelector('.magnification')
        let mhalf = {x:0, y:0}
        let msize = {x:0, y:0}
        let msizeScaled = {x:0, y:0}
        let mpos = {x:0, y:0}
        let scale = 1
        let scaleStep = 0
        const scaleAdd = 0.3
        const maxScale = 25

        let isZoomed = false

        modalImage.addEventListener('wheel', (event) =>
        {
            // Prevent the default scrolling behavior
            event.preventDefault()

            // Determine the direction of the scroll
            const delta = Math.sign(event.deltaY) // -1 for scrolling up, 1 for scrolling down

            // Scrolling up
            if (delta === 1) { scaleStep-- }
            // Scrolling down
            else if (delta === -1) { scaleStep++ }

            scaleStep = Math.min(Math.max(scaleStep, 1), maxScale)

            scale = 1 + scaleAdd * scaleStep

            isZoomed = true

            mpos.x = modalImage.getBoundingClientRect().left
            mpos.y = modalImage.getBoundingClientRect().top
            msize.x = modalImage.offsetWidth
            msize.y = modalImage.offsetHeight
            msizeScaled.x = msize.x * scale
            msizeScaled.y = msize.y * scale
            mhalf.x = msize.x * 0.5
            mhalf.y = msize.y * 0.5

            modalImage.classList.add('modal-img-darken')
            magnification.style.display = 'block'
            magnification.style.width  = `${msize.x}px`
            magnification.style.height = `${msize.y}px`

            magnification.style.backgroundImage = `url('${modalImage.src}')`
            magnification.style.backgroundSize = `${100 * scale}% auto`

            // Set the magnification container position
            magnification.style.left = `${mpos.x}px`
            magnification.style.top = `${mpos.y}px`

            updateMagnifiedOffset(event.clientX, event.clientY)
        })

        modalImage.addEventListener('mouseup', () =>
        {
            if (!isZoomed) { return }

            isZoomed = false
            modalImage.classList.remove('modal-img-darken')
            magnification.style.display = 'none'

            scaleStep = 1
            scale = 1 + scaleAdd * scaleStep
        })

        modalImage.addEventListener('mousemove', (event) =>
        {
            if (!isZoomed) { return }

            updateMagnifiedOffset(event.clientX, event.clientY)
        })

        function updateMagnifiedOffset(cx, cy)
        {
            // Calculate the position within the image
            let x = cx - mpos.x
            let y = cy - mpos.y
            // clamp 0 to msize
            x = Math.min(Math.max(x, 0), msize.x) - mhalf.x
            y = Math.min(Math.max(y, 0), msize.y) - mhalf.y
            x /= msize.x * (getterIsFlipped() ? -1 : 1); y /= msize.y

            x *= -msizeScaled.x; y *= -msizeScaled.y

            x -= (msizeScaled.x - msize.x) * 0.5
            y -= (msizeScaled.y - msize.y) * 0.5

            magnification.style.backgroundPosition = `${x}px ${y}px`
        }
    }
}

export { Magnification }