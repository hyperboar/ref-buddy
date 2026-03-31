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
    stageSaveFetchedContainer.querySelector('#save-exported-urls').addEventListener('click', e =>
    {
        console.log('doing smth')
        const data = stageSaveFetchedContainer.querySelector('#fetched-url-result').value
        const jsonData = JSON.parse(data)
        ApiTagsAi
            .saveExportedUrls(jsonData)
            .then(json =>
            {
                console.log('saved!!')
            })
    })
}

document.addEventListener('DOMContentLoaded', () =>
{
    initializeComponents()
})



console.log('hello world')