import {ApiTags} from 'api'
import {waitForCondition} from '/static/js/discover/utils.js'
import {BgOverlay} from "/static/js/bg_overlay.js";
import {isActiveTextInput, UrlWrapper, wrapButtonFeedbackPromise} from '/static/js/main.js'

class TagItem
{
    _evtTagClick = 'tag_click'
    _evtPinClick = 'tag_pin_click'

    _selCheckbox = 'input[type="checkbox"]'
    _selLabel = 'label'
    _selPin = 'button.tag-pin'

    _container
    _checkbox
    _highlight
    _pin

    _tagId

    _pinned = false

    constructor(containerNode)
    {
        this._container = containerNode
        this._checkbox = this._container.querySelector(this._selCheckbox)
        this._pin = this._container.querySelector(this._selPin)

        this._tagId = this._container.getAttribute('data-id')

        this._itemClickEvent = new CustomEvent(this._evtTagClick, { detail: { tagId: this._tagId }})
        this._pinClickEvent = new CustomEvent(this._evtPinClick,  { detail: { tagId: this._tagId }})

        this._container.querySelector(this._selCheckbox).addEventListener('click', e => { this.tagToggle(e) })
        this._container.querySelector(this._selLabel).addEventListener('click', e => { this.tagToggle(e) })
        this._container.querySelector(this._selPin).addEventListener('click', e => { this.pinToggle(e) })

        this._highlight = this._container.querySelector('#highlight')
    }

    tagToggle(e)
    {
        if (e.currentTarget !== this._checkbox)
        {
            e.preventDefault()
        }

        // console.log('TagItem method toggle tag ' + this._container.getAttribute('data-id'))

        // handle input checkbox so it can trigger callbacks too
        if (e.currentTarget === this._checkbox)
        {
            this._checkbox.checked = !this._checkbox.checked
        }

        this.checked = !this.checked
    }

    pinToggle(e)
    {
        e.preventDefault()

        console.log('TagItem method toggle pin ' + this._container.getAttribute('data-id'))
        this.pinned = !this.pinned
    }

    get checked()
    {
        return this._checkbox.checked
    }

    set checked(value)
    {
        if (value === this._checkbox.checked) { return }

        if (value) { this._container.classList.add('tag-selected') }
        else { this._container.classList.remove('tag-selected') }

        this._checkbox.checked = value

        document.dispatchEvent(this._itemClickEvent)
    }

    get pinned()
    {
        return this._pinned
    }

    set pinned(value)
    {
        if (value === this._pinned) { return }

        if (value) { this._pin.classList.add('tag-pin-on') }
        else { this._pin.classList.remove('tag-pin-on') }

        this._pinned = value

        // console.log('pinned ' + this._pinned)
        document.dispatchEvent(this._pinClickEvent)
    }

    get color()
    {
        return this._container.getAttribute('data-color')
    }

    setHighlight(isOn, hClass = 'highlight')
    {
        if (isOn)
            this._highlight.classList.add(hClass)
        else
            this._highlight.classList.remove(hClass)
    }
}


class WidgetImageTagsEditor
{
    evtTagsUpdated = 'tags_updated'

    _getSelector

    _containerSel
    _container
    _showBtn

    _pPins
    _pMain

    _bgOverlay

    _tagsToHighlight = []

    // init pins list
    PINS = 'pins_list'
    pinsList = [];
    storedList = ''

    // list of all TAG buttons
    tagBtns = {}
    // list of all TAG PROXY buttons
    tagProxyBtns = {}
    tmpTagProxyBtns = {}



