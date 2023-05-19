
class ImgParams {
    imageId
    studyTypeId
    sameFolderId
    timePlannedId

    constructor(imageId, sourceType, sameFolder, timePlanned, isFav) {
        // html ids AND GET param names
        this.imageId = imageId
        this.studyTypeId = sourceType
        this.sameFolderId = sameFolder
        this.timePlannedId = timePlanned
        this.isFavId = isFav
    }

    getParamsAsGET()
    {
        const sourceType = `${this.studyTypeId}=` + document.getElementById(this.studyTypeId).value
        const sameFolder = `${this.sameFolderId}=` + document.getElementById(this.sameFolderId).checked
        const timer      = `${this.timePlannedId}=` + document.getElementById(this.timePlannedId).getAttribute('value')
        const imageId    = `${this.imageId}=` + document.getElementById(this.imageId).textContent

        return `${sourceType}&${sameFolder}&${timer}&${imageId}`
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
    }
}