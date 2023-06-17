/**
 * Rate for single image.
 * @see constructor
 */
class RateBase
{
    up
    down
    loadStyle
    succStyle
    failStyle

    lastBtn

    constructor(upId, downId, loadStyle, succStyle, failStyle)
    {
        this.up    = document.getElementById(upId)
        this.down  = document.getElementById(downId)
        this.loadStyle = loadStyle
        this.succStyle = succStyle
        this.failStyle = failStyle

        this.up.addEventListener('click',   () => { this.onRate(this.up, 1) })
        this.down.addEventListener('click', () => { this.onRate(this.down, -1) })
    }

    onRate(btn, rating)
    {
        this.lastBtn = btn

        this.up.setAttribute('disabled', 'true')
        this.down.setAttribute('disabled', 'true')

        this.up.classList.remove(this.loadStyle, this.succStyle, this.failStyle)
        this.down.classList.remove(this.loadStyle, this.succStyle, this.failStyle)

        btn.classList.add(this.loadStyle)
    }

    onSuccess(response)
    {
        this.lastBtn.classList.add(this.succStyle)
    }

    onFail(error)
    {
        console.error('There was a problem with the fetch operation:', error);

        this.lastBtn.classList.add(this.failStyle)
    }

    onFinal()
    {
        this.up.classList.remove(this.loadStyle)
        this.down.classList.remove(this.loadStyle)

        this.up.removeAttribute('disabled')
        this.down.removeAttribute('disabled')
    }
}

/**
 * Rate for single image.
 * @see constructor
 */
class RateSingle extends RateBase
{
    imageId
    total

    constructor(imageId, totalId, upId, downId, loadStyle, succStyle, failStyle)
    {
        super(upId, downId, loadStyle, succStyle, failStyle);

        this.imageId = imageId
        this.total = document.getElementById(totalId)
    }

    onRate(btn, rating)
    {
        super.onRate(btn, rating);

        fetch(`/add-image-rating?image-id=${this.imageId}&rating=${rating}`)
            .then(response => response.text())
            .then(data =>
            {
                this.onSuccess(data)
                this.total.innerText = data
            })
            .catch(error => this.onFail(error))
            .finally(() => this.onFinal());
    }
}

/**
 * Rate for folder with images.
 * @see constructor
 */
class RateFolder extends RateBase
{
    imageId
    total

    /**
     * @param imageId db image id
     * @param totalId label that shows operation result
     * @param upId rate up button
     * @param downId rate down button
     * @param loadStyle
     * @param succStyle
     * @param failStyle
     */
    constructor(imageId, totalId, upId, downId, loadStyle, succStyle, failStyle)
    {
        super(upId, downId, loadStyle, succStyle, failStyle);

        this.imageId = imageId
        this.total = document.getElementById(totalId)
    }

    onRate(btn, rating)
    {
        super.onRate(btn, rating);

        fetch(`/add-folder-rating?image-id=${this.imageId}&rating=${rating}`)
            .then(response => fetch(`/get-image-rating?image-id=${this.imageId}`))
            .then(response => response.text())
            .then(data =>
            {
                this.onSuccess(data)
                this.total.innerText = data
            })
            .catch(error =>
            {
                this.onFail(error)
            })
            .finally(() =>
            {
                this.onFinal()
            })
    }
}

/**
 * Rate multiple individual images at once.<br/>
 * @see setImageIds
 * Call setImageIds before processing buttons
 */
class RateMultImages extends RateBase
{
    imageIds

    /**
     * @param imageIds an array of integers
     */
    setImageIds(imageIds)
    {
        this.imageIds = imageIds
    }

    onRate(btn, rating)
    {
        super.onRate(btn, rating);

        const idsStr = selectedIds.join(',')

        fetch(`/add-mult-image-rating?image-id=${idsStr}&rating=${rating}`)
            .then(response => fetch(`/get-image-rating?image-id=${this.imageId}`))
            .then(response => response.text())
            .then(data =>
            {
                this.onSuccess(data)
                this.total.innerText = data
            })
            .catch(error =>
            {
                this.onFail(error)
            })
            .finally(() =>
            {
                this.onFinal()
            })
    }
}