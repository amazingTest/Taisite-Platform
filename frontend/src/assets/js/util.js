/**
 * 格式化日期
 * @param {string} dateLike 一个可以转换为日期对象的字符串
 * @param {string} format 格式字符串
 */
export function formatDate (dateLike, format) {
    const date = new Date(dateLike)
    const hours = '' + date.getHours()
    const mins = '' + date.getMinutes()
    const seconds = '' + date.getSeconds()
    const fullYears = '' + date.getFullYear()
    const months = '' + (date.getMonth() + 1)
    const days = '' + date.getDate()
    const years = fullYears.substring(2)
    let result

    format = format || 'YYYY-MM-DD'
    result = format.replace('YYYY', fullYears)
    result = result.replace('YY', years)
    result = result.replace('MM', months.padStart(2, '0'))
    result = result.replace('DD', days.padStart(2, '0'))
    result = result.replace('hh', hours.padStart(2, '0'))
    result = result.replace('mm', mins.padStart(2, '0'))
    result = result.replace('ss', seconds.padStart(2, '0'))

    return result
}

/**
 * 根据字符串路径生成一个js对象
 * @param {string} field 字符串路径
 * @param {fixed} value 路径末端的值
 * 例: field: 'a.b'
 *     value: 2
 *     则返回 { a: { b: 2 } }
 */
export function newObject (field, value) {
    if (!field) return
    const fields = field.split('.')
    const result = {}
    let temp = result

    for (let i = 0; i < fields.length; i++) {
        if (i === fields.length - 1) {
            temp[fields[i]] = value
        } else {
            temp[fields[i]] = {}
            temp = temp[fields[i]]
        }
    }

    return result
}

/**
 * 根据字符串获取嵌套数据
 * @param {object} data 数据源
 * @param {string} field 目标数据路径
 * 例: data: { a: { b: 2 } }
 *    field: 'a.b'
 *    则返回 2
 */
export function getValueFromObject (data, field) {
    if (!field) {
        return
    }

    const fields = field.split('.')
    let result = data

    fields.forEach(f => {
        if (result) {
            result = result[f]
        }
    })

    return result
}

export function checkEmpty (fields) {
    if (!Array.isArray(fields)) {
        return false
    }

    return !fields.some(element => {
        return element === '' || element === null || element === undefined || element.length === 0 || (typeof element === 'number' && isNaN(element))
    })
}

/**
 * 将基础类型的变量值转换为易懂的文字
 * @param {mixed} value 变量值
 * @param {string} type 变量值类型
 * @param {array} options 选项列表（针对type为Option）
 */
export function varToText (value, type, options) {
    if (type === 'Boolean') {
        if (value === true) {
            return '是/有'
        }

        if (value === false) {
            return '否/无'
        }

        return value
    }

    if (type === 'Option' && Array.isArray(options)) {
        const targetOption = options.find(o => o.value === value)

        return targetOption ? targetOption.label : ''
    }

    return value
}
