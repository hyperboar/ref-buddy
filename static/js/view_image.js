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
import {DrawCanvas}    from "image_tools/draw_canvas.js"
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
let drawCanvas = null
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

    function updateViewportHeight() {
        const vh = window.visualViewport.height;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    window.addEventListener('resize', updateViewportHeight);
    window.addEventListener('scroll', updateViewportHeight); // Handle dynamic UI changes
    window.addEventListener('load', updateViewportHeight); // Ensure it runs on page load

     // Call it once at the beginning
    updateViewportHeight();

    const imageId = document.getElementById('image-id').textContent

    // controls
    const ctrlBtn = document.querySelector('.controls-toggle-btn')
    function updateCtrlBtn(evt) {
        const btn = evt.target
        let state = parseInt(btn.getAttribute('data-state')) === 1
        btn.textContent = state ?
            btn.getAttribute('data-on') :
            btn.getAttribute('data-off')

        const panel = btn.closest('.media-controls')
        if (state)
            panel.classList.remove('media-controls-collapsed')
        else
            panel.classList.add('media-controls-collapsed')
    }
    updateCtrlBtn({'target': ctrlBtn})
    ctrlBtn.addEventListener('click', (evt) => {
        const btn = evt.target
        // toggle
        let state = parseInt(btn.getAttribute('data-state'))
        state = (state + 1) % 2
        btn.setAttribute('data-state', state)
        updateCtrlBtn(evt)
    })

    // history
    history = new ImageHistory()
    history.pushToTail(imageId)
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
    imageFlip = new ImageFlip(['.media', '.magnification'])

    // // TODO distinguish between img, gif, video
    // // magnification
    // magnifier = new Magnification(['stub!', '.anim-container #animation'], '.magnification-container', '.magnification', () => imageFlip.isFlipped)

    // grayscale
    imageGrayScale = new ImageGrayscale(['.media',  '.media-bg', '.magnification'])
    const gsButton = document.getElementById('toggle-grayscale')
    gsButton.addEventListener('click', () => imageGrayScale.toggleGrayscale())

    // cursor
    cursor = new ImageCursor('.media', '.magnification')

    // draw canvas
    drawCanvas = new DrawCanvas('#draw-overlay', '.media','#the-media', '#draw-canvas-controls', imageId, ApiImage.SaveDrawing)
    const dcButton = document.getElementById('draw-button')
    dcButton.addEventListener('click', () => drawCanvas.toggle())

    colorPicker = new ColorPicker(-1, '.media', '.pallet-container', '.modal-img-color-picker', '#pallet-frame')
    // palette
    document.getElementById('pallet-button').addEventListener('click', (e) =>
        document.querySelector('.pallet-container').classList.toggle('hidden'))

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

        if (imageMove.history.isAtTail) {hMarker.classList.add('hidden')}
        else hMarker.classList.remove('hidden')

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
            infoPopup.classList.add('hidden')
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


    // const dropTarget = document.querySelector('#drop-target')
    // const body = document.querySelector('body')
    // body.addEventListener('dragover', e =>
    // {
    //     if (dropTarget.classList.contains('hidden')) { dropTarget.classList.remove('hidden') }
    //
    //     e.preventDefault()
    // })
    //     body.addEventListener('mouseup', e =>
    // {
    //     if (!dropTarget.classList.contains('hidden')) { dropTarget.classList.add('hidden') }
    // })
    // // body.addEventListener('dragleave', e =>
    // // {
    // //     e.preventDefault()
    // //
    // //     if (!dropTarget.classList.contains('hidden')) { dropTarget.classList.add('hidden') }
    // // })
    //
    // dropTarget.addEventListener('dragover', e=>
    // {
    //     console.log('target')
    //     // console.log(e)
    //     e.preventDefault()
    // })
    //
    // dropTarget.addEventListener('drop', e=>
    // {
    //     e.preventDefault()
    //
    //     console.log('target')
    //     // console.log(e)
    //
    //     if (!dropTarget.classList.contains('hidden')) { dropTarget.classList.add('hidden') }
    //
    //     const files = e.dataTransfer.items ?
    //         [...e.dataTransfer.items].filter(item => item.kind === "file").map(item => item.getAsFile()) :
    //         [...e.dataTransfer.files]
    //
    //     files.forEach((file, i) =>
    //     {
    //         // console.log(`… file[${i}].name = ${file.name}`)
    //         let reader = new FileReader()
    //         reader.readAsDataURL(file)
    //         reader.onloadend = function()
    //         {
    //             const data = {
    //                 "id": -666,
    //                 "thumb": reader.result,
    //                 "url_image": reader.result,
    //                 "url_folder": "/folder/-1",
    //                 "path": file,
    //                 "path_id": -1,
    //                 "content_type": 1,
    //                 "video": 0,
    //                 "fav": 0,
    //                 "rating": 0,
    //                 "extra": {}
    //             }
    //             console.log(data)
    //             injectImageData(data)
    //             updateComponents(data)
    //         }
    //     })
    // })

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

        if (e.code === 'KeyF' && e.shiftKey && e.ctrlKey) { togglePanelsOrder(); e.preventDefault(); }
        if (e.code === 'KeyZ' && e.ctrlKey && drawCanvas.isDrawingMode) { drawCanvas.undo(); e.preventDefault(); }

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

function togglePanelsOrder()
{
    const container = document.querySelector('.modal')
    const image = container.querySelector('.modal-img-container')
    const controls = container.querySelector('.modal-controls')

    if (container.firstElementChild === image)
    {
        container.insertBefore(controls, image)
    }
    else
    {
        container.insertBefore(image, controls)
    }
}

function updateComponents(data)
{
    selection.selectedIds = [data.id]

    rateImage.imageId = data.id
    rateFolder.imageId = data.id

    // color picker
    colorPicker.reset(data.id)

    fav.setData(data.id, data.fav === 1)
    fav.update(data.fav === 1)

    timer.reset()

    if (data.content_type === 1)
        drawCanvas.updateCanvas('.media .media-img')
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

    const imgId = document.querySelector('#image-id')
    imgId.textContent = data.id

    const mediaBg = document.querySelector('.media-bg')
    // insert appropriate bg
    insertMediaBg(mediaBg, data)

    const media = document.querySelector('.media')
    insertMediaContent(media, data)

    // magnifier
    // magnifier.reset()

    if (data.content_type === 1)
    {
        // magnifier.setImage(data.url_image)
        const mediaImg = document.querySelector('.media-img')
        Array.from([mediaBg, mediaImg]).forEach(im =>
        {
            im.src = data.url_image
            im.alt = `${data.id}:${data.path}`
        })
    }
    // animatiuon
    if (data.content_type === 2) {
        animPlayer.node.classList.remove('hidden')
        animPlayer.pause()
        animPlayer.loadFrames(data.id).then(() => { animPlayer.play() })
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
    if (data.video) {openVidBtn.classList.remove('hidden')}
    else openVidBtn.classList.add('hidden')
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
                if (t.ai !== 0)
                {
                    li.classList.add('ai-tag')
                }
                infoTags.appendChild(li)
            })

            imageTagEditor.highlightTags(Array.from(data[0].tags).map(t => t.name))
        })
}

