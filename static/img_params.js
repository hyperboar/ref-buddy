
class ImgParams {
    imageId
    facingId
    sourceTypeId
    sameFolderId
    difficultyId
    timePlannedId

    constructor(imageId, facing, sourceType, sameFolder, difficulty, timePlanned, isFav) {
        // html ids AND GET param names
        this.imageId = imageId
        this.facingId = facing
        this.sourceTypeId = sourceType
        this.sameFolderId = sameFolder
        this.difficultyId = difficulty
        this.timePlannedId = timePlanned
        this.isFavId = isFav
    }

    getParamsAsGET() {
        const facing     = `${this.facingId}=` + document.getElementById(this.facingId).value
        const sourceType = `${this.sourceTypeId}=` + document.getElementById(this.sourceTypeId).value
        const sameFolder = `${this.sameFolderId}=` + document.getElementById(this.sameFolderId).checked
        const difficulty = `${this.difficultyId}=` + document.getElementById(this.difficultyId).value
        const timer      = `${this.timePlannedId}=` + document.getElementById(this.timePlannedId).textContent
        const imageId    = `${this.imageId}=` + document.getElementById(this.imageId).textContent

        return `${facing}&${sourceType}&${sameFolder}&${difficulty}&${timer}&${imageId}`
    }

    setParamsFromGET() {
        const urlParams = new URLSearchParams(window.location.search);

        document.getElementById(this.facingId).value            = urlParams.get(this.facingId)
        document.getElementById(this.sourceTypeId).value        = urlParams.get(this.sourceTypeId)
        document.getElementById(this.sameFolderId).checked      = urlParams.get(this.sameFolderId) === "true"
        document.getElementById(this.difficultyId).value        = urlParams.get(this.difficultyId)
        document.getElementById(this.timePlannedId).textContent = urlParams.get(this.timePlannedId)
    }

    getParamsFav(fav)
    {
        const imageId    = `${this.imageId}=` + document.getElementById(this.imageId).textContent
        const isFav      = `${this.isFavId}=` + fav

        return `${imageId}&${isFav}`
    }
}