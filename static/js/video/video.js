import { VideoPlayer } from "/static/js/video/video_player.js"
import {VideoKeyProvider, VideoKey, VideoKeyPlayer} from "/static/js/video/video_keys.js"
import {} from "/static/js/main.js"

const videoOnionFwd = document.getElementById('video-fwd')
const onionSwitch = document.getElementById('onion')

const vFrame = document.getElementById('stat-frame')
const vTime  = document.getElementById('stat-time')
const vFps   = document.getElementById('stat-fps')
const vDur   = document.getElementById('stat-dur')
const vProg   = document.getElementById('stat-prog')

let forwardStep = 1.
let lastSelected = null
let isFbfMode = false

const video = new VideoPlayer('#video')

const imageId = parseInt(document.getElementById('image-id').textContent)

const extra = JSON.parse(document.getElementById('image-id').getAttribute('data-extra'))
video.frameRate = extra.fps[0] / extra.fps[1]

vFps.textContent = video.frameRate
vDur.textContent = extra.dur


//#region KEYS ------------------------

const keysAddBtn = document.getElementById('key-add')
const keysList = document.getElementById('keys-list')
const keyTpl = document.getElementById('key-tpl')

const forwardKeys = []
const videoKeyed = new VideoKeyPlayer(video, forwardKeys)

function newKeyTemplate(time, save = true)
{
    const frame = video.getFrameByTime(time)

    const key = new VideoKey(keyTpl, time, frame)

    const dupes = forwardKeys.filter(k => k.frame === frame)
    if (dupes.length > 0)
    {
        dupes[0].node.classList.remove('op-success')
        setTimeout(() => dupes[0].node.classList.add('op-success'), 100)
        return
    }

    const laterKeys = forwardKeys.filter(k => k.time - time > 0.).sort((k1, k2) => k1.time - k2.time)

    key.node.classList.add('op-success')
    if (laterKeys.length === 0)
    {
        keysList.append(key.node)
    }
    else
    {
        keysList.insertBefore(key.node, laterKeys[0].node)
    }

    forwardKeys.push(key)
    forwardKeys.sort((k1, k2) => k1.time - k2.time)

    key.addEventListener('delete_click', removeFwdKey)
    key.addEventListener('time_click', seekKey)

    if (save)
    {
        saveKeys()
    }
}

function removeFwdKey(e)
{
    const key = e.detail.key
    forwardKeys.remove(key)
    saveKeys()
}

function seekKey(e)
{
    video.currentTime = e.detail.key.time
}

function saveKeys()
{
    let keys = []

    forwardKeys.forEach(key =>
    {
        keys.push({time: key.time})
    })

    let videoData = JSON.parse(localStorage.getItem('video-data'))
    if (videoData === null) { videoData = {} }
    const id = 'id_' + imageId
    if (!videoData.hasOwnProperty(id)) { videoData[id] = {} }
    videoData[id]['video_keys'] = keys

    console.log(videoData)

    localStorage.setItem('video-data', JSON.stringify(videoData))
}

function getKeys()
{
    const videoData = JSON.parse(localStorage.getItem('video-data'))
    const id = 'id_' + imageId
    if (videoData === null || !videoData.hasOwnProperty(id) || !videoData[id].hasOwnProperty('video_keys')) { return [] }

    return videoData[id]['video_keys']
}

function fwdSeekNextKey()
{
    const curTime = video.currentTime

    const keys = forwardKeys.filter(k => k.time - curTime > 0.)
    if (keys.length === 0 && forwardKeys.length === 0)
    {
        video.seekTime(0)
    }
    else if (keys.length === 0)
    {
        video.seekTime(forwardKeys[0].time)
    }
    else
    {
        video.seekTime(keys[0].time)
    }
}

function fwdSeekPrevKey()
{
    const curTime = video.currentTime

    const keys = forwardKeys.filter(k => curTime - k.time > 0.)
    if (keys.length === 0 && forwardKeys.length === 0)
    {
        video.seekTime(0)
    }
    else if (keys.length === 0)
    {
        video.seekTime(forwardKeys[forwardKeys.length - 1].time)
    }
    else
    {
        video.seekTime(keys[keys.length - 1].time)
    }
}



function initializeKeys()
{
    // {#const data = [{time:4}, {time:10}]#}
    const data = getKeys()

    data.forEach(item =>
    {
        // console.log(item)
        newKeyTemplate(item.time, false)
    })

    selectClosestForwardKey(video)
}


