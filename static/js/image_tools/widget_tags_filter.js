import {ApiTags} from 'api'
import {waitForCondition} from '/static/js/discover/utils.js'
import {BgOverlay} from '/static/js/bg_overlay.js'
import {} from '/static/js/main.js' // Array.prototype.remove

class WidgetImageTagsFilter
{
    _containerSel
    _container
    _showBtn

    _isReloadOnApply

    _bgOverlay

    widget

    filteredTags = []

    constructor(selContainer, selShowBtn, isReloadOnApply = true)
    {
        this._isReloadOnApply = isReloadOnApply

        if (selContainer === '')
        {
            this._container = document.createElement('div')
            this._container.id = 'tag-filter-totally-not-occupied-name-' + Math.round(Math.random() * 1000)
            this._container.classList.add('vis-hide')
            document.querySelector('body').appendChild(this._container)

            this._containerSel = '#' + this._container.id
        }
        else
        {
            this._containerSel = selContainer
            this._container = document.querySelector(selContainer)
        }

        this._showBtn = document.querySelector(selShowBtn)
        this._showBtn.addEventListener('click', () => this.showWidget())

        this._bgOverlay = new BgOverlay()

        document.addEventListener('keydown', (e) =>
        {
            if (e.code === 'KeyF' && !e.shiftKey) {
                this.toggleTagsFilterDisplay()
            }
        })
    }

    get isLoaded()
    {
        return document.querySelector(`${this._containerSel} #tags-filter`) != null
    }

    loadWidget()
    {
        return ApiTags.GetImageTagFilterWidgetHtml()
            .then(textHtml =>
            {
                this._container.innerHTML = textHtml

                return Promise.all([
                    ApiTags.GetAllTags(),
                    ApiTags.GetAllTagSets(),
                    waitForCondition(() => this.isLoaded)()])
            })
            .then(data =>
            {
                const colors = data[0].colors
                const tags = data[0].tags
                tags.sort((a, d) =>
                {
                    // by color_id then by name
                    if (a.c === d.c) return a.name.localeCompare(d.name)
                    return d.c > a.c ? -1 : 1
                })
                tags.forEach((tag) =>
                {
                    tag.hex = colors[tag.c]
                })

                data[1].sort((a, b) => a.name.localeCompare(b.name))

                this.initializeWidget(tags, data[1])

                return new Promise(resolve => resolve())
            })
    }

    initializeWidget(tags, tagsets)
    {
        this.widget = document.querySelector(`${this._containerSel} #tags-filter`)

        this.widget.querySelector('#tags-filter-apply').addEventListener('click', () => this.applyFilterTag())
        this.widget.querySelector('#tags-filter-close').addEventListener('click', () => this.hideWidget())
        this._bgOverlay.node.addEventListener('click', () => this.hideWidget())

        let container = this.widget.querySelector('#tagList')
        let tplItem = this._container.querySelector('#tpl-tag-item').cloneNode(true)
        tplItem.id = ''
        tplItem.classList.remove('vis-hide')
        tags.forEach(tag =>
        {
            const node = tplItem.cloneNode(true)
            node.textContent = tag.name
            node.setAttribute('data-tag', tag.name)
            node.setAttribute('data-tag-id', tag.id)
            node.style.color = tag.hex
            container.appendChild(node)
        })

        container = this.widget.querySelector('#tag-sets')
        tplItem = this._container.querySelector('#tpl-tagset-option').cloneNode(true)
        tplItem.id = ''
        tplItem.classList.remove('vis-hide')
        tagsets.forEach(tag =>
        {
            const node = tplItem.cloneNode(true)
            node.textContent = tag.name
            node.setAttribute('data-tags', tag.tags)
            node.value = tag.alias
            container.add(node)
        })

        this.fixUrl()
        this.initTags()

        this._container.classList.remove('vis-hide')

        document.addEventListener('keydown', (e) =>
        {
            if (e.code === 'Escape' && !e.shiftKey)
            {
                this.hideWidget()
            }
        })
    }

    showWidget()
    {
        if (this.isLoaded)
        {
            this.showWidgetReal()
        }
        else
        {
            this.loadWidget().then(() => this.showWidget())
        }
    }

    showWidgetReal()
    {
        this.widget.classList.remove('vis-hide')

        this._bgOverlay.show()
    }

    hideWidget()
    {
        this.widget.classList.add('vis-hide')

        this._bgOverlay.hide()

        this.widget.querySelector('#tags-filter-apply').classList.remove('op-success', 'op-fail', 'loading')
        this.widget.querySelector('#tags-filter-close').classList.remove('op-success', 'op-fail', 'loading')
    }

    applyFilterTag()
    {
        if (!this._isReloadOnApply)
        {
            this.hideWidget()
            return
        }

        window.location.reload()
    }

    toggleTagsFilterDisplay()
    {
        if (!this.isLoaded)
        {
            this.showWidget()
            return
        }

        if (this.widget.classList.contains('vis-hide')) {this.showWidget()}
        else this.hideWidget()
    }

