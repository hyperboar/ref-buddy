
class ImgParams {
    imageId
    facingId
    sourceTypeId
    sameFolderId
    difficultyId
    timePlannedId

    constructor(imageId, facing, sourceType, sameFolder, difficulty, timePlanned) {
        // html ids AND GET param names
        this.imageId = imageId
        this.facingId = facing
        this.sourceTypeId = sourceType
        this.sameFolderId = sameFolder
        this.difficultyId = difficulty
        this.timePlannedId = timePlanned
    }

    getParamsAsGET() {
        const facing      = `${this.facingId}=` + document.getElementById(this.facingId).value
        const sourceType  = `${this.sourceTypeId}=` + document.getElementById(this.sourceTypeId).value
        const sameFolder  = `${this.sameFolderId}=` + document.getElementById(this.sameFolderId).checked
        const difficulty  = `${this.difficultyId}=` + document.getElementById(this.difficultyId).value
        const timer       = `${this.timePlannedId}=` + document.getElementById(this.timePlannedId).textContent
        const prevImageId = `${this.imageId}=` + document.getElementById(this.imageId).textContent

        return `${facing}&${sourceType}&${sameFolder}&${difficulty}&${timer}&${prevImageId}`
    }

    setParamsFromGET() {
        const urlParams = new URLSearchParams(window.location.search);

        console.log('this.facingId '      + urlParams.get(this.facingId))
        console.log('this.sourceTypeId '  + urlParams.get(this.sourceTypeId))
        console.log('this.sameFolderId '  + urlParams.get(this.sameFolderId))
        console.log('this.difficultyId '  + urlParams.get(this.difficultyId))
        console.log('this.timePlannedId ' + urlParams.get(this.timePlannedId))
        // console.log('this.imageId ' + urlParams.get(this.imageId))

        document.getElementById(this.facingId).value            = urlParams.get(this.facingId)
        document.getElementById(this.sourceTypeId).value        = urlParams.get(this.sourceTypeId)
        document.getElementById(this.sameFolderId).checked      = urlParams.get(this.sameFolderId) === "true"
        document.getElementById(this.difficultyId).value        = urlParams.get(this.difficultyId)
        document.getElementById(this.timePlannedId).textContent = urlParams.get(this.timePlannedId)
        // document.getElementById(this.imageId).textContent       = urlParams.get(this.imageId)
    }
}