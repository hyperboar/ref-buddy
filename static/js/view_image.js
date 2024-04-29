import {ApiImage, ApiTags} from 'api'
import {RateSingle, RateFolder} from 'image_tools/rating.js'
import {Fav}            from 'image_tools/favorite.js'
import {Magnification}  from 'image_tools/magnification.js'
import {ImageSelection} from 'image_tools/image_selection.js'
import {StudyTimer}     from 'image_tools/study_timer.js'
import {ImageFlip}      from 'image_tools/flip.js'
import {ImageGrayscale} from 'image_tools/grayscale.js'
import {ImageHistory}   from 'image_tools/history.js'
import {ImageNextPrev}  from 'image_tools/nextprev_image.js'
import {TagSetList}     from 'image_tools/tag-set-list.js'
import {ImageCursor}    from "image_tools/cursor.js"
import {ColorPicker}    from "image_tools/color_picker.js"
import {WidgetBoard}    from "image_tools/widget_board.js"
import {FracturedColors}    from "image_tools/fractured_colors.js"
import {WidgetImageTagsEditor} from "image_tools/widget_tags_editor.js"
import {WidgetImageTagsFilter} from "image_tools/widget_tags_filter.js"
import {isActiveTextInput, UrlWrapper} from '/static/js/main.js'
import { AnimPlayer } from "/static/js/video/anim_player.js"

let selection = null
let rateImage = null
let rateFolder = null
let fav = null

let timer = null
let magnifier = null
let imageFlip = null
let imageGrayScale = null
let cursor = null
let colorPicker = null

let tagSets = null

let boardWidget= null
let imageTagEditor = null
let imageTagFilter = null

let imageMove = null
let history = null
let hMarker    = null
let hMarkerPos = null
let hMarkerMax = null

let currentImageData = null

let dragged = null
let dragInAction = false

let animPlayer = null

// let fracColors = null


