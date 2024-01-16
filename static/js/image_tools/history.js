class ImageHistory
{
    cursor = -1

    _ids = []

    constructor()
    {
        // load old history here
    }

    get isAtTail()
    {
        return this._ids.length - 1 === this.cursor
    }

    get pos()
    {
        return this.cursor + 1
    }

    get length()
    {
        return this._ids.length
    }

    pushToTail(id)
    {
        this._ids.push(id)
        // if (this.isAtTail) this.cursor++
    }

    moveToTail()
    {
        this.cursor = this._ids.length - 1
        console.log(`history to tail ${this.cursor}/${this._ids.length-1}  id:${this._ids[this.cursor]}`)
        return this._ids[this.cursor]
    }

    moveBack()
    {
        this.cursor = Math.max(0, this.cursor - 1)
        console.log(`history move back ${this.cursor}/${this._ids.length-1}  id:${this._ids[this.cursor]}`)
        return this._ids[this.cursor]
    }

    moveForward()
    {
        this.cursor = Math.min(this._ids.length - 1, this.cursor + 1)
        console.log(`history move fwd ${this.cursor}/${this._ids.length-1}  id:${this._ids[this.cursor]}`)
        return this._ids[this.cursor]
    }

}

export { ImageHistory }