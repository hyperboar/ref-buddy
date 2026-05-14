import {ApiTagsAi} from 'api'

let stageFetchContainer
let stageSaveFetchedContainer
let stagePollTagsContainer

function initializeComponents()
{
    stageFetchContainer = document.querySelector('#fetch-tags-container')
    stageSaveFetchedContainer = document.querySelector('#save-fetched-container')
    stagePollTagsContainer = document.querySelector('#poll-tags-container')

    // stage 1
    stageFetchContainer.querySelector('#fetch-urls').addEventListener('click', e =>
    {
        let tags = stageFetchContainer.querySelector('#tags').value.toString()
        tags = tags.trim()
        const limit = stageFetchContainer.querySelector('#limit').value
        ApiTagsAi
            .getExportUrls(tags, limit)
            .then(json =>
            {
                stageSaveFetchedContainer.querySelector('#fetch-url-result-count').innerHTML = json.length
                stageSaveFetchedContainer.querySelector('#fetched-url-result').value = JSON.stringify(json)
            })
    })

    // stage 2
    stageSaveFetchedContainer.querySelector('#save-exported-urls').addEventListener('click', evt =>
    {
        console.log('doing smth')
        const data = stageSaveFetchedContainer.querySelector('#fetched-url-result').value
        const jsonData = JSON.parse(data)

        evt.target.classList.remove('op-success', 'op-fail')
        evt.target.classList.add('loading')

        ApiTagsAi
            .saveExportedUrls(jsonData)
            .then(json =>
            {
                evt.target.classList.add('op-success')
                console.log('saved!!')
            })
            .catch(error =>
            {
                evt.target.classList.add('op-fail')
            })
            .finally(() =>
            {
                evt.target.classList.remove('loading')
            })
    })
}

document.addEventListener('DOMContentLoaded', () =>
{
    initializeComponents()
})



console.log('hello world')