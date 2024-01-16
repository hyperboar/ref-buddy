import { DiscoverPost } from "/static/js/discover/d_post.js"
import {imageLoader, TriggerOnVisible, waitFor} from "/static/js/discover/utils.js"
import {} from '/static/js/main.js'

const postTpl = document.querySelector('#post-tpl')
const feedContainer = document.querySelector('.feed')

let IS_LOADING_MORE = false

let centeredNode = null

function getNodeInMiddle()
{
    const windowHeight = window.innerHeight;
    const middleOfWindow = windowHeight / 2 + window.scrollY;

    // Get all the nodes on the page (you might want to narrow this down based on your specific needs)
    const allNodes = document.querySelectorAll('.feed .post');

    if (allNodes === null || allNodes.length === 0) {
        return null
    }

    // Find the node intersecting the middle of the window
    let nodeInMiddle = null;
    for (let idx in allNodes)
    {
        const node = allNodes[idx]
        const rect = node.getBoundingClientRect();
        const nodeTop = rect.top + window.scrollY;
        const nodeBottom = rect.bottom + window.scrollY;

        if (nodeTop <= middleOfWindow && nodeBottom >= middleOfWindow) {
            // Node is intersecting the middle of the window
            nodeInMiddle = node;
            break; // Exit loop once we find the node in the middle
        }
    }

    return nodeInMiddle;
}

function loadMore(url, freezeScroll = true, isHead = true)
{
    IS_LOADING_MORE = true

    fetch(url)
    .then(r =>
    {
        if (!r.ok)
        {
            console.log('something went wrong')
            throw new Error('Response is not ok')
        }

        return r.json()
    })
    .then(json =>
    {
        Promise.all(json.map(item => imageLoader(item.image_url)))
        return json
    })
    .then(json =>
    {
        json.forEach(item =>
        {
            const post = new DiscoverPost(postTpl, item)
            if (isHead)
                feedContainer.prepend(post.node)
            else
                feedContainer.append(post.node)

            if (centeredNode !== null && freezeScroll)
            {
                window.scrollTo({
                    top: centeredNode.offsetTop,
                    behavior: 'instant'
                })
            }
        })

        return waitFor(0.5)()
    })
    .finally(() =>
    {
        IS_LOADING_MORE = false
    })
}

function initializeFooterTrigger()
{
    new TriggerOnVisible('#upper-trigger', (target) =>
    {
        if (IS_LOADING_MORE) { return }

        const node = getNodeInMiddle()
        // console.log(node)

        if (centeredNode !== null)
        {
            centeredNode.classList.remove('test-sel')
        }
        centeredNode = node
        centeredNode.classList.add('test-sel')

        loadMore('/discover-get-content/5/')
    })

    new TriggerOnVisible('#lower-trigger', (target) =>
    {
        if (IS_LOADING_MORE) { return }

        const oldCount = 10
        const id = document.querySelector('.feed .post:last-child').id
        loadMore(`/discover-get-old-content/${oldCount}/${id}/`, false, false)
    })
}

const oldCount = 10
// const timestamp = Date.now().toDateString('YYYY-MM-DDTHH:mm:ss')
loadMore(`/discover-get-old-content/${oldCount}/${0}/`, false, false)

setTimeout(initializeFooterTrigger, 500)
