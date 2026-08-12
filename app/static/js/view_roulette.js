import {ApiImage} from 'api'

const kStorageKey = 'roulette_history'
const tmlHistory = document.querySelector('.history template')
const tplCard = document.querySelector('.deck template')
let history

const cardList = [
    {
        query: 'academic',
        imageId: '42834'
    },
    {
        query: 'stl_kakure',
        imageId: '316338'
    },
    {
        query: 'ai,-ai_stylized',
        imageId: '197888'
    }
]

function setDefaultValues() {

}

async function getRandom(pivot, tags) {
    const imgInfo = await ApiImage.GetNextId(pivot, 'rnd', 'fwd', 'tags='+tags)
    return imgInfo.id
}


function initDeck() {

    const deck = document.querySelector('.deck')

    for (let i in cardList) {
        let el = document.importNode(tplCard.content, true)
        deck.appendChild(el)
        el = deck.lastElementChild
        populateCard(el, cardList[i].imageId)
        el.querySelector('textarea').textContent = cardList[i].query
    }

    // rand
    document.querySelectorAll('.card-controls .ref-rand').forEach((btn, idx) => {
        btn.addEventListener('click', async evt => {
            const card = btn.closest('.card')
            let imageId = card.getAttribute('data-image-id')
            const text = card.querySelector('textarea')
            imageId = await getRandom(imageId, text.value)
            populateCard(card, imageId)
        })
    })

    // by id
    document.querySelectorAll('.card-controls .ref-id').forEach((btn, idx) => {
        btn.addEventListener('click', async evt => {
            const card = btn.closest('.card')
            const text = card.querySelector('.image-id')
            populateCard(card, text.value)
        })
    })
}

function populateCard(card, imageId) {
    card.setAttribute('data-image-id', imageId)
    card.querySelector('img').src = `/image/${imageId}`
    card.querySelector('a').href = `/study-image/${imageId}`
    card.querySelector('input.image-id').value = imageId
}

function loadHistory() {
    history = document.querySelector('.history')

    localStorage.getItem(kStorageKey)
}

document.addEventListener('DOMContentLoaded', () =>
{
    initDeck()
    loadHistory()
    setDefaultValues()
})

