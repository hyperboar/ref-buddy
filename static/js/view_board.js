import {ApiBoards} from 'api'
import {Hotkeys, OSInfo} from '/static/js/main.js'
import {BoardImage, BoardBoard} from '/static/js/board_item.js'


let boardImages = {}
let board = null
let hotkeys = null

const boardId = document.querySelector('#board-id').textContent

// Save image position to the database
function saveImageTransform(imageData)
{
    const image = board.items[imageData.image_id].node
    image.classList.remove('op-success', 'op-fail')
    return ApiBoards.SaveBoardImageTransform(boardId, imageData)
        .catch(err =>
        {
            image.classList.add('op-fail')
            console.log(err)
        })
}


// Initialize the board
function initializeBoard()
{
    hotkeys = new Hotkeys()

    board = new BoardBoard()
    board.setGetIsDragAllowed(() => hotkeys.isPressed('Space'))
    board.setGetIsScaleAllowed(() => hotkeys.isPressed('Space'))

    // Fetch image data from the database
    ApiBoards.GetBoardImages(boardId)
        .then(imageData =>
        {
            // Render images on the board
            imageData.images.forEach(data =>
            {
                boardImages[data.image_id] = data
                const item = new BoardImage(data)
                board.addItem(data.image_id, item)
                item.setOnSaveTransform((data) => saveImageTransform(data))
                item.setGetIsDragAllowed(() => hotkeys.isPressed('KeyCtrl'))
                item.setGetIsScaleAllowed(() => hotkeys.isPressed('KeyCtrl'))
                item.setGetIsRemoveAllowed(() => hotkeys.isPressed('KeyX'))
                item.setGetIsStudyAllowed(() => hotkeys.isPressed('KeyS') || OSInfo.isMultitouch)

                item.onGoToStudyCompleted = () => { hotkeys.cancelKey('KeyS') }
            })
        })
}

// Initialize the board when the page loads
document.addEventListener('DOMContentLoaded', initializeBoard)

document.addEventListener('hotkeyDown', (e) =>
{
    if (e.detail.isPressedMult(['Space', 'KeyR']))
    {
        board.setPosition(0,0)
        board.setScale(1)
    }

    if (e.detail.isPressed(['Space']))
    {
        Object.values(board.items).forEach(item =>
        {
            item.setMovableEnabled(false)
            item.setScalableEnabled(false)
        })
    }
})
document.addEventListener('hotkeyUp', (e) =>
{
    if (!e.detail.isPressed(['Space']))
    {
        Object.values(board.items).forEach(item =>
        {
            item.setMovableEnabled(true)
            item.setScalableEnabled(true)
        })
    }
})