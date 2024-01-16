/*
    Lazyload background-image.<br/>
    When <b>isBgImage</b> is true image path will be put into css style, otherwise into image's src attribute.<br/>
    Requires <b>data-src</b> attribute next to <b>className</b>.
 */
class ImageLazyLoad
{
    constructor(className, isBgImage, rootMargin = '100px', threshold = 0.2)
    {
        const lazyImages = document.querySelectorAll(className);

        const options = {
            threshold: threshold, // Adjust this value to control how close the image needs to be to the viewport to start loading
            rootMargin: rootMargin // Adjust this value to set a margin around the viewport
        };

        const imageObserver = new IntersectionObserver((entries, observer) =>
        {
            entries.forEach(entry =>
            {
                if (!entry.isIntersecting) { return }
                const image = entry.target;
                const src = image.getAttribute('data-src');

                if (!src) { return }

                const proxyImg = new Image()

                proxyImg.onload = () =>
                {
                    if (isBgImage)
                    {
                        image.style.backgroundImage = `url('${src}'`
                    }
                    else
                    {
                        image.setAttribute('src', src)
                    }
                }

                proxyImg.src = src

                observer.unobserve(image);
            });
        }, options);

        lazyImages.forEach(image => {
            imageObserver.observe(image);
        });
    }
}