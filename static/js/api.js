
//#region Image

class ApiImage
{
    static GetPlainUrlStudyImage()
    {
        return ApiInternal.expandWithDefaults(
            {
                'url_long': '/study-image/{image_id}?time-planned={time}&sf={sf}&tags={tags}&tag-set={tagset}',
                'url_short': '/study-image/{image_id}',
                'keys': {
                    'image_id': '{image_id}',
                    'time': '{time}',
                    'sf': '{sf}',
                    'tags': '{tags}',
                    'tagset': '{tagset}'
                }
            },
            {
                'time': '120',
                'sf': '1',
                'tags': '',
                'tagset': 'all'
            })
    }

    static GetPlainUrlThumbImage()
    {
        return ApiInternal.expandWithDefaults(
            {
                'url_long': '/thumb/{image_id}.jpg',
                'url_short': '/thumb/{image_id}.jpg',
                'keys': {
                    'image_id': '{image_id}',
                }
            },
            {})

    }

    /**
     * @param id single int id
     * @param tryPreload
     * @returns Promise<{image_data}>
     */
    static GetSingle(id, tryPreload = false)
    {
        if (tryPreload)
        {
            new Image().src = '/image/' + id
        }
        return fetch("/image-info/" + id)
            .then(r =>
            {
                if (!r.ok) throw new Error("Not Ok")
                return r.json()
            })
    }

    /**
     * @param ids list of int ids
     * @returns Promise<[{image_data}]>
     */
    static GetBulk(ids)
    {
        return new Promise(resolve => resolve([{id:1},{id:2},{id:3}]))
    }

    static GetNextId(pivotId, method, dir, filterUrlParams = "")
    {
        return fetch(`/next-image/${dir}_${method}/${pivotId}?${filterUrlParams}`)
        .then(r =>
        {
            if (!r.ok) throw new Error('Not ok')
            return r.json()
        })
    }

    /**
     * @param id single int id
     * @returns Promise<current rating>
     */
    static GetRating(id)
    {
        return fetch(`/get-image-rating?image-id=${id}`)
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.text()
            })
    }

    /**
     * @param id single int id
     * @param offset rating OFFSET
     * @returns Promise<current rating>
     */
    static UpdateRatingSingle(id, offset)
    {
        return fetch(`/add-image-rating?image-id=${id}&rating=${offset}`)
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.text()
            })
    }

    /**
     * @param id single image id in the folder
     * @param offset rating OFFSET
     * @returns Promise<current rating>
     */
    static UpdateRatingFolder(id, offset)
    {
        return fetch(`/add-folder-rating?image-id=${id}&rating=${offset}`)
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return ApiImage.GetRating(id)
            })
    }

    /**
     * ! NOT TESTED ! NOT USED !
     * @param ids array of int ids
     * @param offset rating OFFSET
     * @returns Promise<current rating>
     */
    static UpdateRatingBulk(ids, offset)
    {
        const idsStr = ids.join(',')
        return fetch(`/add-mult-image-rating?image-id=${idsStr}&rating=${offset}`)
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.text()
            })
    }

    static UpdateLastViewed(id)
    {
        return fetch(`/set-image-last-viewed/${id}`)
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.text()
            })
    }

    static SetFavorite(id, value)
    {
        return fetch(`/set-image-fav/${id}/${value}`)
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.text()
            })
    }

    static GetPalette(id)
    {
        return fetch(`/color/palette/${id}`)
            .then(r =>
                {
                    if (!r.ok) throw new Error('Not ok')
                    return r.json()
                })
    }

    static PickColorAt(id, x, y)
    {
        return fetch(`/color-at-coord?image-id=${id}&x=${x}&y=${y}`)
            .then(r =>
                {
                    if (!r.ok) throw new Error('Not ok')
                    return r.json()
                })
    }

    static PaletteColorAdd(id, hex, x, y)
    {
        return fetch(`/save-image-color?image-id=${id}&x=${x}&y=${y}&hex=${hex}`)
            .then(r =>
                {
                    if (!r.ok) throw new Error('Not ok')
                    return r.json()
                })
    }

    static PaletteColorRemove(imageId, colorId)
    {
        return fetch(`/color/palette/remove/${imageId}/${colorId}`)
            .then(r =>
                {
                    if (!r.ok) throw new Error('Not ok')
                    return r.json()
                })
    }

    static RemoveImages(ids)
    {
        return fetch('/remove/images', ApiInternal.getPostRequest({'image_ids': ids}))
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.json()
            })
    }

    static RestoreRemovedImages(ids)
    {
        return fetch('/remove/restore', ApiInternal.getPostRequest({'image_ids': ids}))
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.json()
            })
    }

    static RemoveImagesPermanently(ids)
    {
        return fetch('/remove/permanent', ApiInternal.getPostRequest({'image_ids': ids}))
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.json()
            })
    }

}

