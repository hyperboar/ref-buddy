class VideoPlayer
{
    onTimeUpdate = (self) => {}
    onSeekBefore = (self) => {}
    onSeekAfter  = (self) => {}


    video = null

    fRate
    fRateFloat


    constructor(sel, frameRate = 24)
    {
        this.video = document.querySelector(sel)
        this.frameRate = frameRate

        this._preventDefaultEvents()

        this.video.ontimeupdate = () => { this.onTimeUpdate(this) }
        this.video.onseeked = () => { this.onSeekAfter(this) }
    }

    _preventDefaultEvents()
    {
        this.video.addEventListener('click', e =>
        {
            e.preventDefault()
            e.stopPropagation()
        })

        this.video.addEventListener('keydown', e =>
        {
            if (e.code === 'ArrowLeft')
            {
                e.preventDefault()
                e.stopPropagation()
            }
            else if (e.code === 'ArrowRight')
            {
                e.preventDefault()
                e.stopPropagation()
            }
            else if (e.code === 'ArrowUp')
            {
                e.preventDefault()
                e.stopPropagation()
            }
            else if (e.code === 'ArrowDown')
            {
                e.preventDefault()
                e.stopPropagation()
            }
        })
    }


    //#region Forwarding

    get currentTime()
    {
        return this.video.currentTime
    }

    set currentTime(value)
    {
        this.video.currentTime = value
    }

    get paused()
    {
        return this.video.paused
    }

    play()
    {
        this.video.play()
    }

    pause()
    {
        this.video.pause()
    }

    //#endregion Forwarding

    set frameRate(value)
    {
        this.fRate = value
        this.fRateFloat = 1. / value
    }

    get frame()
    {
        return Math.round(this.video.currentTime * this.fRate)
    }

    set frame(value)
    {
        this.video.currentTime = value * this.fRateFloat
    }

    seekTime(value)
    {
        this.onSeekBefore(this)
        this.video.currentTime = value
    }

    seekFrame(value)
    {
        this.seekTime(value * this.fRateFloat)
    }
}

export { VideoPlayer }