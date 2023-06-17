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
    loadingStyle

    /**
     * @param imageId db image id
     * @param totalId label that shows current rating
     * @param upId rate up button
     * @param downId rate down button
     * @param loadingStyle
     */
    constructor(imageId, totalId, upId, downId, loadingStyle)
    {
        this.imageId = imageId
        this.up    = document.getElementById(upId)
        this.down  = document.getElementById(downId)
        this.total = document.getElementById(totalId)
        this.loadingStyle = loadingStyle

        this.up.addEventListener('click',   () => { this.rate(1) })
        this.down.addEventListener('click', () => { this.rate(-1) })
    }

    rate(rating)
    {
        this.up.setAttribute('disabled', 'true')
        this.down.setAttribute('disabled', 'true')

        if (rating > 0)
        {
            this.up.classList.add(this.loadingStyle)
        } else
        {
            this.down.classList.add(this.loadingStyle)
        }

        fetch(`/add-image-rating?image-id=${this.imageId}&rating=${rating}`)
            .then(response =>
            {
                if (!response.ok) throw new Error('Network response was not ok');

                response.text().then(data =>
                {
                    this.total.innerText = data
                })
            })
            .catch(error =>
            {
                console.error('There was a problem with the fetch operation:', error);
            })
            .finally(() =>
            {
                this.up.classList.remove(this.loadingStyle)
                this.down.classList.remove(this.loadingStyle)

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
    loadingStyle

    /**
     * @param imageId db image id
     * @param resultId label that shows operation result
     * @param upId rate up button
     * @param downId rate down button
     * @param loadingStyle
     */
    constructor(imageId, resultId, upId, downId, loadingStyle)
    {
        this.imageId = imageId
        this.up    = document.getElementById(upId)
        this.down  = document.getElementById(downId)
        this.result = document.getElementById(resultId)
        this.loadingStyle = loadingStyle

        this.up.addEventListener('click',   () => { this.rate(1) })
        this.down.addEventListener('click', () => { this.rate(-1) })
    }

    rate(rating)
    {
        this.up.setAttribute('disabled', 'true')
        this.down.setAttribute('disabled', 'true')

        if (rating > 0)
        {
            this.up.classList.add(this.loadingStyle)
        }
        else
        {
            this.down.classList.add(this.loadingStyle)
        }

        fetch(`/add-folder-rating?image-id=${this.imageId}&rating=${rating}`)
            .then(response =>
            {
                return fetch(`/get-image-rating?image-id=${this.imageId}`)
            })
            .then(response => response.text())
            .then(data =>
            {
                this.result.innerText = data
            })
            .catch(error =>
            {
                console.error('There was a problem with the fetch operation:', error);
            })
            .finally(() =>
            {
                this.up.classList.remove(this.loadingStyle)
                this.down.classList.remove(this.loadingStyle)

                this.up.removeAttribute('disabled')
                this.down.removeAttribute('disabled')
            });
    }
}