function initializeComponents()
{
    // yay!
    doubleCheckWeHaveAllWeNeedInUrl()

    // history
    history = new ImageHistory()
    history.pushToTail(document.getElementById('image-id').textContent)
    history.moveToTail()

    // selection
    selection = new ImageSelection('stub-select-btn', '.stub-gallery', '.stub-thumb')
    selection.selectionMode = true

    // rating
    rateImage  = new RateSingle(-1, '#image-rating', '#rate-up', '#rate-dn', 'loading', 'op-success', 'op-fail')
    rateFolder = new RateFolder(-1, '#image-rating', '#rate-up-f', '#rate-dn-f', 'loading', 'op-success', 'op-fail')


    //fav
    fav = new Fav(-1, '#is-fav')
    document.addEventListener('fav', (e) => { console.log(e.detail.fav.isFav); currentImageData.fav = e.detail.fav.isFav })

    // flip
    imageFlip = new ImageFlip(['.modal-img-container'])

    // magnification
    magnifier = new Magnification(['.modal-img', '.anim-container #animation'], '.magnification', () => imageFlip.isFlipped)

    // grayscale
    imageGrayScale = new ImageGrayscale(['.modal',  '.modal-bg img'])
    const gsButton = document.getElementById('toggle-grayscale')
    gsButton.addEventListener('click', () => imageGrayScale.toggleGrayscale())

    // cursor
    cursor = new ImageCursor('.modal-img', '.magnification')

    colorPicker = new ColorPicker(-1, '.modal-img', '.pallet-container', '.modal-img-color-picker', '#pallet-frame')
    // palette
    document.getElementById('pallet-button').addEventListener('click', (e) =>
        document.querySelector('.pallet-container').classList.toggle('vis-hide'))

    // same folder
    InitializeSameFolder()

    // moving to next and prev image
    imageMove = new ImageNextPrev(history, '#image-id', '#next', '#prev', '#pick-next-type', getUrlFilterParameters)
    hMarker    = document.getElementById('history-marker')
    hMarkerPos = document.getElementById('h-cur-pos')
    hMarkerMax = document.getElementById('h-max-pos')
    document.addEventListener('image_change_ready', (e) =>
    {
        document.getElementById('image-id').textContent = e.detail.nextId

        if (imageMove.history.isAtTail) {hMarker.classList.add('vis-hide')}
        else hMarker.classList.remove('vis-hide')

        console.log(`${imageMove.pos} ${imageMove.length}`)

        hMarkerPos.textContent = imageMove.history.pos
        hMarkerMax.textContent = imageMove.history.length

        return loadImage()
    })

    // tag sets
    tagSets = new TagSetList('#tag-set')

    // timer
    const timerTime = 120
    timer = new StudyTimer(timerTime, '#time-current', '#time-planned', '#timer-start')
    document.addEventListener('timer_start', () =>
    {
        ApiImage.UpdateLastViewed(currentImageData.id)
            .then((_) =>
            {
                console.log('Last Viewed time updated!')
            })
    })

    animPlayer = new AnimPlayer(
        '.anim-container',
        '.anim-container #animation',
        '.anim-container #stat-frame',
        '.anim-container #stat-time',
        '.anim-container #stat-dur',
        '.anim-container #stat-prog')
    animPlayer.node.addEventListener('onupdate', (e) =>
    {
        const anim = e.detail.video
        const modalBg = document.querySelector('.modal-bg img')
        modalBg.src = anim.currentFrameUrl

        magnifier.setImage(anim.currentFrameUrl)
    })

    // board
    boardWidget = new WidgetBoard('', '#board-button', () => selection.selectedIds)

    // tags editor
    imageTagEditor = new WidgetImageTagsEditor('', '#tags-edit-button', () => selection)
    document.addEventListener(imageTagEditor.evtTagsUpdated, (e) =>
    {
        updateImageTags()
    })

    // tags filter
    imageTagFilter = new WidgetImageTagsFilter('', '#tags-filter-button', false)

    // video
    const openVidBtn = document.getElementById('open-vid-btn')
    openVidBtn.addEventListener('click', (e) =>
    {
        e.preventDefault()

        if (e.shiftKey)
        {
            fetch(`/open-video?path=${encodeURI(pathElement.textContent)}`)
        }
        else
        {
            if (currentImageData.content_type === 2)
                window.open(`/study-anim/${currentImageData.id}`)
            else
                window.open(`/study-video/${currentImageData.id}`)
        }
    })


    // fracColors = new FracturedColors()


    // popups

    // Get references to the button and popup elements
    const infoBtn = document.getElementById('info-button')
    const infoPopup = document.getElementById('image-info-popup')

    // Show the popup when the button is clicked
    infoBtn.addEventListener('click', () => toggleInfoPopup())


    // Hide the popup when clicking outside of it
    document.addEventListener('click', (event) =>
    {
        if (!infoPopup.contains(event.target) && event.target !== infoBtn)
        {
            infoPopup.classList.add('vis-hide')
        }
    })

    // Copy the path to clipboard when the "Copy to Clipboard" button is clicked
    const pathElement = document.getElementById('image-path')
    const copyButton = document.getElementById('image-path-copy-btn')
    copyButton.addEventListener('click', () =>
    {
        const path = pathElement.textContent
        document.copyToClipboard(path, () =>
        {
            copyButton.textContent = 'Copied!'
        })
    })


    const dropTarget = document.querySelector('#drop-target')
    const body = document.querySelector('body')
    body.addEventListener('dragover', e =>
    {
        if (dropTarget.classList.contains('vis-hide')) { dropTarget.classList.remove('vis-hide') }

        e.preventDefault()
    })
        body.addEventListener('mouseup', e =>
    {
        if (!dropTarget.classList.contains('vis-hide')) { dropTarget.classList.add('vis-hide') }
    })
    // body.addEventListener('dragleave', e =>
    // {
    //     e.preventDefault()
    //
    //     if (!dropTarget.classList.contains('vis-hide')) { dropTarget.classList.add('vis-hide') }
    // })

    dropTarget.addEventListener('dragover', e=>
    {
        console.log('target')
        // console.log(e)
        e.preventDefault()
    })

    dropTarget.addEventListener('drop', e=>
    {
        e.preventDefault()

        console.log('target')
        // console.log(e)

        if (!dropTarget.classList.contains('vis-hide')) { dropTarget.classList.add('vis-hide') }

        const files = e.dataTransfer.items ?
            [...e.dataTransfer.items].filter(item => item.kind === "file").map(item => item.getAsFile()) :
            [...e.dataTransfer.files]

        files.forEach((file, i) =>
        {
            // console.log(`… file[${i}].name = ${file.name}`)
            let reader = new FileReader()
            reader.readAsDataURL(file)
            reader.onloadend = function()
            {
                const data = {
                    "id": -666,
                    "thumb": reader.result,
                    "url_image": reader.result,
                    "url_folder": "/folder/-1",
                    "path": file,
                    "path_id": -1,
                    "content_type": 1,
                    "video": 0,
                    "fav": 0,
                    "rating": 0,
                    "extra": {}
                }
                console.log(data)
                injectImageData(data)
                updateComponents(data)
            }
        })
    })

    // hotkeys
    document.addEventListener('keydown', (e) =>
    {
        if (isActiveTextInput()) return

        if (currentImageData.content_type === 2) //
        {
            if (e.code === 'ArrowRight') { animPlayer.move(1); e.preventDefault(); } // ->
            if (e.code === 'ArrowLeft')  { animPlayer.move(-1); e.preventDefault(); } // <-
            if (e.shiftKey && e.code === 'ArrowLeft')  { imageMove.clickPrev(e); e.preventDefault(); } // <-
            if (e.shiftKey && e.code === 'ArrowRight') { imageMove.clickNext(e); e.preventDefault(); } // ->
        }
        else
        {
            if (e.code === 'ArrowLeft')  { imageMove.clickPrev(e); e.preventDefault(); } // <-
            if (e.code === 'ArrowRight') { imageMove.clickNext(e); e.preventDefault(); } // ->
        }


        if (e.altKey || e.ctrlKey || e.metaKey) { return }
        if ((e.code.includes('Numpad') || e.code.includes('Digit')) && e.shiftKey)
        { cursor.toggle(e.code); e.preventDefault(); return } // cursors
        if (e.code === 'KeyF' && e.shiftKey) { imageFlip.toggleFlip(); e.preventDefault(); } // g

        if (e.shiftKey) { return }
        if (e.code.includes('Numpad') || e.code.includes('Digit'))
        { imageGrayScale.toggleContrastKeycode(e.code); e.preventDefault(); } // g
        if (e.code.includes('Enter')){ timer.start(); e.preventDefault(); } // enter

        if (currentImageData.content_type === 2) //
        {
            if (e.code === 'Space')      { animPlayer.togglePlay(); e.preventDefault(); } // space
        }
        else
        {
            if (e.code === 'Space')      { toggleSameFolder(e); e.preventDefault(); } // space
        }

        if (e.code === 'KeyG')       { imageGrayScale.toggleGrayscale(); e.preventDefault(); } // g
        if (e.code === 'KeyI')       { toggleInfoPopup(); e.preventDefault(); } // g
        // if (e.code === 'KeyV')       { fracColors.render('.modal-img'); e.preventDefault(); } // g
    })
}

