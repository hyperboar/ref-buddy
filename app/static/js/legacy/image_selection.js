/**
 * Allows for selection of certain tiles in the grid.<br/>
 * Selected ids can then be fetched from ImageSelection.selectedIds.</br>
 * <br/>
 * Class uses some hardcoded css style names. Check fields called class* <br/>
 * Html layout is supposed to be like this:
 * @example
 * <button id="">Toggle selection</button>
 * <div class="gallery">
 *      <div class="tile">
 *          <a href>
 *              <img src="" data-id="some_id">
 *          </a>
 *      </div>
 * </div>
 *
 */
class ImageSelection
{
    toggleBtn

    classGallery
    classTile

    selectionMode = false
    selectedIds = []
    lastClickedTile = null

    classNoSelect = 'no-select'
    classModeBtn = 'select-mode-btn'
    classSelectable ='selectable'
    classSelected ='selected'
    classDisabled ='disabled'
    classBodyModeOn = 'body-sel-mode-on'

    attrDataId = 'data-id'

    tileClickAction = (e) => this.onTileSelectionClick(e)

    constructor(toggleBtnId, classGallery, classTile)
    {
        this.classGallery = classGallery
        this.classTile = classTile

        this.toggleBtn = document.getElementById(toggleBtnId)

        this.toggleBtn.addEventListener('click', () => this.toggleSelectionMode());
    }

    /**
     * Go through all available tiles and assign/remove click callback to each classTile element.
     */
    toggleSelectionMode()
    {
        this.selectionMode = !this.selectionMode;

        console.log(`${this.selectionMode}`)

        // Add or remove event listeners and update UI based on selection mode state
        if (this.selectionMode)
        {
            document.querySelector('body').classList.add(this.classBodyModeOn)
            document.querySelector(this.classGallery).classList.add(this.classNoSelect)
            this.toggleBtn.classList.add(this.classModeBtn)

            // Disable other interactions and enable selection mode UI
            document.querySelectorAll(this.classTile).forEach((tile) =>
            {
                tile.querySelector('a').classList.add(this.classDisabled)
                tile.addEventListener('click', this.tileClickAction)

                const img = tile.querySelector('img')
                img.classList.remove(this.classSelected)
                img.classList.add(this.classSelectable)
            });
        }
        else
        {
            this.selectedIds = []

            document.querySelector('body').classList.remove(this.classBodyModeOn)
            document.querySelector(this.classGallery).classList.remove(this.classNoSelect)
            this.toggleBtn.classList.remove(this.classModeBtn)

            // Enable other interactions and disable selection mode UI
            document.querySelectorAll(this.classTile).forEach((tile) =>
            {
                tile.querySelector('a').classList.remove(this.classDisabled)
                tile.removeEventListener('click', this.tileClickAction);

                const img = tile.querySelector('img')
                img.classList.remove(this.classSelectable)
                img.classList.remove(this.classSelected)
            });
        }
    }

    selectAll()
    {
        document.querySelectorAll(this.classTile).forEach((tile) =>
        {
            this.handleTileClick(tile)
            this.lastClickedTile = null
        })
    }

    onTileSelectionClick(event)
    {
        this.handleTileClick(event.currentTarget, false, event.shiftKey)
    }

    /**
     * The thing that assigns classes and processes batch selection recursively.
     * @param tile
     * @param isBatch
     * @param isShift whether or not shift key is down
     */
    handleTileClick(tile, isBatch=false, isShift=false)
    {
        const tileId = tile.getAttribute(this.attrDataId)

        // add, batch select, this tile NOT included
        if (isBatch && !this.selectedIds.includes(tileId))
        {
            this.selectedIds.push(tileId)
            const img = tile.querySelector('img')
            img.classList.add(this.classSelected);
        }
        // add, single select, this tile NOT included
        else if (!isBatch && !this.selectedIds.includes(tileId))
        {
            this.selectedIds.push(tileId)
            const img = tile.querySelector('img')
            img.classList.add(this.classSelected);
        }
        // remove, single select, this tile IS included
        else if (!isBatch && this.selectedIds.includes(tileId))
        {
            const idx = this.selectedIds.indexOf(tileId);
            if (idx !== -1) this.selectedIds.splice(idx, 1);
            const img = tile.querySelector('img')
            img.classList.remove(this.classSelected);
        }


        // stop when BATCH select, recursion stop
        if (isBatch) { return }

        if (isShift && this.lastClickedTile)
        {
            const dir = this.findSiblingDirection(this.lastClickedTile, tile)
            let getNextTile = cur => dir > 0 ? cur.nextElementSibling : cur.previousElementSibling
            let nextTile = getNextTile(this.lastClickedTile)
            while(nextTile !== tile)
            {
                this.handleTileClick(nextTile, true)
                nextTile = getNextTile(nextTile)
            }
        }

        this.lastClickedTile = tile
    }

    findSiblingDirection(elem1, elem2)
    {
        if (elem1 === elem2) { return 0 }

        let run = elem1
        while (run != null)
        {
            if (run === elem2) { return 1 }
            run = run.nextElementSibling
        }

        return -1
    }
}