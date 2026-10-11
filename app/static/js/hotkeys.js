
class Hotkeys {
    static _boundEvent = null
    static _mapping = null
    static _consumed = false

    // ctrl, shift, alt, Key*, Arrow*, NumAny (Digit* | Numpad*)
    static isDown(key_alias, evt = null, mapping = null) {

        if (Hotkeys._consumed) return

        // checking environment
        if (!evt && !Hotkeys._boundEvent) {
            throw new Error('Hotkeys. No event provided')
        }
        if (!evt) evt = Hotkeys._boundEvent

        if (!Hotkeys._mapping && !mapping) {
            throw new Error('Hotkeys. No event provided')
        }
        if (!mapping) mapping = Hotkeys._mapping

        if (!key_alias || key_alias === '') {
            throw new Error('Hotkeys. No key alias')
        }
        let key = mapping[key_alias]
        if (!key || key === '') {
            throw new Error('Hotkeys. No mapping for key ' + key_alias)
        }

        // actual hotkey press check
        let keys = key.replace(' ', '').split('+')
        const totalKeys = keys.length

        let conditions = []
        if (keys.includes('ctrl') && evt.ctrlKey) { conditions.push(true); Hotkeys.excludeKey(keys, 'ctrl') }
        if (keys.includes('shift') && evt.shiftKey) { conditions.push(true); Hotkeys.excludeKey(keys, 'shift') }
        if (keys.includes('alt') && evt.altKey) { conditions.push(true); Hotkeys.excludeKey(keys, 'alt') }
        if (keys.includes('Space') && evt.code === 'Space') { conditions.push(true); Hotkeys.excludeKey(keys, 'Space') }

        if (keys.includes('NumAny') && (evt.code.includes('Numpad') || evt.code.includes('Digit'))) { conditions.push(true); Hotkeys.excludeKey(keys, 'NumAny') }

        for (let k of keys) {
            if (k.startsWith('Key') && evt.code === k) { conditions.push(true) }
            if (k.startsWith('Arrow') && evt.code === k) { conditions.push(true) }
        }

        const isDown = conditions.length === totalKeys && conditions.every(c => c === true)
        if (isDown && Hotkeys._preventDefault) evt.preventDefault()
        if (isDown) Hotkeys._consumed = true
        return isDown
    }

    static excludeKey(keys, key) {
        const idx = keys.indexOf(key)
        if (idx < 0) return
        keys.splice(idx, 1)
    }

    static bindMapping(mapping) {
        if (!mapping) {
            throw new Error('Hotkeys. No key mapping provided')
        }

        Hotkeys._mapping = mapping
    }
    static unbindMapping() {
        Hotkeys._mapping = null
    }

    static bindEvent(evt) {
        if (!evt) {
            throw new Error('Hotkeys. No event provided')
        }
        Hotkeys._boundEvent = evt
    }
    static unbindEvent() {
        Hotkeys._boundEvent = null
    }

    static bindPreventDefaultOnDown(prevent) {
        Hotkeys._preventDefault = prevent
    }

    static reset() {
        Hotkeys._boundEvent = null
        Hotkeys._mapping = null
        Hotkeys._preventDefault = false
        Hotkeys._consumed = false
    }

}

export { Hotkeys }