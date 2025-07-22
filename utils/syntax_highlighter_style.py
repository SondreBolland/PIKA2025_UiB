from pygments.style import Style
from pygments.token import Comment, Keyword, Name, String, Number, Operator, Generic

class SyntaxHighlighterStyle(Style):
    default_style = ""
    background_color = "#ffffff"
    styles = {
        Comment:        'italic #008200',
        Keyword:        'bold #006699',
        Name.Function:  '#000000',
        Name.Class:     '#0066cc',
        Name.Builtin:   '#ff1493',
        Name.Variable:  '#aa7700',
        String:         '#0000ff',
        Number:         '#009900',
        Operator:       '#000000',
        Generic:        '#000000',
    }