function updateComponents(data)
{
    selection.selectedIds = [data.id]

    rateImage.imageId = data.id
    rateFolder.imageId = data.id

    colorPicker.reset(data.id)

    fav.setData(data.id, data.fav === 1)
    fav.update(data.fav === 1)

    timer.reset()
}

function loadImage() {
    const id = document.getElementById('image-id').textContent
    return ApiImage.GetSingle(id, true)
        .then(data => {
            console.log(data)
            injectImageData(data)
            updateComponents(data)
        })
}


function injectImageData(data)
{
    currentImageData = data

    const imgId = document.getElementById('image-id')
    imgId.textContent = data.id

    const modalBg = document.querySelector('.modal-bg img')
    const modalImg = document.querySelector('.modal-img')

    magnifier.reset()
    if (data.content_type === 2) // animated something
    {
        modalImg.classList.add('vis-hide')
        animPlayer.node.classList.remove('vis-hide')
        animPlayer.pause()
        animPlayer.loadFrames(data.id).then(() => { animPlayer.play() })
    }
    else
    {
        modalImg.classList.remove('vis-hide')
        animPlayer.node.classList.add('vis-hide')
        animPlayer.pause()

        magnifier.setImage(data.url_image)

        Array.from([modalBg, modalImg]).forEach(im =>
        {
            im.src = data.url_image
            im.alt = `${data.id}:${data.path}`
        })
    }

    const rating = document.querySelector('#image-rating')
    rating.textContent = data.rating

    const folderLink = document.getElementById('img-folder-link')
    folderLink.href = data.url_folder


    // info
    const imgPath = document.querySelector('#image-path')
    if (data.video) data.path = data.path.replace('.mp4.gif', '.mp4')
    imgPath.textContent = data.path
    const infoId = document.querySelector('#info-image-id')
    infoId.href = '/study-image/' + data.id
    infoId.textContent = data.id

    updateImageTags()

    // misc
    const stubThumb = document.querySelector('.stub-thumb')
    stubThumb.setAttribute('data-id', data.id)

    const openVidBtn = document.getElementById('open-vid-btn')
    if (data.video) {openVidBtn.classList.remove('vis-hide')}
    else openVidBtn.classList.add('vis-hide')
}

