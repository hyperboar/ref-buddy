

class TimerUpdateReason {
    static Run = 1
    static Tick = 2
}

class StudyTimer
{
    _evtTimerStart = 'timer_start'
    _evtTimerDone = 'timer_done'
    _evt5SecLeft = 'timer_5sec_left'

    _timerId = null

    _maxTime
    _curTimeText
    _maxTimeText
    _startBtn

    _isStarted
    _isPaused

    _elapsedTime

    constructor(maxTime, selTimeText, selMaxTimeText, selStartBtn)
    {
        this._maxTime = maxTime

        this._curTimeText = document.querySelector(selTimeText)
        this._maxTimeText = document.querySelector(selMaxTimeText)
        this._startBtn = document.querySelector(selStartBtn)

        this.reset()

        this._startBtn.addEventListener('click', () => this.start())
    }

    start()
    {
        if (!this._isStarted) {
            this._actual_start()
        } else {
            this._isPaused = !this._isPaused
        }

        this._updateUI(TimerUpdateReason.Run)
    }

    _actual_start() {
        if (this._isStarted) return

        this._isStarted = true
        this._isPaused = false

        this._elapsedTime = 0
        this._timerId = setInterval(() =>
        {
            if (this._isPaused) return
            this._elapsedTime++

            this._updateUI(TimerUpdateReason.Tick)

            if (this._elapsedTime === this._maxTime)
                document.dispatchEvent(new CustomEvent(this._evtTimerDone))
            else if (this._elapsedTime === this._maxTime - 5)
                document.dispatchEvent(new CustomEvent(this._evt5SecLeft))
        }, 1000)

        document.dispatchEvent(new CustomEvent(this._evtTimerStart))
    }

    _updateUI(reason) {
        switch (reason) {
            case TimerUpdateReason.Tick:
                this._curTimeText.textContent = this._format_time(this._elapsedTime)
                break
            case TimerUpdateReason.Run:
                if (!this._isStarted) {
                    this._startBtn.textContent = 'Alga Only'
                } else {
                    if (this._isPaused) {
                        this._startBtn.textContent = 'Paused'
                    } else {
                        this._startBtn.textContent = 'Alga Only'
                    }
                }
                break
        }
    }

    _format_time(seconds)
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
        this._isPaused = false

        this._curTimeText.textContent = this._format_time(0)
        this._maxTimeText.textContent  = this._format_time(this._maxTime)

        this._startBtn.textContent = 'Start'
    }
}

export { StudyTimer }