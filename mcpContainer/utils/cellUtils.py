def run_cell(code: str, context: dict):
    import io, sys, traceback

    buffer = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buffer

    result = None
    error = None

    try:
        stripped = code.strip()
        if not stripped:
            return {"stdout": "", "result": None, "error": None}

        lines = stripped.splitlines()

        # Try evaluating last line as expression
        try:
            last_expr = compile(lines[-1], "<cell>", "eval")
        except SyntaxError:
            # Not an expression → just exec everything
            exec(stripped, context)
        else:
            # Expression case → exec all but last, eval last
            if len(lines) > 1:
                exec("\n".join(lines[:-1]), context)
            result = eval(last_expr, context)

    except Exception:
        error = traceback.format_exc()
    finally:
        sys.stdout = old_stdout

    return {
        "stdout": buffer.getvalue(),
        "result": result,
        "error": error,
    }
