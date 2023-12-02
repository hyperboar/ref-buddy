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

    root

    constructor(selUp, selDown, loadStyle, succStyle, failStyle, root = null)
    {
        if (root === null) this.root = document
        else this.root = root

        this.up    = this.root.querySelector(selUp)
        this.down  = this.root.querySelector(selDown)
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

    constructor(imageId, selTotal, selUp, selDown, loadStyle, succStyle, failStyle, root = null)
    {
        super(selUp, selDown, loadStyle, succStyle, failStyle, root);

        this.imageId = imageId
        this.total = this.root.querySelector(selTotal)
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
     * @param selTotal label that shows operation result
     * @param selUp rate up button
     * @param selDown rate down button
     * @param loadStyle
     * @param succStyle
     * @param failStyle
     * @param root
     */
    constructor(imageId, selTotal, selUp, selDown, loadStyle, succStyle, failStyle, root = null)
    {
        super(selUp, selDown, loadStyle, succStyle, failStyle, root);

        this.imageId = imageId
        this.total = this.root.querySelector(selTotal)
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
 * @see updateImageIds
 * Call setImageIds before processing buttons
 */
class RateMultImages extends RateBase
{
    imageIds

    /**
     * Override this method so correct ids are fetched right before the up/down click event.
     */
    updateImageIds()
    {
        throw new Error("Not implemented")
    }

    /**
     * @param imageIds an array of integers
     */
    setImageIds(imageIds)
    {
        this.imageIds = imageIds
    }

    onRate(btn, rating)
    {
        this.updateImageIds()
        if (this.imageIds.length === 0) { return }
        const idsStr = this.imageIds.join(',')

        super.onRate(btn, rating);

        fetch(`/add-mult-image-rating?image-id=${idsStr}&rating=${rating}`)
            .then(response => this.onSuccess(response))
            .catch(error => this.onFail(error))
            .finally(() => this.onFinal())
    }
}