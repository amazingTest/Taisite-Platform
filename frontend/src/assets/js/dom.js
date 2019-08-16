export function parentsUntil (el, selector, filter) {
    const result = []
    const matchesSelector = el.matches || el.webkitMatchesSelector || el.mozMatchesSelector || el.msMatchesSelector

    el = el.parentElement

    while (el && !matchesSelector.call(el, selector)) {
        if (!filter) {
            result.push(el)
        } else {
            if (matchesSelector.call(el, filter)) {
                result.push(el)
            }
        }

        el = el.parentElement
    }

    return result
}

export function closest (el, selector) {
    const matchesSelector = el.matches || el.webkitMatchesSelector || el.mozMatchesSelector || el.msMatchesSelector

    while (el) {
        if (matchesSelector.call(el, selector)) {
            return el
        } else {
            el = el.parentElement
        }
    }

    return null
}
