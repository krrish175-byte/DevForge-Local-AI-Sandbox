def apply_rules(code: str, err: dict):
    etype = err["error_type"]
    line = err["line"]
    codeline = err["code_line"]

    lines = code.split("\n")

    # ----------------------------
    # ZeroDivisionError
    # ----------------------------
    if etype == "ZeroDivisionError":
        new = codeline.replace("/", "/ (y if y != 0 else 1)")
        lines[line - 1] = new
        return "\n".join(lines), "guard_zero_division"

    # ----------------------------
    # TypeError: str + int
    # ----------------------------
    if etype == "TypeError" and "+" in codeline:
        if '"' in codeline or "'" in codeline:
            new = codeline.replace("+", "+ str(") + ")"
            lines[line - 1] = new
            return "\n".join(lines), "fix_type_mismatch_str_int"

    # ----------------------------
    # ValueError invalid literal
    # ----------------------------
    if etype == "ValueError" and "int(" in codeline:
        new = f"    try:\n        {codeline}\n    except ValueError:\n        x = None"
        lines[line - 1] = new
        return "\n".join(lines), "guard_invalid_literal"

    # ----------------------------
    # IndexError out of range
    # ----------------------------
    if etype == "IndexError":
        # fix range loop boundaries
        new = "    " + codeline.replace("range(", "range(len(arr))")
        lines[line - 1] = new
        return "\n".join(lines), "fix_index_off_by_one"

    # ----------------------------
    # IndentationError
    # ----------------------------
    if etype == "IndentationError":
        lines[line - 1] = "    " + codeline.lstrip()
        return "\n".join(lines), "fix_indentation"

    return None, None