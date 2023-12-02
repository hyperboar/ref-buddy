

function imageLoader(url)
{
    return new Promise(function(resolve, reject)
    {
        try {
            const img = new Image()
            img.onload = () => { resolve(url) }
            img.onabort = () => { reject(url) }
        }
        catch (e)
        {
            reject(url)
            throw e
        }
    })
}

function waitFor(seconds)
{
    return function(arg)
    {
        return new Promise(function(resolve, reject)
        {
            setTimeout(() => resolve(arg), seconds * 1000)
        })
    }
}

// Triggers becomeVisible(target) callback when selNode becomes framed by viewport.
class TriggerOnVisible
{
    target

    constructor(selNode, becomeVisible, margin = '20px', threshold = 0.2)
    {
        this.target = document.querySelector(selNode);

        const options = {
            threshold: threshold, // Adjust this value to control how close the image needs to be to the viewport to start loading
            rootMargin: margin // Adjust this value to set a margin around the viewport
        };

        const imageObserver = new IntersectionObserver((entries, observer) =>
        {
            entries.forEach(entry =>
            {
                if (!entry.isIntersecting) { return }

                becomeVisible(this.target)
            });
        }, options)

        imageObserver.observe(this.target)
    }
}

export { imageLoader, waitFor, TriggerOnVisible }