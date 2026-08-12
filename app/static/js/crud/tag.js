import {ApiTags} from 'api'

const tplTag = document.querySelector('template#tpl-tag')
const tagsList = document.querySelector('#tags-list')
const form = document.querySelector('#tag-form')

let tagColors


function addTagToList(data, firstSibling = false) {

    const node = tplTag.content.cloneNode(true)
    const tr = node.querySelector('tr')
    tr.id = tr.id + data.id
    tr.setAttribute('data-id', data.id)
    node.querySelector('#id').textContent  = data.id
    node.querySelector('#name').textContent  = data.name
    node.querySelector('#name').style.color = data.hex
    node.querySelector('#color').textContent = data.c
    node.querySelector('#color').style.color = data.hex
    node.querySelector('#update').addEventListener('click', setUpdateTag)
    node.querySelector('#delete').addEventListener('click', deleteTag)

    tr.setAttribute('data', JSON.stringify(data))

    if (!firstSibling)
        tagsList.appendChild(node)
    else
        tagsList.prepend(node)
}

function loadList() {
    ApiTags.GetAllTags().then(json => {
        tagColors = json.colors
        const tags = Array.from(json.tags)
        tags.sort(function(a,b) {
            return a.c - b.c || a.name.localeCompare(b.name) || a.id - b.id
        })

        tags.forEach(t =>  t.hex = tagColors[t.c])
        tags.forEach(t => addTagToList(t))

        initializeForm(tagColors)

        document.querySelector('#add-tag-btn').addEventListener('click', setCreateTag)
    })
}

function initializeForm(colors) {
    const s = form.querySelector('select')
    Object.keys(colors).forEach(key => {
        console.log(key)
        const op = document.createElement('option')
        op.value = key
        op.textContent = key + ' ' + colors[key]
        op.style.color = colors[key]
        s.appendChild(op)
    })
}

function setFormAction(action) {
    const selector = 'input[type="submit"]'
    let submit = form.parentNode.querySelector(selector)
    submit.replaceWith(submit.cloneNode(true))
    submit = form.parentNode.querySelector(selector)

    if (action === 'add') {
        submit.addEventListener('click', createTag)
    }
    else if (action === 'update') {
        submit.addEventListener('click', updateTag)
    }

    form.classList.remove('hidden')
}

function setCreateTag(evt) {
    setFormAction('add')

    form.querySelector('#id').removeAttribute('value')
    form.querySelector('#tag').value = ''
    form.querySelector('#color').value = 0
}

function setUpdateTag(evt) {
    setFormAction('update')

    const data = JSON.parse(evt.target.closest('tr').getAttribute('data'))

    form.querySelector('#id').value = data.id
    form.querySelector('#tag').value = data.name
    form.querySelector('#color').value = data.c
}

function createTag(evt) {
    evt.preventDefault()
    evt.stopPropagation()

    const data = Object.fromEntries(new FormData(form))

    ApiTags.CreateTag(data)
        .then(json => {
            console.log('success')
            form.classList.add('hidden')
            data.id = json.id
            data.hex = tagColors[data.color]
            addTagToList(data, true)

        }).catch(e => {
            console.log('oops')
            console.error(e)
        })
}

function updateTag(evt) {
    evt.preventDefault()
    evt.stopPropagation()

    const formData = Object.fromEntries(new FormData(form))

    ApiTags.UpdateTag(formData)
        .then(json => {
            console.log('success')
            form.classList.add('hidden')

            const tr = document.querySelector(`tr#tag-${formData.id}`)
            const data = JSON.parse(tr.getAttribute('data'))
            data.name = formData.name
            data.c = form.querySelector('#color').value
            data.hex = tagColors[data.c]
            tr.setAttribute('data', JSON.stringify(data))

            tr.querySelector('#name').textContent  = data.name
            tr.querySelector('#name').style.color = data.hex
            tr.querySelector('#color').textContent = data.c
            tr.querySelector('#color').style.color = data.hex

        }).catch(e => {
            console.log('oops')
            console.error(e)
        })
}

function deleteTag(evt) {
    evt.preventDefault()
    evt.stopPropagation()

    const data = JSON.parse(evt.target.closest('tr').getAttribute('data'))
    if (!confirm(`Delete tag '${data.id}:${data.name}'?`)) return

    ApiTags.DeleteTag(data.id)
        .then(json => {
            console.log('success')
            form.classList.add('hidden')
            evt.target.closest('tr').remove()
        }).catch(e => {
            console.log('oops')
            console.error(e)
        })
}

document.addEventListener('DOMContentLoaded', () =>
{
    loadList()
})