export function parseLuaTable(str) {
    if (!str || typeof str !== 'string') return {};
    let pos = 0;
    const len = str.length;

    function skipWhitespace() { while (pos < len && /\s/.test(str[pos])) pos++; }

    function parseString() {
        const quote = str[pos]; pos++;
        let result = '';
        while (pos < len && str[pos] !== quote) {
            if (str[pos] === '\\' && pos + 1 < len) { pos++; result += str[pos]; }
            else { result += str[pos]; }
            pos++;
        }
        pos++;
        return result;
    }

    function parseNumber() {
        let numStr = '';
        if (str[pos] === '-') { numStr += str[pos]; pos++; }
        while (pos < len && /[0-9.]/.test(str[pos])) { numStr += str[pos]; pos++; }
        return parseFloat(numStr);
    }

    function parseIdentifier() {
        let id = '';
        while (pos < len && /[a-zA-Z0-9_\u4e00-\u9fa5]/.test(str[pos])) { id += str[pos]; pos++; }
        return id;
    }

    function parseValue() {
        skipWhitespace();
        if (pos >= len) return null;
        const char = str[pos];
        if (char === '"' || char === "'") return parseString();
        if (char === '{') return parseTable();
        if (/[0-9]/.test(char) || (char === '-' && pos + 1 < len && /[0-9]/.test(str[pos + 1]))) return parseNumber();
        const id = parseIdentifier();
        if (id === 'true') return true;
        if (id === 'false') return false;
        if (id === 'nil') return null;
        return id;
    }

    function parseTable() {
        const result = {}; let arrayIndex = 1;
        pos++; skipWhitespace();
        while (pos < len && str[pos] !== '}') {
            skipWhitespace();
            if (str[pos] === '}') break;
            let key, value;
            if (str[pos] === '[') {
                pos++; skipWhitespace();
                key = (str[pos] === '"' || str[pos] === "'") ? parseString() : parseNumber();
                skipWhitespace(); pos++; skipWhitespace(); pos++; skipWhitespace();
                value = parseValue();
            } else if (/[a-zA-Z_\u4e00-\u9fa5]/.test(str[pos])) {
                key = parseIdentifier(); skipWhitespace();
                if (str[pos] === '=') { pos++; skipWhitespace(); value = parseValue(); }
                else { value = key; key = arrayIndex; }
            } else { key = arrayIndex; value = parseValue(); }
            result[key] = value;
            if (typeof key === 'number' && key === arrayIndex) arrayIndex++;
            skipWhitespace();
            if (str[pos] === ',') { pos++; skipWhitespace(); }
        }
        pos++;
        return result;
    }

    skipWhitespace();
    return str[pos] === '{' ? parseTable() : {};
}
