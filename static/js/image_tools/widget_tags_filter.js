import {ApiTags} from 'api'
import {waitForCondition} from '/static/js/discover/utils.js'
import {BgOverlay} from '/static/js/bg_overlay.js'
import {UrlWrapper, isActiveTextInput} from '/static/js/main.js' // + Array.prototype.remove

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
            this._container.classList.add('hidden')
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
            if (isActiveTextInput()) return

            if (e.code === 'KeyF' && !e.shiftKey)
            {
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

        // only when gallery is present
        const g = document.querySelector('.gallery')
        if (g !== null)
        {
            this.widget.querySelector('#tags-filter-gallery-apply').addEventListener('click', () => this.applyGalleryFilter())
            this.widget.querySelector('#tags-filter-gallery-unapply').addEventListener('click', () => this.unapplyGalleryFilter())

            this.widget.querySelector('#tags-filter-gallery-apply').classList.remove('hidden')
            this.widget.querySelector('#tags-filter-gallery-unapply').classList.remove('hidden')
            this.widget.querySelector('#filter-by-name').classList.remove('hidden')
        }

        let container = this.widget.querySelector('#tagList')
        let tplItem = this._container.querySelector('#tpl-tag-item').cloneNode(true)
        tplItem.id = ''
        tplItem.classList.remove('hidden')
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
        tplItem.classList.remove('hidden')
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
        this.initSort()

        this._container.classList.remove('hidden')

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
        this.widget.classList.remove('hidden')

        this._bgOverlay.show()
    }

    hideWidget()
    {
        this.widget.focus()

        this.widget.classList.add('hidden')

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

        if (this.widget.classList.contains('hidden')) {this.showWidget()}
        else this.hideWidget()
    }

    fixUrl()
    {
        const url = new UrlWrapper(window.location.href)
        const changed =
            url.probeSearch('page', '1') +
            url.probeSearch('tags', '')

        if (changed > 0)
            url.updateLocationHref()
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

        const url = new UrlWrapper(window.location.href)
        url.setSearch('tags', encodeURIComponent(newTagsList))
        url.updateLocationHref()

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

        const url = new UrlWrapper(window.location.href)
        url.setSearch('tag-set', encodeURIComponent(curSet))
        url.updateLocationHref()

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

    initSort()
    {
        const byFn = document.querySelector('#tags-filter #sort-name')
        byFn.addEventListener('click', e =>
        {
            const btn = e.target
            let isAsc = parseInt(btn.getAttribute('data-dir'))
            this.resetSortBtns()
            btn.setAttribute('data-dir', isAsc * -1)

            this.sortBy((a, b) => isAsc * a.getAttribute('data-fn').localeCompare(b.getAttribute('data-fn')))
        })

        const byImport = document.querySelector('#tags-filter #sort-import')
        byImport.addEventListener('click', e =>
        {
            const btn = e.target
            let isAsc = parseInt(btn.getAttribute('data-dir'))
            this.resetSortBtns()
            btn.setAttribute('data-dir', isAsc * -1)

            this.sortBy((a, b) =>
            {
                const aa = parseFloat(a.getAttribute('data-tstamp'))
                const bb = parseFloat(b.getAttribute('data-tstamp'))
                if (Math.abs(aa - bb) < 0.001) return 0
                return isAsc * (aa < bb ? 1 : -1)
            })

        })

        const byRate = document.querySelector('#tags-filter #sort-rating')
        byRate.addEventListener('click', e =>
        {
            const btn = e.target
            let isAsc = parseInt(btn.getAttribute('data-dir'))
            this.resetSortBtns()
            btn.setAttribute('data-dir', isAsc * -1)

            this.sortBy((a, b) =>
            {
                const aa = parseInt(a.getAttribute('data-rt'))
                const bb = parseInt(b.getAttribute('data-rt'))
                if (aa === bb)return 0
                return isAsc * (aa < bb ? 1 : -1)
            })
        })
    }

    sortBy(funcSort)
    {
        const g = document.querySelector('.gallery')
        Array.from(g.children).sort(funcSort).forEach(ch => g.appendChild(ch))
    }

    resetSortBtns()
    {
        const byFn = document.querySelector('#tags-filter #sort-name')
        const byImport = document.querySelector('#tags-filter #sort-import')
        const byRate = document.querySelector('#tags-filter #sort-rating')

        byFn.setAttribute('data-dir', 1)
        byImport.setAttribute('data-dir', 1)
        byRate.setAttribute('data-dir', 1)
    }

    applyGalleryFilter()
    {
        const g = document.querySelector('.gallery')
        if (g === null) return

        const tagPos = this.filteredTags.filter(t => !t.startsWith('-'))
        const tagNeg = this.filteredTags.filter(t => t.startsWith('-')).map(t => t.substring(1, t.length))

        const text = this.widget.querySelector('#search-text').value.toLowerCase()

        Array.from(g.children).forEach(ov =>
        {
            ov.classList.remove('hidden')

            if (text.length > 0 && !ov.title.toLowerCase().includes(text))
            {
                ov.classList.add('hidden')
                return
            }

            const tags = [] +
                ov.querySelector('.recent-tags').textContent.split(',') +
                ov.querySelector('.tags-list').textContent.split(',')

            for(let i in tagNeg)
            {
                if (tags.includes(tagNeg[i]))
                {
                    ov.classList.add('hidden')
                    break
                }
            }
        })
    }

    unapplyGalleryFilter()
    {
        const g = document.querySelector('.gallery')
        if (g === null) return

        Array.from(g.children).forEach(ov =>
        {
            ov.classList.remove('hidden')
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