document.addEventListener('keydown', e =>
{
    if (e.code === 'KeyK')
    {
        e.preventDefault()
        e.stopPropagation()
        newKeyTemplate(video.currentTime)
    }
})

document.getElementById('key-fwd-play').addEventListener('click', e =>
{
    if (videoKeyed.paused) videoKeyed.play()
    else videoKeyed.pause()
})

keysAddBtn.addEventListener('click', e =>
{
    newKeyTemplate(video.currentTime)
})

document.getElementById('clear-save').addEventListener('click', e =>
{
    forwardKeys.forEach(k => k.remove())
    forwardKeys.splice(0, forwardKeys.length)
    localStorage.removeItem('video-data')
})


initializeKeys()

//#endregion KEYS -- end ------------------------


// CONTROLS

onionSwitch.addEventListener('click', e =>
{
    videoOnionFwd.classList.toggle('vis-hide')
})

forwardStep = parseInt(document.getElementById('frame-step').value)
document.getElementById('frame-step').addEventListener('change', e =>
{
    forwardStep = parseInt(e.currentTarget.value)
})

// CONTROLS -- end


// update stats
video.addEventListener('onupdate', e =>
{
    const vid = e.detail.video
    vFrame.textContent = vid.frame.toString()
    vTime.textContent  = vid.currentTime.toFixed(2)
    vProg.textContent = (vid.currentTime / extra.dur * 100.).toFixed(2)
})


function selectClosestForwardKey(vid)
{
    if (forwardKeys.length === 0) return

    let min = 999999999.
    let idx = 0
    for (let key in forwardKeys)
    {
        let diff = Math.abs(forwardKeys[key].time - vid.currentTime)
        if (diff < min)
        {
            idx = key
            min = diff
        }
    }

    if (lastSelected !== null) lastSelected.selected(false)
    lastSelected = forwardKeys[idx]
    lastSelected.selected(true)
}
// update forward keys
video.addEventListener('onupdate', e =>
{
    const vid = e.detail.video
    selectClosestForwardKey(vid)
})

video.addEventListener('onseekbefore', e =>
{
    const vid = e.detail.video
    vid._beforeSeekTime = vid.currentTime
})

video.addEventListener('onseekafter', e =>
{
    if (!onionSwitch.checked) { return }

    const vid = e.detail.video
    const offset = vid.currentTime - vid._beforeSeekTime
    // console.log(offset)
    // console.log(vid.currentTime + (offset > 0. ? -offset : offset))
    videoOnionFwd.currentTime = vid.currentTime + (offset > 0. ? -offset : offset)
})


document.querySelector('#fbf-mode').addEventListener('click', e =>
{
    isFbfMode = e.currentTarget.checked
})


const keyMap =
{
    normal: function (e)
    {
        if (e.code === 'Space')
        {
            e.preventDefault()
            e.stopPropagation()
            if (video.paused) { video.play() }
            else { video.pause() }
        }
        else if (e.code === video.KeyPrev)
        {
            e.preventDefault()
            e.stopPropagation()
            if (!video.paused) { video.pause() }

            if (e.shiftKey)
            {
                fwdSeekPrevKey()
            }
            else
            {
                video.seekFrame(video.frame - 1)
            }
        }
        else if (e.code === video.KeyNext)
        {
            e.preventDefault()
            e.stopPropagation()
            if (!video.paused) { video.pause() }

            if (e.shiftKey)
            {
                fwdSeekNextKey()
            }
            else
            {
                video.seekFrame(video.frame + 1)
            }
        }
        else if (e.code === video.KeyNextJump)
        {
            e.preventDefault()
            e.stopPropagation()
            if (!video.paused) { video.pause() }
            video.seekFrame(video.frame + forwardStep)
        }
        else if (e.code === video.KeyPrevJump)
        {
            e.preventDefault()
            e.stopPropagation()
            if (!video.paused) { video.pause() }
            video.seekFrame(video.frame - forwardStep)
        }
    },
    fbf: function(e)
    {
        if (e.code === video.KeyPrev)
        {
            e.preventDefault()
            e.stopPropagation()
            if (!video.paused) { video.pause() }
            fwdSeekPrevKey()

        }
        else if (e.code === video.KeyNext)
        {
            e.preventDefault()
            e.stopPropagation()
            if (!video.paused) { video.pause() }
            fwdSeekNextKey()
        }
    }
}

// Frame-by-frame scrubbing with left and right arrow keys
document.addEventListener('keydown', e =>
{
    isFbfMode ? keyMap.fbf(e) : keyMap.normal(e)
})