    constructor(selContainer, selShowBtn, getterSelector)
    {
        this._tagsUpdatedEvent = new CustomEvent(this.evtTagsUpdated)

        this._getSelector = getterSelector

        if (selContainer === '')
        {
            this._container = document.createElement('div')
            this._container.id = 'tag-editor-totally-not-occupied-name-' + Math.round(Math.random() * 1000)
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
        this._showBtn.addEventListener('click', (e) =>
        {
            this.showWidget()
        })

        this._bgOverlay = new BgOverlay()

        this._container.classList.remove('vis-hide')

        document.addEventListener('keydown', (e) =>
        {
            if (isActiveTextInput()) return

            if (e.code === 'KeyT' && !e.shiftKey)
            {
                this.toggleTagsPopupDisplay(e)
            }
        })
    }

    get isLoaded()
    {
        return document.querySelector(`${this._containerSel} #tags-editor-popup`) != null
    }

    loadWidget()
    {
        return ApiTags.GetImageTagEditorWidgetHtml()
            .then(textHtml =>
            {
                this._container.innerHTML = textHtml
                return Promise.all([ApiTags.GetAllTags(), waitForCondition(() => this.isLoaded)()])
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

                this.initializeWidget(tags)

                return new Promise(resolve => resolve())
            })
    }

    initializeWidget(tags)
    {
        this.storedList = localStorage.getItem(this.PINS)
        if (this.storedList) { this.pinsList = JSON.parse(this.storedList) }

        const tagsContainer = this._container.querySelector('#tagList')
        const tplTag = this._container.querySelector('#tpl-tag-item').cloneNode(true)
        tplTag.id = ''
        tplTag.classList.remove('vis-hide')

        tags.forEach(tag =>
        {
            const node = tplTag.cloneNode(true)
            node.classList.remove('vis-hide')
            node.setAttribute('data-id', tag.name)
            node.setAttribute('data-color', tag.hex)
            node.querySelector('.tag-pin').setAttribute('value', tag.name)
            node.querySelector('input').id = tag.name
            node.querySelector('input').value = tag.name
            node.querySelector('label').textContent = tag.name
            node.querySelector('label').style.color = tag.hex
            node.querySelector('label').for = tag.name
            tagsContainer.appendChild(node)
        })

        // preload tags!!
        document.querySelectorAll('.tag-item').forEach(item =>
        {
            const tagId = item.getAttribute('data-id')
            this.tagBtns[tagId] = new TagItem(item)
        })

        this._pMain = document.querySelector(`${this._containerSel} #tags-editor-popup`)
        this._pPins = document.querySelector(`${this._containerSel} #tags-pins`)

        this._pMain.querySelector('#tags-submit-add').addEventListener('click', (e) => this.submitAddTags(e))
        this._pMain.querySelector('#tags-submit-del').addEventListener('click', (e) => this.submitRemoveTags(e))
        this._pMain.querySelector('#tags-clear').addEventListener('click', (e) => this.clearTagsPopup(e))
        this._pMain.querySelector('#pins-clear').addEventListener('click', (e) => this.clearPinsList(e))
        this._pMain.querySelector('#tags-close').addEventListener('click', (e) => this.hideWidget(e))
        this._bgOverlay.node.addEventListener('click', (e) => this.hideWidget(e))

        this._pPins.querySelector('#tags-pins-submit-add').addEventListener('click', (e) => this.submitAddTags(e))
        this._pPins.querySelector('#tags-pins-submit-del').addEventListener('click', (e) => this.submitRemoveTags(e))
        this._pPins.querySelector('#tags-pins-clear').addEventListener('click', (e) => this.clearTagsPopup(e))

        this.populatePinnedTags()

        document.addEventListener('keydown', (e) =>
        {
            if (isActiveTextInput()) return

            if (e.code === 'KeyN' && !e.shiftKey)
            {
                this.toggleTagsPinsDisplay(e)
            }
            else if (e.code === 'Escape' && !e.shiftKey)
            {
                this.hideWidget(e)
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
            this.loadWidget().then(() =>
            {
                this.showWidgetReal()
            })
        }
    }

    showWidgetReal()
    {
        this._pMain.classList.remove('vis-hide')
        this._bgOverlay.show()
        this._pMain.querySelector('#images-count').textContent = '' + this._getSelector().selectedIds.length

        Array.from(Object.values(this.tagBtns)).forEach(btn => btn.setHighlight(this._tagsToHighlight.includes(btn._tagId)))
    }

    hideWidget()
    {
        // hide
        this._pMain.classList.add('vis-hide')
        this._bgOverlay.hide()

        this._pMain.querySelector('#tags-submit-add').classList.remove('op-success', 'op-fail', 'loading')
        this._pMain.querySelector('#tags-submit-del').classList.remove('op-success', 'op-fail', 'loading')
        this._pPins.querySelector('#tags-pins-submit-add').classList.remove('op-success', 'op-fail', 'loading')
        this._pPins.querySelector('#tags-pins-submit-del').classList.remove('op-success', 'op-fail', 'loading')
    }

    toggleTagsPopupDisplay()
    {
        if (!this.isLoaded)
        {
            this.showWidget()
            return
        }
        if (this._pMain.classList.contains('vis-hide'))
        {
            this.showWidget()
        }
        else
        {
            this.hideWidget()
        }
    }

    showPins()
    {
        if (this.isLoaded)
        {
            this._pPins.classList.remove('tags-pins-hide')
        }
        else
        {
            this.loadWidget().then(() =>
            {
                this._pPins.classList.remove('tags-pins-hide')
            })
        }

    }

    hidePins()
    {
        this._pPins.classList.add('tags-pins-hide')
    }

    toggleTagsPinsDisplay()
    {
        if (this._pPins.classList.contains('tags-pins-hide'))
        {
            this.showPins()
        }
        else
        {
            this.hidePins()
        }
    }

    clearTagsPopup()
    {
        Array.from(this._pPins.querySelectorAll('input[type="checkbox"]:checked'))
            .map((checkbox) => { checkbox.checked = false; checkbox.parentNode.classList.remove('tag-selected') })

        Array.from(Object.values(this.tagBtns)).forEach(t => t.checked = false)
    }

    submitAddTags(evt)
    {
        if (!this._getSelector().selectionMode) { return }

        const elem = evt.currentTarget
        const selectedTags = Array.from(this._pMain.querySelectorAll('#tagList input[type="checkbox"]:checked'))
            .map((checkbox) => checkbox.value)

        wrapButtonFeedbackPromise(
            ApiTags.AddTags(this._getSelector().selectedIds, selectedTags)
                .then(() =>
                {
                    this.showNewTags(this._getSelector().selectedIds, selectedTags, [])
                    document.dispatchEvent(this._tagsUpdatedEvent)
                })
            , elem)
            .then(() =>
            {
                this.handleClearTagsOnSubmit(selectedTags, [])
            })
    }

    submitRemoveTags(evt)
    {
        if (!this._getSelector().selectionMode) { return }

        const elem = evt.currentTarget
        const selectedTags = Array.from(this._pMain.querySelectorAll('#tagList input[type="checkbox"]:checked'))
            .map((checkbox) => checkbox.value)

        wrapButtonFeedbackPromise(
            ApiTags.RemoveTags(this._getSelector().selectedIds, selectedTags)
                .then(() =>
                {
                    this.showNewTags(this._getSelector().selectedIds, [], selectedTags)
                    document.dispatchEvent(this._tagsUpdatedEvent)
                })
            , elem)
            .then(() =>
            {
                this.handleClearTagsOnSubmit([], selectedTags)
            })
    }

    // show tags in overlay
    showNewTags(ids, ptags = [], ntags = [])
    {
        document.querySelectorAll('.thumbnail').forEach(elem =>
        {
            const id = elem.getAttribute('data-id')
            if (!ids.includes(id)) { return }

            elem.querySelector('.overlay').classList.remove('vis-hide')

            const tl = elem.querySelector('.recent-tags')
            let recentTags = tl.textContent
            if (ptags.length > 0)
            {
                let tmp = recentTags === '' ? [] : recentTags.split(', ')
                tmp = Array.from(new Set([].concat(tmp, ptags)))
                tmp.sort()
                tl.textContent = tmp.join(', ')
            }
            if (ntags.length > 0)
            {
                let tmp = recentTags === '' ? [] : recentTags.split(', ')
                tmp = Array.from(tmp).filter(t => !ntags.includes(t))
                tmp.sort()
                tl.textContent = tmp.join(', ')
            }
            elem.querySelector('.tags-list').setAttribute('data-recent', tl.textContent)
        })
    }

    addTagToPinList(tagId, container, isTmp = false)
    {
        if (tagId === '' || tagId === null || !this.tagBtns.hasOwnProperty(tagId)) { return }

        const tpl = this._container.querySelector('#tag-pin-template')

        let btn = tpl.cloneNode(true)
        container.appendChild(btn)

        const inpt = btn.querySelector('input')
        const label = btn.querySelector('label')

        btn.id = ''
        btn.setAttribute('data-id', tagId)
        inpt.id = 'pin-' + tagId
        inpt.value = tagId
        label.setAttribute('for', 'pin-' + tagId)
        label.textContent = tagId
        label.style.color = this.tagBtns[tagId].color

        btn.addEventListener('click', evt =>
        {
            evt.preventDefault()

            const proxyItem = evt.currentTarget.querySelector('input')
            // console.log(`proxy ${proxyItem}`)
            // console.log(proxyItem)
            proxyItem.checked = !proxyItem.checked

            const id = evt.currentTarget.getAttribute('data-id')
            const tag = this.tagBtns[id]
            tag.checked = proxyItem.checked
            // console.log(`end proxy ${proxyItem}`)
            if (proxyItem.checked)
            {
                proxyItem.parentNode.classList.add('tag-selected')
            }
            else
            {
                proxyItem.parentNode.classList.remove('tag-selected')
            }
        })

        if (!isTmp)
        {
            this.tagBtns[tagId].pinned = true
            this.tagProxyBtns[tagId] = btn
        }
        else
        {
            this.tmpTagProxyBtns[tagId] = btn
        }

        btn.classList.remove('vis-hide')
    }

    removeTagFromPinList(tagId)
    {
        if (tagId === '') { return }

        if (!this.tagProxyBtns.hasOwnProperty(tagId)) { return }

        this.tagProxyBtns[tagId].remove()
        delete this.tagProxyBtns[tagId]
    }

    populatePinnedTags()
    {
        const pins = this._pPins.querySelector('#buttons')
        for (const id of this.pinsList)
        {
            this.addTagToPinList(id, pins)
        }

        document.addEventListener('tag_click', e =>
        {
            const tagId = e.detail.tagId

            // PINNED tags
            if (this.tagProxyBtns.hasOwnProperty(tagId))
            {
                const proxy = this.tagProxyBtns[tagId]
                const proxyInput = this.tagProxyBtns[tagId].querySelector('input')
                proxyInput.checked = this.tagBtns[tagId].checked

                if (proxyInput.checked) {proxy.classList.add('tag-selected')}
                else { proxy.classList.remove('tag-selected') }

                return
            }

            if (this.tmpTagProxyBtns.hasOwnProperty(tagId))
            {

            }
        })

        document.addEventListener('tag_pin_click', e =>
        {
            const pinId = e.detail.tagId
            const pin = this.tagBtns[pinId]

            // console.log(pin)
            // console.log(this.pinsList)
            const index = this.pinsList.indexOf(pinId)
            if (index === -1)
            {
                this.pinsList.push(pinId)
                this.addTagToPinList(e.detail.tagId, pins)
            }
            else
            {
                this.pinsList.splice(index, 1)
                this.removeTagFromPinList(e.detail.tagId, pins)
            }

            this.pinsList.sort()
            localStorage.setItem(this.PINS, JSON.stringify(this.pinsList))

            // console.log(this.pinsList)

            // quit if none
            if (this.pinsList.length === 0)
            {
                this._pPins.classList.add('tags-pins-hide')
            }
            else
            {
                this._pPins.classList.remove('tags-pins-hide')
            }
        })

        // quit if none
        if (this.pinsList.length === 0)
        {
            this._pPins.classList.add('tags-pins-hide')
        }
    }

    handleClearTagsOnSubmit(tagPos, tagNeg)
    {
        const url = new UrlWrapper(window.location.href)
        const shouldClear = parseInt(url.getSearch('conts', '0')) > 0
        if (!shouldClear) return

        Object.values(this.tagBtns).forEach(btn =>
        {
            btn.setHighlight(false, 'highlight-add')
            btn.setHighlight(false, 'highlight-remove')
        })

        tagPos.forEach(t => this.tagBtns[t].setHighlight(true, 'highlight-add'))
        tagNeg.forEach(t => this.tagBtns[t].setHighlight(true, 'highlight-remove'))

        this.clearTagsPopup()
    }

    clearPinsList()
    {
        this.pinsList = []
        this._pPins.classList.add('tags-pins-hide')
        localStorage.setItem(this.PINS, JSON.stringify(this.pinsList))

        this._pPins.querySelectorAll('.tag-pin').forEach(elem => { elem.classList.remove('tag-pin-on') })
    }

    highlightTags(tags)
    {
        this._tagsToHighlight = tags
    }
}


export { WidgetImageTagsEditor }