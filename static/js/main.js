

Array.prototype.remove = function(elem)
{
    const idx = this.indexOf(elem)
    // not found, adding
    if (idx !== -1)
    {
        this.splice(idx, 1)
    }
}