import {BgOverlay} from "/static/js/bg_overlay.js";
import {waitForCondition} from "/static/js/discover/utils.js";
import {ApiMisc} from "api";

class YesNoPopup
{
    _container
    _containerSel

    _widget

    constructor(selContainer = '')
    {
        this._isShown = false

        if (selContainer === '')
        {
            this._container = document.createElement('div')
            this._container.id = 'popup_yesno-totally-not-occupied-name-' + Math.round(Math.random() * 1000)
            this._container.classList.add('vis-hide')
            document.querySelector('body').appendChild(this._container)

            this._containerSel = '#' + this._container.id
        }
        else
        {
            this._containerSel = selContainer
            this._container = document.querySelector(selContainer)
        }

        // this._showBtn = document.querySelector(selShowBtn)
        // this._showBtn.addEventListener('click', (e) =>
        // {
        //     this.showWidget()
        // })

        this._bgOverlay = new BgOverlay()

        this._container.classList.remove('vis-hide')
    }

    get isLoaded()
    {
        return document.querySelector(`${this._containerSel} #yesno`) != null
    }

    loadWidget()
    {
        return ApiMisc.getPopupYesNo()
            .then(textHtml =>
            {
                this._container.innerHTML = textHtml
                return Promise.all([waitForCondition(() => this.isLoaded)()])
            })
            .then(_ =>
            {
                this._widget = document.querySelector(`${this._containerSel} #yesno`)

                this._widget.querySelector('#yes').addEventListener('click', e => { this.onYesHandler() })
                this._widget.querySelector('#no').addEventListener('click', e => { this.onNoHandler() })

                return new Promise(resolve => resolve())
            })
    }

    onYesHandler()
    {
        console.log('yes')
        this._lastOnYes()

        this.hide()
    }

    onNoHandler()
    {
        console.log('no')
        this._lastOnNo()

        this.hide()
    }

    show(title, text, onYes, onNo = () => {})
    {
        this._lastTitle = title
        this._lastText  = text
        this._lastOnYes = onYes
        this._lastOnNo  = onNo

        if (!this.isLoaded)
        {
            this.loadWidget()
                .then(() =>
                {
                    this.show(this._lastTitle, this._lastText, this._lastOnYes, this._lastOnNo)
                })
            return
        }

        if (this._isShown) return
        this._isShown = true

        this._bgOverlay.show()

        this._widget.querySelector('.title').textContent = this._lastTitle
        this._widget.querySelector('.text').textContent  = this._lastText

        this._widget.classList.remove('vis-hide')
    }

    hide()
    {
        this._widget.classList.add('vis-hide')
        this._bgOverlay.hide()
        this._isShown = false
    }
}

export {YesNoPopup}