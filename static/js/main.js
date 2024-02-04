

Array.prototype.remove = function(elem)
{
    const idx = this.indexOf(elem)
    // not found, adding
    if (idx !== -1)
    {
        this.splice(idx, 1)
    }
}

document.copyToClipboard = function (content, onSuccess = null, onFail = null)
{
    navigator.clipboard.writeText(content)
        .then(function ()
        {
            if (onSuccess === null) { return }
            onSuccess(content)
        })
        .catch(function (error)
        {
            if (onFail === null) { return }
            onFail(content)
            console.error('Error copying content:', error)
        });
}

/**
 * Fetch url and show progress/success/fail state of it
 * @param url
 * @param target Node object that will be used to show pending progress
 */
function fetchAndSimpleFeedback(url, target)
{
    target.classList.remove('op-success', 'op-fail')
    target.classList.add('loading')

    fetch(url)
        .then(response =>
        {
            if (!response.ok) throw new Error('Network response was not ok')
            target.classList.add('op-success')
        })
        .catch(error =>
        {
            target.classList.add('op-fail')
            console.error('There was a problem with the fetch operation:', error)
        })
        .finally(() =>
        {
            target.classList.remove('loading')
        });
}

function wrapButtonFeedbackPromise(promise, target)
{
    target.classList.remove('op-success', 'op-fail')
    target.classList.add('loading')

    return promise
        .then(() =>
        {
            target.classList.add('op-success')
        })
        .catch(error =>
        {
            target.classList.add('op-fail')
            console.error('There was a problem with the fetch operation:', error)
        })
        .finally(() =>
        {
            target.classList.remove('loading')
        })
}

/**
 * Fetch remote widget and show it on screen inside of given container.<br/>
 * Also reloads javascript tag, so interactions still work and XSS is possible >_<
 * @param url
 * @param selTrigger
 * @param selContainer
 * @param onLoadSetup callback that receives container to do smth with it
 */
function simpleShowLoadableWidget(url, selTrigger, selContainer, triggerAction = (evt) => {})
{
    const trigger = document.querySelector(selTrigger)
    const container = document.querySelector(selContainer)

    let IS_LOADING = false
    let IS_LOADED  = false

    trigger.addEventListener('click', (e) =>
    {
        // loading
        if (!IS_LOADING && !IS_LOADED)
        {
            IS_LOADING = true

            trigger.classList.add('loading')
            trigger.classList.remove('op-success', 'op-fail')

            fetch(url)
                .then((r) =>
                {
                    if (!r.ok) { throw new Error('Something went wrong... not ok') }
                    return r.text()
                })
                .then((html) =>
                {
                    container.innerHTML = html

                    // load any script that was linked to original template
                    const scripts = container.querySelectorAll('script')
                    const urls = Array.from(scripts).map(s => { return {'type': s.type, 'src': s.src} })
                    scripts.forEach(s => s.remove())

                    return Promise.all(urls.map(url => loadScript(url)))
                })
                .then(() =>
                {
                    trigger.classList.add('op-success')
                })
                .catch((err) =>
                {
                    trigger.classList.add('op-fail')
                    console.log(err)
                })
                .finally(() =>
                {
                    container.classList.remove('vis-hide')
                    trigger.classList.remove('loading')

                    IS_LOADED = true
                    IS_LOADING = false

                    triggerAction(e)
                })

            return
        }

        triggerAction(e)

    }) // addListener click
}

/**
 *
 * @param scriptUrl
 * @returns {Promise<string>}
 */
function loadScript(scriptUrl)
{
    return new Promise((resolve) =>
    {
        const script = document.createElement('script')

        script.onload = () => { resolve(scriptUrl.src) }

        script.type = scriptUrl.type

        const cacheBuster = `?bust=${new Date().getTime()}`
        script.src = scriptUrl.src + cacheBuster

        document.querySelector('head').append(script)
    })
}

/**
 * Help handle hotkeys in a more generalized ways.
 */
class Hotkeys
{
    evt_down = 'hotkeyDown'
    evt_up   = 'hotkeyUp'

    pressedKeys = {}
    eventDown = null
    eventUp = null

    constructor()
    {
        this.eventDown = new CustomEvent(
            this.evt_down,
            {
                bubbles: true, // Allow event to bubble up through the DOM tree
                cancelable: true, // Allow event to be canceled
                detail: this // Optional data to pass with the event
            })

        this.eventUp = new CustomEvent(
            this.evt_up,
            {
                bubbles: true, // Allow event to bubble up through the DOM tree
                cancelable: true, // Allow event to be canceled
                detail: this // Optional data to pass with the event
            })

        document.addEventListener('keydown', (e) =>
        {
            if (e.code === 'Space') { e.preventDefault() }

            this.pressedKeys[e.code] = true

            if (e.ctrlKey)
            {
                this.pressedKeys['KeyCtrl'] = true
            }

            document.dispatchEvent(this.eventDown)
        })
        document.addEventListener('keyup', (e) =>
        {
            delete this.pressedKeys[e.code]

            if (!e.ctrlKey)
            {
                delete this.pressedKeys['KeyCtrl']
            }

            document.dispatchEvent(this.eventUp)
        })
    }

    isPressed(code)
    {
        return this.pressedKeys[code] === true
    }

    isPressedMult(codeArr)
    {
        return !Array.from(codeArr).some(code => this.pressedKeys[code] !== true)
    }

    isPressedNothing()
    {
        return Object.keys(this.pressedKeys).length === 0
    }
}

class UrlWrapper
{
    _url

    constructor(urlStr)
    {
        this.setUrl(urlStr)
    }

    setUrl(urlStr)
    {
        this._url = new URL(urlStr);
    }

    updateLocationHref()
    {
        window.history.replaceState({}, '', this._url.toString())
    }

    getFullStr()
    {
        return this._url.toString()
    }

    getSearchStr()
    {
        return this._url.searchParams.toString()
    }

    /**
     * Adds search param to the url, if there was none.
     * @returns true if parameter was added, false otherwise
     */
    probeSearch(name, defaultValue = '')
    {
        if (this._url.searchParams.has(name)) return false

        this._url.searchParams.set(name, defaultValue)
        return true
    }

    getSearch(name, defaultValue = null)
    {
        return this._url.searchParams.get(name) || defaultValue
    }

    setSearch(name, value)
    {
        this._url.searchParams.set(name, value)
    }
}

export { simpleShowLoadableWidget, loadScript, fetchAndSimpleFeedback, wrapButtonFeedbackPromise, UrlWrapper, Hotkeys }