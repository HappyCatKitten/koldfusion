/*
 * cfform.js - client-side validation for CFFORM / CFINPUT
 * KoldFusion Application Server 4.5
 * Works in Netscape Navigator 3.0+ and Internet Explorer 4.0+ (and, it
 * turns out, everything since).
 */

function _CF_onError(form_object, input_object, object_value, error_message)
{
    alert(error_message);
    if (input_object && input_object.focus) input_object.focus();
    return false;
}

function _CF_hasValue(obj, obj_type)
{
    if (obj_type == "TEXT" || obj_type == "PASSWORD" || obj_type == "TEXTAREA")
    {
        if (obj.value.length == 0)
            return false;
        for (var i = 0; i < obj.value.length; i++)
            if (obj.value.charAt(i) != " ") return true;
        return false;
    }
    else if (obj_type == "SELECT")
    {
        for (var i = 0; i < obj.length; i++)
            if (obj.options[i].selected && obj.options[i].value != "") return true;
        return false;
    }
    else if (obj_type == "SINGLE_VALUE_RADIO" || obj_type == "SINGLE_VALUE_CHECKBOX")
    {
        return obj.checked;
    }
    else if (obj_type == "RADIO" || obj_type == "CHECKBOX")
    {
        if (obj.length == null) return obj.checked;
        for (var i = 0; i < obj.length; i++)
            if (obj[i].checked) return true;
        return false;
    }
    return true;
}

function _CF_checkinteger(object_value)
{
    if (object_value.length == 0) return true;
    var start = 0;
    if (object_value.charAt(0) == "-" || object_value.charAt(0) == "+") start = 1;
    if (start == object_value.length) return false;
    for (var i = start; i < object_value.length; i++)
        if ("0123456789".indexOf(object_value.charAt(i)) == -1) return false;
    return true;
}

function _CF_checknumber(object_value)
{
    if (object_value.length == 0) return true;
    var start = 0, dot = false, digits = 0;
    if (object_value.charAt(0) == "-" || object_value.charAt(0) == "+") start = 1;
    for (var i = start; i < object_value.length; i++)
    {
        var c = object_value.charAt(i);
        if (c == ".") { if (dot) return false; dot = true; }
        else if ("0123456789".indexOf(c) == -1) return false;
        else digits++;
    }
    return digits > 0;
}

function _CF_checkrange(object_value, min_value, max_value)
{
    if (object_value.length == 0) return true;
    if (!_CF_checknumber(object_value)) return false;
    var n = parseFloat(object_value);
    if (min_value != null && n < min_value) return false;
    if (max_value != null && n > max_value) return false;
    return true;
}

function _CF_numberrange(object_value, min_value, max_value) { return _CF_checkrange(object_value, min_value, max_value); }

function _CF_checkdaterange(m, d, y)
{
    if (m < 1 || m > 12 || d < 1 || y < 0) return false;
    var days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    if ((y % 4 == 0 && y % 100 != 0) || y % 400 == 0) days[1] = 29;
    return d <= days[m - 1];
}

function _CF_splitdate(object_value)
{
    var parts = object_value.split(/[\/\-\.]/);
    if (parts.length != 3) return null;
    for (var i = 0; i < 3; i++) if (!_CF_checkinteger(parts[i]) || parts[i].length == 0) return null;
    var y = parseInt(parts[2], 10);
    if (parts[2].length <= 2) y += (y < 30) ? 2000 : 1900;
    return [parseInt(parts[0], 10), parseInt(parts[1], 10), y];
}

function _CF_checkdate(object_value)
{
    if (object_value.length == 0) return true;
    var p = _CF_splitdate(object_value);
    return p != null && _CF_checkdaterange(p[0], p[1], p[2]);
}

function _CF_checkeurodate(object_value)
{
    if (object_value.length == 0) return true;
    var p = _CF_splitdate(object_value);
    return p != null && _CF_checkdaterange(p[1], p[0], p[2]);
}

function _CF_checktime(object_value)
{
    if (object_value.length == 0) return true;
    var parts = object_value.split(":");
    if (parts.length < 2 || parts.length > 3) return false;
    for (var i = 0; i < parts.length; i++) if (!_CF_checkinteger(parts[i]) || parts[i].length == 0) return false;
    var h = parseInt(parts[0], 10), m = parseInt(parts[1], 10), s = parts.length == 3 ? parseInt(parts[2], 10) : 0;
    return h >= 0 && h <= 23 && m >= 0 && m <= 59 && s >= 0 && s <= 59;
}

function _CF_checkphone(object_value)
{
    if (object_value.length == 0) return true;
    return /^\(?\d{3}\)?[ \-\.]?\d{3}[ \-\.]?\d{4}$/.test(object_value);
}

function _CF_checkzip(object_value)
{
    if (object_value.length == 0) return true;
    return /^\d{5}([ \-]\d{4})?$/.test(object_value);
}

function _CF_checkssn(object_value)
{
    if (object_value.length == 0) return true;
    return /^\d{3}[ \-]?\d{2}[ \-]?\d{4}$/.test(object_value);
}

function _CF_checkcreditcard(object_value)
{
    if (object_value.length == 0) return true;
    var digits = "";
    for (var i = 0; i < object_value.length; i++)
    {
        var c = object_value.charAt(i);
        if ("0123456789".indexOf(c) != -1) digits += c;
        else if (c != " " && c != "-") return false;
    }
    if (digits.length < 13 || digits.length > 16) return false;
    var sum = 0, dbl = false;
    for (var j = digits.length - 1; j >= 0; j--)
    {
        var n = parseInt(digits.charAt(j), 10);
        if (dbl) { n *= 2; if (n > 9) n -= 9; }
        sum += n;
        dbl = !dbl;
    }
    return sum % 10 == 0;
}

/* CFTREE (HTML rendition) */
function _CF_getById(id)
{
    return document.getElementById ? document.getElementById(id) : (document.all ? document.all[id] : null);
}

function _CF_treeToggle(id)
{
    var el = _CF_getById(id), mark = _CF_getById(id + "_m");
    if (!el) return;
    var open = (el.style.display == "none");
    el.style.display = open ? "block" : "none";
    if (mark) mark.innerHTML = open ? "[-]" : "[+]";
}

function _CF_treeSelect(tree, value, path)
{
    for (var i = 0; i < document.forms.length; i++)
    {
        var f = document.forms[i];
        if (f[tree + ".node"])
        {
            f[tree + ".node"].value = value;
            if (f[tree + ".path"]) f[tree + ".path"].value = (path != null) ? path : value;
            window.status = "Selected: " + value;
        }
    }
}
