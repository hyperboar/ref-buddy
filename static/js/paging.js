/**
 * Happened to be called twice, per pagination widget included.
 * @param btnCls
 */
function initializePaging(btnCls)
{
    document.querySelectorAll(btnCls).forEach((elem) =>
    {
        // make sure it has only one click handler
        const r = elem.getAttribute('rigged')
        if (r) { return }

        elem.setAttribute('rigged', true)
        elem.addEventListener('click', (event) =>
        {
            const btn = event.currentTarget
            const value = btn.value

            let queryString = window.location.href.split('?')[1]
            let params = new URLSearchParams(queryString)
            params.set('page', value)

            const newUrl = window.location.href.split('?')[0] + '?' + decodeURIComponent(params.toString())
            if(window.location.href === newUrl)
            {
                window.location.reload()
            }
            else
            {
                window.location.href = newUrl
            }
        })
    })
}