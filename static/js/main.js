

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

/**
 * Fetch remote widget and show it on screen inside of given container.<br/>
 * Also reloads javascript tag, so interactions still work and XSS is possible >_<
 * @param url
 * @param triggerSelector
 * @param containerSelector
 * @param onLoadSetup callback that receives container to do smth with it
 */
function simpleShowLoadableWidget(url, triggerSelector, containerSelector, onLoadSetup = (container) => {})
{
    const trigger = document.querySelector(triggerSelector)
    const container = document.querySelector(containerSelector)

    trigger.addEventListener('click', (e) =>
    {
        // loading
        if (container.textContent === '')
        {
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
                    onLoadSetup(container)

                    const code = container.querySelector('script')
                    const text = code.textContent
                    code.remove()

                    const jsElem = document.createElement('script')
                    container.appendChild(jsElem)
                    jsElem.textContent = text

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
                })

            return
        }

        container.firstChild.classList.toggle('vis-hide')
    })
}

/**
 * Help handle hotkeys in a more generalized ways.
 */
class Hotkeys
{
    pressedKeys = {}

    constructor()
    {
        document.addEventListener('keydown', (e) =>
        {
            if (e.code === 'Space') { e.preventDefault() }

            this.pressedKeys[e.code] = true

            if (e.ctrlKey)
            {
                this.pressedKeys['KeyCtrl'] = true
            }
        })
        document.addEventListener('keyup', (e) =>
        {
            delete this.pressedKeys[e.code]

            if (!e.ctrlKey)
            {
                delete this.pressedKeys['KeyCtrl']
            }
        })
    }

    isPressed(code)
    {
        return this.pressedKeys[code] === true
    }

    isPressedMult(codeArr)
    {
        !Array.from(codeArr).some(code => this.pressedKeys[code] !== true)
    }
}