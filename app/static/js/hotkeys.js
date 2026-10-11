
class Hotkeys {
    static _boundEvent = null
    static _mapping = null
    static _consumed = false

    static _mods = {
        'ctrl': function(e) { return e.ctrlKey },
        'shift': function(e) { return e.shiftKey },
        'alt': function(e) { return e.altKey },
        'meta': function(e) { return e.metaKey }
    }

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

        let conditions = []

        // special cases: mods and numbers
        conditions.push(Hotkeys._checkModifyRequired(keys, 'ctrl', evt));  this._excludeKey(keys, 'ctrl')
        conditions.push(Hotkeys._checkModifyRequired(keys, 'shift', evt)); this._excludeKey(keys, 'shift')
        conditions.push(Hotkeys._checkModifyRequired(keys, 'alt', evt));   this._excludeKey(keys, 'alt')
        conditions.push(Hotkeys._checkModifyRequired(keys, 'meta', evt));  this._excludeKey(keys, 'meta')

        // fail early
        if (!conditions.every(c => c === true)) return false

        if (keys.includes('NumAny')) {
            conditions.push(evt.code.includes('Numpad') || evt.code.includes('Digit'))
            this._excludeKey(keys, 'NumAny')
        }

        // the rest of the keys
        for (let k of keys) {
            if (keys.includes(k)) conditions.push(evt.code === k)
        }

        const isDown = conditions.every(c => c === true)
        if (isDown && Hotkeys._preventDefault) evt.preventDefault()
        if (isDown) Hotkeys._consumed = true
        return isDown
    }

    static _checkModifyRequired(keys, key, evt) {
        return (keys.includes(key) &&  Hotkeys._mods[key](evt)) ||
              (!keys.includes(key) && !Hotkeys._mods[key](evt))
    }

    static _excludeKey(keys, key) {
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