//#endregion Image


//#region Tags

class ApiTags
{
    static GetImageTagEditorWidgetHtml()
    {
        return fetch('/embed-panel-tag-editor')
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.text()
            })
    }

    static GetImageTagFilterWidgetHtml()
    {
        return fetch('/embed-panel-tag-filter')
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.text()
            })
    }

    /**
     * @returns Promise<{colors, tags}>
     */
    static GetAllTags()
    {
        return fetch('/tags/all')
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.json()
            })
    }

    /**
     * @param ids list of int ids
     * @returns Promise<[{id, [tag]}]>
     */
    static GetBulk(ids)
    {
        return fetch('/tags/image/bulk', ApiInternal.getPostRequest({'image_ids': ids}))
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.json()
            })
    }

    /**
     * @param id single int id
     * @returns Promise<[{id, [tag]}]>
     */
    static GetSingle(id)
    {
        return fetch('/tags/image/single/' + id)
        .then(r =>
        {
            if (!r.ok) throw new Error('Not ok')
            return r.json()
        })
    }

    static GetAllTagSets()
    {
        return fetch('/tags/set-list')
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.json()
            })
    }

    static AddTags(imageIds, tags)
    {
        return fetch('/add-image-tags', ApiInternal.getPostRequest({'image_ids': imageIds, 'tags': tags}))
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.json()
            })
    }

    static RemoveTags(imageIds, tags)
    {
        return fetch('/remove-image-tags', ApiInternal.getPostRequest({'image_ids': imageIds, 'tags': tags}))
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.json()
            })
    }
}

//#endregion Tags


//#region Boards

class ApiBoards
{
    static GetWidgetHtml()
    {
        return fetch('/widget/get-boards-all')
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.text()
            })
    }

    static GetBoards()
    {
        return fetch('/boards/list')
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.text()
            })
    }

    static AddImageToBoard(boardId, imageIds)
    {
        return fetch('/board/add-images', ApiInternal.getPostRequest({'board_id': boardId, 'image_ids': imageIds}))
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.text()
            })
    }
}

//#endregion Boards


//#region Misc

class ApiMisc
{
    static getPopupYesNo()
    {
        return fetch('/misc/yesno')
            .then(r =>
            {
                if (!r.ok) throw new Error('Not ok')
                return r.text()
            })
    }
}

//#endregion Misc

class ApiInternal
{
    static getPostRequest(payload)
    {
        return {
            method: "POST",
            body: JSON.stringify(payload),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        }
    }

    static expandWithDefaults(obj, objDefaults)
    {
        obj.urlLongWithDefaults = () =>
        {
            let url = obj.url_long
            Object.keys(objDefaults).forEach(key =>
            {
                url = url.replace(obj['keys'][key], objDefaults[key])
            })

            return url
        }
        obj.urlShortWithDefaults = () =>
        {
            let url = obj.url_long
            Object.keys(objDefaults).forEach(key =>
            {
                url = url.replace(obj['keys'][key], objDefaults[key])
            })

            return url
        }
        return obj
    }
}

export { ApiImage, ApiTags, ApiBoards, ApiMisc }