class VideoKeyProvider
{

}

class VideoKeyPlayer
{
    _keys
    _video
    _paused = true

    _currentKey

    constructor(video, keys, interval = 200)
    {
        this._video = video
        this._keys = keys
        this._interval = interval
    }

    setKeys(keys)
    {
        this._keys = keys
        this._currentKey = keys[0]
    }

    get paused()
    {
        return this._paused
    }

    play()
    {
        if (!this.paused) return
        this._paused = false

        this._video.pause()

        if (!this._currentKey) this._currentKey = this._keys[0]

        this.currentKey = this.currentKey
        this.playNextKey()
    }

    pause()
    {
        this._paused = true
    }

    get currentKey()
    {
        return this._currentKey
    }

    set currentKey(value)
    {
        this._currentKey = value
        this._video.currentTime = value.time
    }

    playNextKey()
    {
        setTimeout(() => {
            this.currentKey = this.nextKey(this.currentKey)
            if (!this.paused) this.playNextKey()
        }, this._interval)
    }

    nextKey(key)
    {
        const idx = this._keys.indexOf(key)
        if (idx === -1 || idx + 1 >= this._keys.length)
        {
            return this._keys[0]
        }

        return this._keys[idx + 1]
    }
}

class VideoKey
{
    _evtTimeClick = 'time_click'
    _evtDeleteClick = 'delete_click'

    _sel

    time
    frame
    node

    constructor(tpl, time, frame)
    {
        this.time  = time
        this.frame = frame

        this.node = tpl.cloneNode(true)

        this.node.id = 'key'
        this.node.setAttribute('data-time', time)

        this._sel = this.node.querySelector('#sel')

        this._onTimeClickEvent   = new CustomEvent(this._evtTimeClick,  { detail: { key: this }})
        this._onDeleteClickEvent = new CustomEvent(this._evtDeleteClick,  { detail: { key: this }})

        this.node.querySelector('#time').textContent = time.toFixed(2)
        this.node.querySelector('#frame').textContent = frame

        this.node.querySelector('#delete').addEventListener('click', e => this.remove(e))
        this.node.querySelector('td').addEventListener('click', e => { this.node.dispatchEvent(this._onTimeClickEvent) })
    }

    addEventListener(eventType, callback)
    {
        this.node.addEventListener(eventType, callback)
    }

    remove(e)
    {
        this.node.dispatchEvent(this._onDeleteClickEvent)
        this.node.remove()
    }

    selected(value)
    {
        if (value)
        {
            this._sel.textContent = '>'
        }
        else
        {
            this._sel.textContent = ''
        }
    }
}

export { VideoKeyProvider, VideoKey, VideoKeyPlayer }