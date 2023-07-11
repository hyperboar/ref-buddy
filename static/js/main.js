

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