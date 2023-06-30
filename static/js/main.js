

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