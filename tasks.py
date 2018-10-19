
import invoke


@invoke.task()
def build_doc_html(ctx):
    with ctx.cd("./doc"):
        ctx.run("sphinx-build -b html . ./_build/html")


@invoke.task()
def build_doc_latex(ctx):
    with ctx.cd("./doc"):
        ctx.run("sphinx-build -b latex . ./_build/latex")


@invoke.task()
def compile_latex(ctx):
    with ctx.cd("./doc/_build/latex"):
        ctx.run("pdflatex "
                "-output-format=pdf "
                "-output-directory=./pdf "
                "-aux-directory=./auxil "
                "spooky-console.tex ")
