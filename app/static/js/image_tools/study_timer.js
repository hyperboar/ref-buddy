
class StudyTimer
{
    _evtTimerStart = 'timer_start'

    _timerId = null

    _maxTime
    _curTimeText
    _maxTimeText
    _startBtn

    _isStarted

    constructor(maxTime, selTimeText, selMaxTimeText, selStartBtn)
    {
        this._maxTime = maxTime

        this._curTimeText = document.querySelector(selTimeText)
        this._maxTimeText = document.querySelector(selMaxTimeText)
        this._startBtn = document.querySelector(selStartBtn)

        this.reset()

        this._startBtn.addEventListener('click', () => { this.start() })
    }

    start()
    {
        if (this._isStarted) {return}
        this._isStarted = true

        let elapsedTime = 0
        this._timerId = setInterval(() =>
        {
            elapsedTime++
            this._curTimeText.textContent = this.format_time(elapsedTime)
        }, 1000)

        document.dispatchEvent(new CustomEvent(this._evtTimerStart))

        this._startBtn.textContent = 'Alga Only'
        this._startBtn.setAttribute('disabled', 'true')
    }

    format_time(seconds)
    {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      const formattedMinutes = String(minutes).padStart(2, '0')
      const formattedSeconds = String(remainingSeconds).padStart(2, '0')
      return `${formattedMinutes}:${formattedSeconds}`
    }

    reset()
    {
        if (this._timerId)
        {
            clearInterval(this._timerId)
            this._timerId = null
        }

        this._isStarted = false

        this._curTimeText.textContent = this.format_time(0)
        this._maxTimeText.textContent  = this.format_time(this._maxTime)

        this._startBtn.textContent = 'Start'
        this._startBtn.removeAttribute('disabled')
    }
}

export { StudyTimer }