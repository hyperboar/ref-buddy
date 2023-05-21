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

    /**
     * @param imageId db image id
     * @param totalId label that shows current rating
     * @param upId rate up button
     * @param downId rate down button
     */
    constructor(imageId, totalId, upId, downId, )
    {
        this.imageId = imageId
        this.up    = document.getElementById(upId)
        this.down  = document.getElementById(downId)
        this.total = document.getElementById(totalId)

        this.up.addEventListener('click',   () => { this.rate(1) })
        this.down.addEventListener('click', () => { this.rate(-1) })
    }

    rate(rating)
    {
        this.up.setAttribute('disabled', 'true')
        this.down.setAttribute('disabled', 'true')

        if (rating > 0)
        {
            this.up.classList.add('loading-fav')
        } else
        {
            this.down.classList.add('loading-fav')
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
                this.up.classList.remove('loading-fav')
                this.down.classList.remove('loading-fav')

                this.up.removeAttribute('disabled')
                this.down.removeAttribute('disabled')
            });
    }
}