function insertMediaBg(container, data)
{
    container.childNodes.forEach(el => el.remove())

    // image
    if (data.content_type === 1 || data.content_type === 2)
    {
        const tpl = document.querySelector('#tpl-media-bg-image')
        const node = tpl.cloneNode(true).content

        node.querySelector('img').src = data.url_image

        container.appendChild(node)
    }
    // video
    else
    {
        const tpl = document.querySelector('#tpl-media-bg-video')
        const node = tpl.cloneNode(true).content

        container.appendChild(node)
    }
}

function insertMediaContent(container, data)
{
    container.childNodes.forEach(el => el.remove())

    // image
    if (data.content_type === 1)
    {
        const tpl = document.querySelector('#tpl-media-image')
        const node = tpl.cloneNode(true).content

        node.querySelector('img').src = data.url_image

        container.appendChild(node)
    }
    // video
    else if (data.content_type === 2)
    {
        const tpl = document.querySelector('#tpl-media-frames')
        const node = tpl.cloneNode(true).content

        node.querySelector('img').src = data.url_image
        container.appendChild(node)

        // animation
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
            const modalBg = document.querySelector('.media-bg img')
            modalBg.src = anim.currentFrameUrl

            // magnifier.setImage(anim.currentFrameUrl)
        })
    }
    else
    {
        const tpl = document.querySelector('#tpl-media-video')
        const node = tpl.cloneNode(true).content

        node.querySelector('source').src = data.url_image

        container.appendChild(node)
    }
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
    infoPopup.classList.toggle('hidden')
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