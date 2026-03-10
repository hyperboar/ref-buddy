import { RateSingle } from "image_tools/rating.js";

class DiscoverPost
{
    _selImage = '.content img'
    _selStudy = '.content a'
    _selTags = '.tags'

    node
    data
    rate

    constructor(tplNode, data)
    {
        this.data = data

        this.node = tplNode.cloneNode(true)
        this.node.id = "" + data.image_id

        this.node.querySelector(this._selImage).src = data.image_url
        this.node.querySelector(this._selStudy).href = data.image_study_url

        const tags = data.tags.map(t => '#' + t.replace(' ', '_')).join(' ')
        this.node.querySelector(this._selTags).textContent = tags

        this.node.classList.remove('hidden')

        this.node.ugly_link = this

        this.rate = new RateSingle(this.data.image_id, '#image-rating', '#rate-up', '#rate-dn', 'loading', 'op-success', 'op-fail', this.node)
        this.node.querySelector('#image-rating').textContent = this.data.rating

        this.node.querySelector('#rate-up').addEventListener('click', e => this.pingLastActive(e))
        this.node.querySelector('#rate-dn').addEventListener('click', e => this.pingLastActive(e))
    }

    pingLastActive(e)
    {
        fetch(`/discover-last-active/${this.data.image_id}/`)
    }
}

export { DiscoverPost }