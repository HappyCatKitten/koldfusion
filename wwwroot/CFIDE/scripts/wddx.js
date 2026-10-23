/*
 * wddx.js - WDDX JavaScript objects (WddxSerializer, WddxRecordset)
 * KoldFusion Application Server 4.5
 */

function WddxRecordset() {}
WddxRecordset.prototype.getRowCount = function () {
    for (var col in this) if (typeof this[col] == "object" && this[col].length != null) return this[col].length;
    return 0;
};
WddxRecordset.prototype.getField = function (row, col) { return this[col.toLowerCase()][row]; };
WddxRecordset.prototype.setField = function (row, col, value) { this[col.toLowerCase()][row] = value; };
WddxRecordset.prototype.addColumn = function (name) {
    var n = this.getRowCount(), a = new Array();
    for (var i = 0; i < n; i++) a[i] = null;
    this[name.toLowerCase()] = a;
};
WddxRecordset.prototype.addRows = function (n) {
    for (var col in this) if (typeof this[col] == "object" && this[col].length != null)
        for (var i = 0; i < n; i++) this[col][this[col].length] = null;
};

function WddxSerializer() {}
WddxSerializer.prototype.serializeValue = function (v) {
    if (v == null) return "<null/>";
    var t = typeof v;
    if (t == "boolean") return "<boolean value='" + v + "'/>";
    if (t == "number") return "<number>" + v + "</number>";
    if (t == "string") return "<string>" + v.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") + "</string>";
    if (v instanceof Date)
        return "<dateTime>" + v.getFullYear() + "-" + (v.getMonth() + 1) + "-" + v.getDate() + "T" +
               v.getHours() + ":" + v.getMinutes() + ":" + v.getSeconds() + "</dateTime>";
    if (v instanceof Array) {
        var s = "<array length='" + v.length + "'>";
        for (var i = 0; i < v.length; i++) s += this.serializeValue(v[i]);
        return s + "</array>";
    }
    if (v instanceof WddxRecordset) {
        var cols = [];
        for (var c in v) if (typeof v[c] == "object" && v[c].length != null) cols[cols.length] = c;
        var r = "<recordset rowCount='" + v.getRowCount() + "' fieldNames='" + cols.join(",") + "'>";
        for (var j = 0; j < cols.length; j++) {
            r += "<field name='" + cols[j] + "'>";
            for (var k = 0; k < v[cols[j]].length; k++) r += this.serializeValue(v[cols[j]][k]);
            r += "</field>";
        }
        return r + "</recordset>";
    }
    var o = "<struct>";
    for (var key in v) if (typeof v[key] != "function") o += "<var name='" + key + "'>" + this.serializeValue(v[key]) + "</var>";
    return o + "</struct>";
};
WddxSerializer.prototype.serialize = function (v) {
    return "<wddxPacket version='1.0'><header/><data>" + this.serializeValue(v) + "</data></wddxPacket>";
};
