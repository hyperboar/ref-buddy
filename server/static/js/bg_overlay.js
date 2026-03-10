class BgOverlay
{
    DEFAULT_HTML_ID = '#bg-overlay'
    DEFAULT_STYLE = 'bg-overlay'
    DEFAULT_ATTR = 'data-count'

    _style
    _attrUsageCount
    _selNodeId

    _node


    constructor(style = '', attrUsageCount = '', selPreferredId = '')
    {
        this._style = style === '' ? this.DEFAULT_STYLE : style
        this._attrUsageCount = attrUsageCount === '' ? this.DEFAULT_ATTR : attrUsageCount
        this._selNodeId = selPreferredId === '' ? this.DEFAULT_HTML_ID : selPreferredId

        this._node = document.querySelector(this._selNodeId)
        if (this._node == null)
        {
            this._node = document.createElement('div')
            this._node.id = this._selNodeId.replace('#', '')
            this._node.classList.add('hidden', 'bg-overlay')
            document.querySelector('body').appendChild(this._node)
        }

        this._node.addEventListener('click',  (e) =>
        {
            e.preventDefault()
            e.stopPropagation()
        })
    }

    get node()
    {
        return this._node
    }

    get count() { return parseInt(this._node.getAttribute(this._attrUsageCount) ?? '0') }
    set count(value) { this._node.setAttribute(this._attrUsageCount, value) }

    show()
    {
        if (this.count === 0) this._node.classList.remove('hidden')
        this.count++
    }

    hide()
    {
        this.count = Math.max(0, this.count - 1)
        if (this.count > 0) return

        this._node.classList.add('hidden')
    }
}

export { BgOverlay }