import { VideoPlayer } from "/static/js/video/video_player.js"

// const video = document.getElementById('video')
const videoOnionFwd = document.getElementById('video-fwd')

const vFrame = document.getElementById('cur-frame')
const vTime  = document.getElementById('cur-time')

let forwardStep = 1.

const video = new VideoPlayer('#video')

const imageId = parseInt(document.getElementById('image-id').textContent)

// KEYS

const keysAddBtn = document.getElementById('key-add')
const keysList = document.getElementById('keys-list')
const keyTpl = document.getElementById('key-tpl')
console.log(keyTpl)

function newKeyTemplate(value)
{
    const key = keyTpl.cloneNode(true)
    keysList.append(key)

    key.id = 'key'
    key.setAttribute('data-time', value)

    key.querySelector('#text').textContent = value.toFixed(2)
    key.querySelector('#text').addEventListener('click', seekKey)
    key.querySelector('#delete').addEventListener('click', removeKey)

    key.classList.remove('vis-hide')

    saveKeys()
}

function removeKey(e)
{
    const btn = e.currentTarget
    btn.parentNode.parentNode.parentNode.removeChild(btn.parentNode.parentNode)

    saveKeys()
}

function seekKey(e)
{
    e.preventDefault()

    const text = e.currentTarget
    const value = parseFloat(text.parentNode.parentNode.getAttribute('data-time'))
    console.log(value)
    video.currentTime = value
}

function saveKeys()
{
    let keys = []

    Array.from(keysList.querySelectorAll('#keys-list #key')).forEach(item =>
    {
        console.log(item)
        const value = parseFloat(item.getAttribute('data-time'))
        keys.push({time: value})
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



function initializeKeys()
{
    // {#const data = [{time:4}, {time:10}]#}
    const data = getKeys()

    data.forEach(item =>
    {
        console.log(item)
        newKeyTemplate(item.time)
    })
}



keysAddBtn.addEventListener('click', e =>
{
    newKeyTemplate(video.currentTime)
})
document.getElementById('clear-save').addEventListener('click', e =>
{
    localStorage.removeItem('video-data')
})


initializeKeys()

// KEYS -- end


// CONTROLS

document.getElementById('onion').addEventListener('click', e =>
{
    videoOnionFwd.classList.toggle('vis-hide')
})

forwardStep = parseInt(document.getElementById('frame-step').value)
document.getElementById('frame-step').addEventListener('change', e =>
{
    forwardStep = parseInt(e.currentTarget.value)
})

// CONTROLS -- end


function seek(vid, frames, fps)
{
    console.log(`before cur time: ${vid.currentTime}`)

    const offset = frames * fps

    const time = vid.currentTime
    vid.currentTime += offset

    if (offset > 0.)
    {
        videoOnionFwd.currentTime = time
    } else
    {
        videoOnionFwd.currentTime = vid.currentTime + offset
    }


    console.log(`after cur time: ${vid.currentTime} :: 1 frame ${frames * fps} `)
}

video.onTimeUpdate = function(vid)
{
    vFrame.textContent = vid.frame.toString()
    vTime.textContent  = `${vid.currentTime.toFixed(2)}`
}

video.onSeekBefore = function(vid)
{
    vid._beforeSeekTime = vid.currentTime
}

video.onSeekAfter = function(vid)
{
    const offset = vid.currentTime - vid._beforeSeekTime
    videoOnionFwd.currentTime = vid.currentTime + (offset > 0. ? -offset : offset)
}


document.addEventListener('keydown', e =>
{
    // {#if (e.shiftKey) {return}#}
    if (e.code === 'Space')
    {
        e.preventDefault()
        e.stopPropagation()
        if (video.paused) { video.play() }
        else { video.pause() }
    }
})

// Frame-by-frame scrubbing with left and right arrow keys
document.addEventListener('keydown', e =>
{
    if (e.code === 'ArrowLeft')
    {
        e.preventDefault()
        e.stopPropagation()
        if (!video.paused) { video.pause() }
        video.seekFrame(video.frame - 1)
        // seek(video, -1, fps)
    }
    else if (e.code === 'ArrowRight')
    {
        e.preventDefault()
        e.stopPropagation()
        if (!video.paused) { video.pause() }
        video.seekFrame(video.frame + 1)
        // seek(video, 1, fps)
    }
    else if (e.code === 'ArrowUp')
    {
        e.preventDefault()
        e.stopPropagation()
        if (!video.paused) { video.pause() }
        video.seekFrame(video.frame + forwardStep)
    }
    else if (e.code === 'ArrowDown')
    {
        e.preventDefault()
        e.stopPropagation()
        if (!video.paused) { video.pause() }
        video.seekFrame(video.frame - forwardStep)
    }
})