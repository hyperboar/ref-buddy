/**
 * Rate for single image.
 * @see constructor
 */
class RateSingle
{
    imageId
    up
    down
    total
    loadStyle
    succStyle
    failStyle

    /**
     * @param imageId db image id
     * @param totalId label that shows current rating
     * @param upId rate up button
     * @param downId rate down button
     * @param loadStyle
     * @param succStyle
     * @param failStyle
     */
    constructor(imageId, totalId, upId, downId, loadStyle, succStyle, failStyle)
    {
        this.imageId = imageId
        this.up    = document.getElementById(upId)
        this.down  = document.getElementById(downId)
        this.total = document.getElementById(totalId)
        this.loadStyle = loadStyle
        this.succStyle = succStyle
        this.failStyle = failStyle

        this.up.addEventListener('click',   () => { this.rate(1) })
        this.down.addEventListener('click', () => { this.rate(-1) })
    }

    rate(rating)
    {
        this.up.setAttribute('disabled', 'true')
        this.down.setAttribute('disabled', 'true')

        this.up.classList.remove(this.loadStyle, this.succStyle, this.failStyle)
        this.down.classList.remove(this.loadStyle, this.succStyle, this.failStyle)

        const btn = rating > 0 ? this.up : this.down
        btn.classList.add(this.loadStyle)

        fetch(`/add-image-rating?image-id=${this.imageId}&rating=${rating}`)
            .then(response =>
            {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.text()
            })
            .then(data =>
            {
                this.total.innerText = data

                const btn = rating > 0 ? this.up : this.down
                btn.classList.add(this.succStyle)
            })
            .catch(error =>
            {
                console.error('There was a problem with the fetch operation:', error);

                const btn = rating > 0 ? this.up : this.down
                btn.classList.add(this.failStyle)
            })
            .finally(() =>
            {
                this.up.classList.remove(this.loadStyle)
                this.down.classList.remove(this.loadStyle)

                this.up.removeAttribute('disabled')
                this.down.removeAttribute('disabled')
            });
    }
}


/**
 * Rate for folder with images.
 * @see constructor
 */
class RateFolder
{
    imageId
    up
    down
    result
    loadStyle
    succStyle
    failStyle

    /**
     * @param imageId db image id
     * @param resultId label that shows operation result
     * @param upId rate up button
     * @param downId rate down button
     * @param loadStyle
     * @param succStyle
     * @param failStyle
     */
    constructor(imageId, resultId, upId, downId, loadStyle, succStyle, failStyle)
    {
        this.imageId = imageId
        this.up    = document.getElementById(upId)
        this.down  = document.getElementById(downId)
        this.result = document.getElementById(resultId)
        this.loadStyle = loadStyle
        this.succStyle = succStyle
        this.failStyle = failStyle

        this.up.addEventListener('click',   () => { this.rate(1) })
        this.down.addEventListener('click', () => { this.rate(-1) })
    }

    rate(rating)
    {
        this.up.setAttribute('disabled', 'true')
        this.down.setAttribute('disabled', 'true')

        this.up.classList.remove(this.loadStyle, this.succStyle, this.failStyle)
        this.down.classList.remove(this.loadStyle, this.succStyle, this.failStyle)

        const btn = rating > 0 ? this.up : this.down
        btn.classList.add(this.loadStyle)

        fetch(`/add-folder-rating?image-id=${this.imageId}&rating=${rating}`)
            .then(response =>
            {
                return fetch(`/get-image-rating?image-id=${this.imageId}`)
            })
            .then(response => response.text())
            .then(data =>
            {
                this.result.innerText = data
                const btn = rating > 0 ? this.up : this.down
                btn.classList.add(this.succStyle)
            })
            .catch(error =>
            {
                console.error('There was a problem with the fetch operation:', error)

                const btn = rating > 0 ? this.up : this.down
                btn.classList.add(this.failStyle)
            })
            .finally(() =>
            {
                this.up.classList.remove(this.loadStyle)
                this.down.classList.remove(this.loadStyle)

                this.up.removeAttribute('disabled')
                this.down.removeAttribute('disabled')
            });
    }
}