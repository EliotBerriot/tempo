import markdown
from markdown.extensions import Extension


class EscapeHtml(Extension):
    def extendMarkdown(self, md, md_globals):
        del md.preprocessors['html_block']
        del md.inlinePatterns['html']


def safe_markdown(text):
    return markdown.markdown(text, extensions=[EscapeHtml()])
