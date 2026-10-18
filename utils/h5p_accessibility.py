"""Narrow accessibility fixes for the bundled H5P MultiChoice runtime."""

def repair_runtime(html: str) -> str:
    # MultiChoice's result/reset handlers must target only their own question.
    # The exports contain two minifier variants with different local names.
    html = html.replace('s(".h5p-answers")', 'l')
    html = html.replace('a(".h5p-answers")', 'h')
    # The named visual wall needs an image role; its drawing is unchanged.
    return html.replace('class="karel-trace__wall" aria-label="wall"',
                        'class="karel-trace__wall" role="img" aria-label="wall"')