    fixUrl()
    {
        let url = window.location.href.replace(/#$/, "")
        if (url.indexOf('?') === -1) { url = `${url}?page=1&tags=` }
        window.history.replaceState({}, '', url)
    }

    initTags()
    {
        const ts = this.widget.querySelector('#tag-sets')
        const tagset = this.getTagSetFromUrl(window.location.href)
        ts.value = tagset
        // console.log(/tagset)

        // set actual selectedIndex
        Array.from(ts.options).forEach((o, idx) => { if (o.value === tagset) ts.selectedIndex = idx })

        // console.log(ts)
        // console.log(ts.options)
        // console.log(`idx ${ts.selectedIndex}`)

        ts.addEventListener('change', (e) => this.setTagSet(e))

        this.updateTagSetTags(ts)

        const tags = this.getTagsFromUrl(window.location.href)
        this.filteredTags = tags

        this.widget.querySelectorAll('.tag-filter').forEach(tagElem =>
        {
            let tag = tagElem.getAttribute('data-tag')

            if (this.filteredTags.includes(tag)) { this.updateTagState(tagElem, 1) }
            else if (this.filteredTags.includes('-' + tag)) { this.updateTagState(tagElem, 2) }
            else { this.updateTagState(tagElem, 0) }

            tagElem.addEventListener('click', (e) =>
            {
                this.cycleTagState(e.currentTarget)
            })

            const attr = tagElem.value
            if (!tags.includes(attr)) { return }
        })
    }

    updateTagState(tagElem, state)
    {
        tagElem.classList.remove('tag-selected-pos', 'tag-selected-neg')

        if (state === 0)
        {
        }
        else if (state === 1)
        {
            tagElem.classList.add('tag-selected-pos')
        }
        else if (state === 2)
        {
            tagElem.classList.add('tag-selected-neg')
        }

        tagElem.setAttribute('data-state', state)
    }

    toggleTag(tagElem, state)
    {
        let tag = tagElem.getAttribute('data-tag')

        console.log(`${tag}`)

        console.log(this)
        let full_url = window.location.href
        const pageString = full_url.split('?')[0]
        let ids = this.getTagsFromUrl(full_url)

        if (state === 0)
        {
            ids.remove(tag)
            ids.remove('-' + tag)
        }
        else if (state === 1)
        {
            ids.push(tag)
            ids.remove('-' + tag)
        }
        else if (state === 2)
        {
            ids.remove(tag)
            ids.push('-' + tag)
        }

        this.filteredTags = ids

        console.log(`${ids}`)

        const newTagsList = ids.join(',').replace(/^,/, "")
        let queryString = full_url.split('?')[1]
        let params = new URLSearchParams(queryString)
        params.set('tags', encodeURIComponent(newTagsList))
        let newUrl = pageString + '?' + decodeURIComponent(params.toString())
        window.history.replaceState({}, '', newUrl)

        this.updateTagState(tagElem, state)
    }

    cycleTagState(tagElem)
    {
        const state = parseInt(tagElem.getAttribute('data-state'))
        const newState = (state + 1) % 3
        this.toggleTag(tagElem, newState)
    }

    setTagSet(e)
    {
        const ts = e.currentTarget
        const curSet = ts.options[ts.selectedIndex].value

        let full_url = window.location.href
        const pageString = full_url.split('?')[0]

        let queryString = full_url.split('?')[1]
        let params = new URLSearchParams(queryString)
        params.set('tag-set', encodeURIComponent(curSet))
        let newUrl = pageString + '?' + decodeURIComponent(params.toString())
        window.history.replaceState({}, '', newUrl)

        this.updateTagSetTags(ts)
    }

    updateTagSetTags(ts)
    {
        const tags = ts.options[ts.selectedIndex].getAttribute('data-tags').split(',')

        document.querySelectorAll('.tag-filter').forEach(tagElem =>
        {
            const id = tagElem.getAttribute('data-tag-id')
            tagElem.classList.remove('tag-set-pos', 'tag-set-neg')
            if (tags.includes(id))
            {
                tagElem.classList.add('tag-set-pos')
            }
            else if (tags.includes('-' + id))
            {
                tagElem.classList.add('tag-set-neg')
            }
        })
    }

    getTagsFromUrl(url)
    {
        let full_url = url.replace(/#$/, "")
        let queryString = full_url.split('?')[1]
        let params = new URLSearchParams(queryString)
        let tags = decodeURIComponent(params.get('tags'))
        if (!tags) { tags = "" }

        return tags.split(',')
    }

    getTagSetFromUrl(url)
    {
        let full_url = url.replace(/#$/, "")
        let queryString = full_url.split('?')[1]
        let params = new URLSearchParams(queryString)
        let tags = decodeURIComponent(params.has('tag-set') ? params.get('tag-set') : 'all')
        tags = tags === '' ? 'all' : tags

        return tags
    }
}

export { WidgetImageTagsFilter }