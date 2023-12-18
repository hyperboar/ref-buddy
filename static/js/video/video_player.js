class VideoPlayer
{
    _evtOnTimeUpdate = 'onupdate'
    _evtOnSeekBefore = 'onseekbefore'
    _evtOnSeekAfter  = 'onseekafter'

    video = null

    fRate
    fRateFloat

    KeyNext = 'ArrowRight'
    KeyPrev = 'ArrowLeft'
    KeyNextJump = 'ArrowUp'
    KeyPrevJump = 'ArrowDown'


    constructor(sel, frameRate = 24)
    {
        this.video = document.querySelector(sel)
        this.frameRate = frameRate

        this._preventDefaultEvents()

        this._onTimeUpdateEvent = new CustomEvent(this._evtOnTimeUpdate, { detail: { video: this }});
        this._onSeekBeforeEvent = new CustomEvent(this._evtOnSeekBefore,  { detail: { video: this }});
        this._onSeekAfterEvent  = new CustomEvent(this._evtOnSeekAfter,  { detail: { video: this }});

        this.video.addEventListener('timeupdate', e => { this.video.dispatchEvent(this._onTimeUpdateEvent) })
        this.video.addEventListener('seeked', e => { this.video.dispatchEvent(this._onSeekAfterEvent) })

        this.video.muted = true
        this.video.loop = true
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
            if (e.code === this.KeyPrev)
            {
                e.preventDefault()
                e.stopPropagation()
            }
            else if (e.code === this.KeyNext)
            {
                e.preventDefault()
                e.stopPropagation()
            }
            else if (e.code === this.KeyPrevJump)
            {
                e.preventDefault()
                e.stopPropagation()
            }
            else if (e.code === this.KeyNextJump)
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

    addEventListener(eventType, callback)
    {
        this.video.addEventListener(eventType, callback)
    }

    //#endregion Forwarding

    get frameRate()
    {
        return this.fRate
    }

    set frameRate(value)
    {
        this.fRate = value
        this.fRateFloat = 1. / value
    }

    getFrameByTime(time)
    {
        return Math.round(time * this.fRate)
    }

    get frame()
    {
        return this.getFrameByTime(this.video.currentTime)
    }

    set frame(value)
    {
        this.video.currentTime = value * this.fRateFloat
    }

    seekTime(value)
    {
        // this.onSeekBefore(this)
        this.video.dispatchEvent(this._onSeekBeforeEvent)
        this.video.currentTime = value
    }

    seekFrame(value)
    {
        this.seekTime(value * this.fRateFloat)
    }
}


export { VideoPlayer }