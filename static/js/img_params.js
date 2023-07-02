
class ImgParams {
    imageId
    sameFolderId
    timePlannedId
    minRatingId
    tagSetId

    constructor(imageId, sameFolder, timePlanned, isFav, minRating, tagSetId) {
        // html ids AND GET param names
        this.imageId = imageId
        this.sameFolderId = sameFolder
        this.timePlannedId = timePlanned
        this.isFavId = isFav
        this.minRatingId = minRating
        this.tagSetId = tagSetId

        document.getElementById(this.tagSetId).addEventListener('change', (e) =>
        {
            const curSet = e.currentTarget.value

            let full_url = window.location.href
            const pageString = full_url.split('?')[0]

            let queryString = full_url.split('?')[1]
            let params = new URLSearchParams(queryString)
            params.set('tag-set', encodeURIComponent(curSet))
            let newUrl = pageString + '?' + decodeURIComponent(params.toString())
            window.history.replaceState({}, '', newUrl)
        })
    }

    getParamsAsGET()
    {
        const sameFolder = `${this.sameFolderId}=` + document.getElementById(this.sameFolderId).checked
        const timer      = `${this.timePlannedId}=` + document.getElementById(this.timePlannedId).getAttribute('value')
        const imageId    = `${this.imageId}=` + document.getElementById(this.imageId).textContent
        const rating     = `${this.minRatingId}=` + document.getElementById(this.minRatingId).value

        // tags, temporary
        let queryString = window.location.href.split('?')[1]
        let params = new URLSearchParams(queryString)
        const tagsValues = params.get('tags') || ''
        const tags = `tags=${tagsValues}`

        // tag set, temporary
        const tagSetValue = document.getElementById(this.tagSetId).value || params.get(this.tagSetId)
        const tagset = `${this.tagSetId}=${tagSetValue}`

        return `${sameFolder}&${timer}&${imageId}&${rating}&${tags}&${tagset}`
    }

    getImgIdAsGET()
    {
        const imageId    = `${this.imageId}=` + document.getElementById(this.imageId).textContent
        return `${imageId}`
    }

    getParamsFav(fav)
    {
        const imageId    = `${this.imageId}=` + document.getElementById(this.imageId).textContent
        const isFav      = `${this.isFavId}=` + fav

        return `${imageId}&${isFav}`
    }

    getParamTagSet()
    {
        const elem = document.getElementById(this.tagSetId)
        let value = elem.value
        if (value === 'none')
        {
            let queryString = window.location.href.split('?')[1]
            let params = new URLSearchParams(queryString)
            value = params.get(this.tagSetId) || 'none'
        }
        if (value === 'none')
        {
            elem.selectedIndex = 1
            value = elem.options[1]
        }

        return value
    }

    setParamsFromGET()
    {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get(this.sameFolderId) !== null)
        {
            document.getElementById(this.sameFolderId).checked = urlParams.get(this.sameFolderId) === "true"
        }

        if (urlParams.get(this.timePlannedId) !== null)
        {
            document.getElementById(this.timePlannedId).setAttribute('value', urlParams.get(this.timePlannedId))
        }

        if (urlParams.get(this.minRatingId) !== null)
        {
            document.getElementById(this.minRatingId).setAttribute('value', urlParams.get(this.minRatingId))
        }

        if (urlParams.get(this.tagSetId) !== null)
        {
            const list = Array.from(document.getElementById(this.tagSetId).options)
            const value = this.getParamTagSet()
            document.getElementById(this.tagSetId).selectedIndex = list.findIndex(o => o.value === value)

            document.getElementById(this.tagSetId).setAttribute('value', urlParams.get(this.tagSetId))
        }
    }
}