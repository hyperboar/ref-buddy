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
import {WidgetImageTagsEditor} from "image_tools/widget_tags_editor.js"
import {WidgetImageTagsFilter} from "image_tools/widget_tags_filter.js"
import {UrlWrapper}     from '/static/js/main.js'

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
    imageFlip = new ImageFlip(['.modal-img', '.magnification'])

    // magnification
    magnifier = new Magnification('.modal-img', '.magnification', () => imageFlip.isFlipped)

    // grayscale
    imageGrayScale = new ImageGrayscale('.modal-img', '.magnification', '.modal-bg')
    const gsButton = document.getElementById('toggle-grayscale')
    gsButton.addEventListener('click', () => imageGrayScale.toggleGrayscale())

    // cursor
    cursor = new ImageCursor('.modal-img', '.magnification')

    colorPicker = new ColorPicker(-1, '.modal-img', '.pallet-container', '.modal-img-color-picker', '#pallet-frame')
    // palette
    document.getElementById('pallet-button').addEventListener('click', (e) =>
        document.querySelector('.pallet-container').classList.toggle('vis-hide'))

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
            window.open(`/study-video/${currentImageData.id}`)
        }
    })


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

    // hotkeys
    document.addEventListener('keydown', function(e)
    {
        if (e.code === 'ArrowLeft')  { imageMove.clickPrev(e); e.preventDefault(); } // <-
        if (e.code === 'ArrowRight') { imageMove.clickNext(e); e.preventDefault(); } // ->

        if (e.altKey || e.ctrlKey || e.metaKey) { return }
        if ((e.code.includes('Numpad') || e.code.includes('Digit')) && e.shiftKey)
        { cursor.toggle(e.code); e.preventDefault(); return } // cursors
        if (e.code === 'KeyF' && e.shiftKey) { imageFlip.toggleFlip(); e.preventDefault(); } // g

        if (e.shiftKey) { return }
        if (e.code.includes('Numpad') || e.code.includes('Digit'))
        { imageGrayScale.toggleContrastKeycode(e.code); e.preventDefault(); } // g
        if (e.code.includes('Enter')){ timer.start(); e.preventDefault(); } // enter
        if (e.code === 'Space')      { toggleSameFolder(); e.preventDefault(); } // space
        if (e.code === 'KeyG')       { imageGrayScale.toggleGrayscale(); e.preventDefault(); } // g
        if (e.code === 'KeyI')       { toggleInfoPopup(); e.preventDefault(); } // g
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

    const modalBg = document.querySelector('.modal-bg')
    const modalImg = document.querySelector('.modal-img')

    Array.from([modalBg, modalImg]).forEach(im =>
    {
        im.src = data.url_image
        im.alt = `${data.id}:${data.path}`
    })

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
        url.probeSearch('tags') ||
        url.probeSearch('tag-set', 'all') ||
        url.probeSearch('sf', '1') ||
        url.probeSearch('time-planned', '120')

    if (changed)
        url.updateLocationHref()
}

function toggleSameFolder()
{
    const sf = document.getElementById('same-folder')
    sf.checked = !sf.checked
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