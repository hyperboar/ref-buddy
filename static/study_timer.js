
class StudyTimer {
    maxTime;
    curTimeId;
    maxTimeId;

    constructor(maxTime, curTimeId, maxTimeId) {
        this.maxTime = maxTime;
        this.curTimeId = curTimeId;
        this.maxTimeId = maxTimeId;

        document.getElementById(curTimeId).textContent = this.format_time(0)
        document.getElementById(maxTimeId).textContent = this.format_time(maxTime)
    }

    start()
    {
        let cur = document.getElementById(this.curTimeId)
        let elapsedTime = 0
        let formatter = this.format_time
        setInterval(function ()
        {
            elapsedTime++;
            cur.textContent = formatter(elapsedTime)
        }, 1000);
    }

    format_time(seconds)
    {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      const formattedMinutes = String(minutes).padStart(2, '0');
      const formattedSeconds = String(remainingSeconds).padStart(2, '0');
      return `${formattedMinutes}:${formattedSeconds}`;
    }
}