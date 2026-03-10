import {waitForCondition} from "/static/js/discover/utils.js"
import * as zipjs from "vendors/zip.js"
import {ApiImage} from "api"

class AnimPlayer
{
    _evtOnTimeUpdate = 'onupdate'
    _evtOnSeekBefore = 'onseekbefore'
    _evtOnSeekAfter  = 'onseekafter'

    _framesData = null

    // fRate
    // fRateFloat

    // KeyNext = 'ArrowRight'
    // KeyPrev = 'ArrowLeft'
    // KeyNextJump = 'ArrowUp'
    // KeyPrevJump = 'ArrowDown'

    _vFrame = null
    _vTime  = null
    _vDur   = null
    _vProg   = null

    _curFrame = 0
    _curTimeout = null
    _isPlaying = false

    _targetImage = null
    _loaded = false
    

    constructor(selContainer, selImg, selFrame, selTime, selDur, selProg)
    {
        this._container = document.querySelector(selContainer)
        this._targetImage = document.querySelector(selImg)

        this._vFrame = document.querySelector(selFrame)
        this._vTime  = document.querySelector(selTime)
        this._vDur   = document.querySelector(selDur)
        this._vProg   = document.querySelector(selProg)

        this._onTimeUpdateEvent = new CustomEvent(this._evtOnTimeUpdate, { detail: { video: this }});
        this._onSeekBeforeEvent = new CustomEvent(this._evtOnSeekBefore,  { detail: { video: this }});
        this._onSeekAfterEvent  = new CustomEvent(this._evtOnSeekAfter,  { detail: { video: this }});
    }

    loadFrames(imageId)
    {
        this._loaded = false

        return ApiImage.GetAnimInfo(imageId)
            .then(data =>
            {
                this._framesData = data
                this._vDur.textContent = this._framesData.dur

                return ApiImage.GetAnimFrames(imageId)
            })
            .then(blob =>
            {
                return new zipjs.ZipReader(new zipjs.BlobReader(blob)).getEntries()
            })
            .then(imgFiles =>
            {
                let loaded = 0
                imgFiles.forEach(async (img, idx) =>
                {
                    const blob = await img.getData(new zipjs.BlobWriter())
                    this._framesData.frames[idx]['url'] = URL.createObjectURL(blob)
                    loaded++
                })

                return waitForCondition(() => loaded >= this._framesData.frames.length)()
            })
            .then(() =>
            {
                this._loaded = true
                this._targetImage.src = this._framesData.frames[0]['url']

                return new Promise(resolve => resolve(this._framesData))
            })
    }


    _cycleAnimation()
    {
        this.seekFrame(this._curFrame)

        this._curTimeout = setTimeout(() =>
        {
            this._curFrame = (this._curFrame + 1) % this._framesData.frames.length
            this._cycleAnimation()
        }, this._framesData.frames[this._curFrame].dur)
    }

    get node()
    {
        return this._container
    }

    get paused()
    {
        return !this._isPlaying
    }

    pause()
    {
        if (this.paused) return

        clearTimeout(this._curTimeout)
        this._isPlaying = false
    }

    play()
    {
        if (!this._loaded) return

        if (!this.paused) return
        this._isPlaying = true
        this._cycleAnimation()
    }

    togglePlay()
    {
        if (!this.paused) this.pause()
        else this.play()
    }

    move(dir)
    {
        this.pause()

        this.seekFrame(this._curFrame + dir)
    }

    _updateStats()
    {
        this._vFrame.textContent = `${this._curFrame}`
        this._vTime.textContent = `${this._framesData.frames[this._curFrame].dur}`
        this._vProg.textContent = `${Math.floor(this._curFrame/this._framesData.frames.length * 100)}`
    }

    //#region Forwarding

    get currentTime()
    {
        return this._curFrame
    }

    set currentTime(value)
    {
        // this.video.currentTime = value
        console.log('cant set currentTime for animation yet')
    }

    // addEventListener(eventType, callback)
    // {
    //     this.video.addEventListener(eventType, callback)
    // }

    //#endregion Forwarding


    // getFrameByTime(time)
    // {
    //     return Math.round(time * this.fRate)
    // }

    get frame()
    {
        return this._curFrame
    }

    set frame(value)
    {
        this.seekFrame(value)
    }

    get currentFrameUrl()
    {
        return this._framesData.frames[this._curFrame]['url']
    }

    // seekTime(value)
    // {
    //     // this.onSeekBefore(this)
    //     this.video.dispatchEvent(this._onSeekBeforeEvent)
    //     this.video.currentTime = value
    // }

    seekFrame(value)
    {
        this._curFrame = (this._framesData.frames.length + value) % this._framesData.frames.length
        this._targetImage.src = this._framesData.frames[this._curFrame]['url']

        this._updateStats()

        this._container.dispatchEvent(this._onTimeUpdateEvent)
    }
}


export { AnimPlayer }