import {ApiTags} from 'api'
import {UrlWrapper} from '/static/js/main.js'

class TagSetList
{
    list

    constructor(selList, selectValue = null)
    {
        this.list = document.querySelector(selList)

        ApiTags.GetAllTagSets()
            .then(data =>
            {
                data.forEach(item =>
                {
                    const option = document.createElement("option");
                    option.text = item.name
                    option.value = item.alias
                    this.list.add(option)
                })

                this.list.remove(0)

                const url = new UrlWrapper(window.location.href)
                this.value = url.getSearch('tag-set')
            })

        this.list.addEventListener('change', (e) => { this.onChange(e) })
    }

    onChange(e)
    {
        const newVal = this.value
        const url = new UrlWrapper(window.location.href)
        const oldVal = url.getSearch('tag-set')

        if (oldVal === newVal) return

        url.setSearch('tag-set', newVal)
        url.updateLocationHref()
    }

    set value(val)
    {
        let idx = Array.from(this.list.options).findIndex(o => o.value === val)
        if (idx === this.list.selectedIndex) return

        if (idx === -1) idx = 0
        this.list.selectedIndex = idx
    }

    get value()
    {
        return this.getValueByIndex(this.list.selectedIndex)
    }

    getValueByIndex(idx)
    {
        return this.list.options[idx].value
    }
}

export { TagSetList }