import {ApiBoards} from 'api';
import {BgOverlay} from "/static/js/bg_overlay.js"
import {waitForCondition} from '/static/js/discover/utils.js'
import {wrapButtonFeedbackPromise} from "/static/js/main.js"

class WidgetBoard
{
    _containerSel
    _container
    _showBtn

    _getterIds

    _bgOverlay

    constructor(selContainer, selShowBtn, getterSelectedIds)
    {
        this._getterIds = getterSelectedIds

        if (selContainer === '')
        {
            this._container = document.createElement('div')
            this._container.id = 'board-add-totally-not-occupied-name-' + Math.round(Math.random() * 1000)
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

        this._bgOverlay = new BgOverlay()

        this._showBtn.addEventListener('click', () =>
        {
            this.showWidget()
        })
    }

    get isLoaded()
    {
        return document.getElementById('boards-popup') != null
    }

    loadWidget()
    {
        return ApiBoards.GetWidgetHtml()
            .then(textHtml =>
            {
                this._container.innerHTML = textHtml
                return waitForCondition(() => this.isLoaded)()
            })
            .then((_) =>
            {
                this.initializeWidget()

                return new Promise(resolve => resolve())
            })
    }

    initializeWidget()
    {
        document.getElementById('board-send-btn').addEventListener('click', (e) =>
        {
            const ids = this._getterIds()
            if (ids.length === 0) { return }

            // const idsStr = ids.join(',')

            const btn = e.currentTarget
            const board_id = document.getElementById('boards').value
            // const url = btn.getAttribute('data-url')
            wrapButtonFeedbackPromise(ApiBoards.AddImageToBoard(board_id, ids), btn)
            // fetchAndSimpleFeedback(`${url}?b-id=${board_id}&image-id=${idsStr}`, btn)
        })
        document.getElementById('board-send-close-btn').addEventListener('click', () =>
        {
            this.hideWidget()
        })
        this._bgOverlay.node.addEventListener('click', () => this.hideWidget())

        this._container.classList.remove('vis-hide')
    }

    showWidget()
    {
        if (this.isLoaded)
        {
            document.querySelector(`${this._containerSel} .popup`).classList.remove('vis-hide')
            this._bgOverlay.show()
        }
        else
        {
            this.loadWidget().then(() =>
            {
                document.querySelector(`${this._containerSel} .popup`).classList.remove('vis-hide')
                this._bgOverlay.show()
            })
        }
    }

    hideWidget()
    {
        if (!this.isLoaded) return
        document.querySelector(`${this._containerSel} .popup`).classList.add('vis-hide')
        document.querySelector(`${this._containerSel} #board-send-btn`).classList.remove('op-success', 'op-fail')

        this._bgOverlay.hide()
    }
}

export { WidgetBoard }