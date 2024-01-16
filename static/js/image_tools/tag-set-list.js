import {ApiTags} from 'api'

class TagSetList
{
    list

    constructor(selList)
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
                this.list.selectedIndex = 0
            })
    }

    get value()
    {
        return this.list.value
    }
}

export { TagSetList }