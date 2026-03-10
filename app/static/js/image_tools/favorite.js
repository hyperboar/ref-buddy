import {ApiImage}       from 'api'

class Fav
{
    imageId
    btn

    _evtOnFav = 'fav'
    
    constructor(id, selButton) 
    {
        this.imageId = id

        this._onFav = new CustomEvent(this._evtOnFav, { detail: { fav: this }});

        this.btn = document.querySelector(selButton)

        this.btn.addEventListener('click', () =>
        {
            let val = (parseInt(this.btn.value) + 1) % 2
    
            this.btn.classList.add('loading')

            ApiImage.SetFavorite(this.imageId, val)
                .then((_) =>
                {
                    this.btn.value = val
                    this.update(this.isFav)

                    document.dispatchEvent(this._onFav)
                })
                .finally(() =>
                {
                    this.btn.classList.remove('loading')
                })
        })
    }

    get isFav()
    {
        console.log(this.btn.value)
        return this.btn.value === "1"
    }
    
    setData(id, isFav)
    {
        this.imageId = id
        this.btn.value = isFav ? "1" : "0"
    }

    update(isFav)
    {
        if (isFav)
        {
            this.btn.classList.add('on')
        }
        else
        {
            this.btn.classList.remove('on')
        }
    }
}

export { Fav }