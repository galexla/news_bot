from utils.misc import get_text_excerpts


def test_get_text_excerpts():
    assert '' == get_text_excerpts('', 250, 3)

    assert '' == get_text_excerpts('fHello! This is a test sentence1. ', -1, -1)

    assert ' ' == get_text_excerpts(' ', 250, 3)

    assert 'Hello! ' == get_text_excerpts('Hello! ', 250, 3)

    assert 'Hello! This is a test sentence1. ' == \
        get_text_excerpts('Hello! This is a test sentence1. ', 250, 3)

    assert 'Hello! This is a test sentence1. This is a test sentence2. ' == \
        get_text_excerpts(
            'Hello! This is a test sentence1. This is a test sentence2. ', 250, 3)

    text = 'Hello! '
    for i in range(1, 11):
        text += f'This is a test sentence{i}. '

    result = get_text_excerpts(text, 250, 3)
    assert result == \
'''Hello! This is a test sentence1. This is a test sentence2. 
...
This is a test sentence4. This is a test sentence5. This is a test sentence6. 
...
This is a test sentence7. This is a test sentence8. This is a test sentence9. '''

    result = get_text_excerpts(text, 140, 4)
    assert result == \
'''Hello! 
...
This is a test sentence3. 
...
This is a test sentence6. 
...
This is a test sentence8. '''
