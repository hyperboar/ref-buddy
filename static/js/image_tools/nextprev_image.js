import {ApiImage} from 'api'

class ImageNextPrev
{
    _history

    _evtImageChangeReady = 'image_change_ready' // detail.nextId

    _imgId
    _next
    _prev
    _nextSelector



    constructor(historyRef, selImageId, selNext, selPrev, selSelector, getterFilterStr)
    {
        this._history = historyRef

        this._filterStr = getterFilterStr

        this._imgId = document.querySelector(selImageId)
        this._next = document.querySelector(selNext)
        this._prev = document.querySelector(selPrev)
        this._nextSelector = document.querySelector(selSelector)

        this._next.addEventListener('click', () => this.clickNext())
        this._prev.addEventListener('click', () => this.clickPrev())
    }

    get history()
    {
        return this._history
    }

    clickNext()
    {
        return this.pickNext('fwd', this._nextSelector.value, this._imgId.textContent)
    }

    clickPrev()
    {
        return this.pickNext('bck', this._nextSelector.value, this._imgId.textContent)
    }

    pickNext(dir, method, id, notify = true)
    {
        let fetcher = null
        if (method === 'rnd')
        {
            fetcher = this.handleNextRandom(dir, method, id)
        }
        else
        {
            fetcher = ApiImage.GetNextId(id, method, dir)
                .then(nextImg =>
                {
                    this._history.moveToTail()
                    return new Promise(resolve => resolve(nextImg))
                })
        }

        return fetcher
            .then(nextImg =>
            {
                if (notify)
                {
                    document.dispatchEvent(new CustomEvent(this._evtImageChangeReady, { detail: { nextId: nextImg.id }}))
                }

                const urlStudy = ApiImage.GetPlainUrlStudyImage()
                const oldUrl = urlStudy.url_short.replace(urlStudy.keys.image_id, id)         + '?' + this._filterStr()
                const newUrl = urlStudy.url_short.replace(urlStudy.keys.image_id, nextImg.id) + '?' + this._filterStr()

                history.pushState(null, null, oldUrl)
                history.replaceState(null, null, newUrl)

                // console.log(nextImg)
                return new Promise(resolve => resolve(nextImg))
            })
    }

    handleNextRandom(dir, method, id)
    {
        if (dir === 'fwd' && this._history.isAtTail)
        {
            return ApiImage.GetNextId(id, method, dir, this._filterStr())
                .then(nextImg =>
                {
                    console.log('history tail')
                    this._history.pushToTail(nextImg.id)
                    this._history.moveToTail()
                    return new Promise(resolve => resolve(nextImg))
                })
        }
        else if (dir === 'fwd' && !this._history.isAtTail)
        {
            return new Promise(resolve =>
            {
                return resolve({'id': this._history.moveForward()})
            })
        }
        else
        {
            return new Promise(resolve =>
            {
                return resolve({'id': this._history.moveBack()})
            })
        }
    }
}

export { ImageNextPrev }