function updateImageTags()
{
    const infoTags = document.querySelector('#image-info-popup #tags')
    infoTags.childNodes.forEach(t => t.remove())

    ApiTags.GetSingle(currentImageData.id)
        .then(data =>
        {
            data[0].tags.sort((a, b) => a.name.localeCompare(b.name))
            data[0].tags.forEach(t =>
            {
                const li = document.createElement('li')
                li.style.color = t.color
                const a = document.createElement('a')
                a.href = '/all?tags=' + t.name
                a.textContent = t.name
                li.appendChild(a)
                infoTags.appendChild(li)
            })

            imageTagEditor.highlightTags(Array.from(data[0].tags).map(t => t.name))
        })
}

function doubleCheckWeHaveAllWeNeedInUrl()
{
    const url = new UrlWrapper(window.location.href)

    const changed =
        url.probeSearch('tags') +
        url.probeSearch('tag-set', 'all') +
        url.probeSearch('sf', '1') +
        url.probeSearch('time-planned', '120')

    if (changed > 0)
        url.updateLocationHref()
}

function InitializeSameFolder()
{
    const sf = document.getElementById('same-folder')
    const url = new UrlWrapper(window.location.href)
    sf.checked = url.getSearch('sf', '1') === '1'

    sf.addEventListener('click', e => toggleSameFolder(e))
}

function toggleSameFolder(e)
{
    let sf = null
    if (e.type === 'click')
    {
        sf = e.target
    }
    else
    {
        sf = document.getElementById('same-folder')
        sf.checked = !sf.checked
    }

    const url = new UrlWrapper(window.location.href)
    url.setSearch('sf', sf.checked ? '1' : '0')
    url.updateLocationHref()
}

function toggleInfoPopup()
{
    const infoPopup = document.getElementById('image-info-popup')
    infoPopup.classList.toggle('vis-hide')
}

function getUrlFilterParameters()
{
    const url = new UrlWrapper(window.location.href)

    return url.getSearchStr()
}

/*
document.addEventListener('DOMContentLoaded', () =>
{
    let imgParams = new ImgParams('image-id', 'same-folder', 'time-planned', 'is-fav', 'min-rating', 'tag-set')

    imgParams.setParamsFromGET()

    // popup
})
*/

document.addEventListener('DOMContentLoaded', () =>
{
    console.log('Page Loaded!')

    initializeComponents()

    loadImage()
})