
class ImgParams {
    imageId
    studyTypeId
    sameFolderId
    timePlannedId
    minRatingId

    constructor(imageId, sourceType, sameFolder, timePlanned, isFav, minRating) {
        // html ids AND GET param names
        this.imageId = imageId
        this.studyTypeId = sourceType
        this.sameFolderId = sameFolder
        this.timePlannedId = timePlanned
        this.isFavId = isFav
        this.minRatingId = minRating
    }

    getParamsAsGET()
    {
        const sourceType = `${this.studyTypeId}=` + document.getElementById(this.studyTypeId).value
        const sameFolder = `${this.sameFolderId}=` + document.getElementById(this.sameFolderId).checked
        const timer      = `${this.timePlannedId}=` + document.getElementById(this.timePlannedId).getAttribute('value')
        const imageId    = `${this.imageId}=` + document.getElementById(this.imageId).textContent
        const rating     = `${this.minRatingId}=` + document.getElementById(this.minRatingId).value

        // tags, temporary
        let queryString = window.location.href.split('?')[1]
        let params = new URLSearchParams(queryString)
        const tagsValues = params.get('tags') || ''
        const tags = `tags=${tagsValues}`

        return `${sourceType}&${sameFolder}&${timer}&${imageId}&${rating}&${tags}`
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
    }
}