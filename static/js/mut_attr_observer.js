/**
 * Helper class that notifies listener when attribute of an element has been changed.<br/>
 * Might not work in all browsers.
 */
class MutationAttributeObserver
{
    constructor(elem, name, callback)
    {
        const observer = new MutationObserver((mutationsList) =>
        {
            for (const mutation of mutationsList)
            {
                if (mutation.type !== 'attributes' || mutation.attributeName !== name) { return }
                console.log(`Image src changed: ${mutation.target}`);
                callback(mutation.target, mutation.oldValue)
            }
        });

        observer.observe(elem, { attributes: true });
    }
}
