import test_char_data as alphabet_char_data
import os

class Html:

    def __init__(self, title):
        self.header  = '<!DOCTYPE html>\n'
        self.header += '<html lang="ja">\n'
        self.header += '  <head>\n'
        self.header += '    <meta charset="UTF-8">\n'
        self.header += '    <title>{}</title>\n'.format(title)
        self.header += '  </head>\n'
        self.header += '  <body>\n'

        self.body = ''

        self.footer  = '\n'
        self.footer += '  </body>\n'
        self.footer += '</html>'

    def appendsvg(self, fname, width=200):
        self.body += '\n  <img src="{}" width="{}">'.format(fname, width)

    def appendbreak(self):
        self.body += '\n  <br>'

    def output_html(self):
        return self.header + self.body + self.footer

def generate_characters(wide_size, narrow_size,
                        alphabet_line_width=None, digit_line_width=None,
                        test=False):

    if alphabet_line_width:
        line_width_a = alphabet_line_width
    else:
        line_width_a = wide_size # alphabet

    if digit_line_width:
        line_width_d = digit_line_width
    else:
        line_width_d = narrow_size # alphabet
    if test:
        save_dir = "test_output/w{}_n{}".format(wide_size, narrow_size)
    else:
        save_dir = "output/w{}_n{}".format(wide_size, narrow_size)

    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)

    html = Html('Sheikah characters (wide:{}, narrow:{})'.format(wide_size, narrow_size))
    file_names = []
    grid_file_names = []

    alphabet_characters = alphabet_char_data.characters
    digit_characters = []

    for c in alphabet_characters:
        svg_output = c.generate_svg(wide_size, narrow_size, line_width_a)
        fname = '{}.svg'.format(c.char_name)
        f = open(save_dir + '/' + fname, 'w')
        f.write(svg_output)
        f.close()
        file_names += [fname]
        print('write --> {}'.format(fname))

        svg_output = c.generate_svg(wide_size, narrow_size, line_width_a,
                             color='cyan', grid_display=True)
        fname = '{}_grid.svg'.format(c.char_name)
        f = open(save_dir + '/' + fname, 'w')
        f.write(svg_output)
        f.close()
        grid_file_names += [fname]
        print('write --> {}'.format(fname))
        if c.test_print:
            print(c.test_print)

    for c in digit_characters:
        svg_output = c.generate_svg(wide_size, narrow_size, line_width_d)
        fname = '{}.svg'.format(c.char_name)
        f = open(save_dir + '/' + fname, 'w')
        f.write(svg_output)
        f.close()
        file_names += [fname]
        print('write --> {}'.format(fname))

        svg_output = c.generate_svg(wide_size, narrow_size, line_width_d,
                             color='cyan', grid_display=True)
        fname = '{}_grid.svg'.format(c.char_name)
        f = open(save_dir + '/' + fname, 'w')
        f.write(svg_output)
        f.close()
        grid_file_names += [fname]
        print('write --> {}'.format(fname))
        if c.test_print:
            print(c.test_print)


    for fname in file_names:
        html.appendsvg(fname)
    html.appendbreak()
    for fname in grid_file_names:
        html.appendsvg(fname, 300)

    f = open(save_dir + '/index.html', 'w')
    f.write(html.output_html())
    f.close()
    print('write --> {}'.format(save_dir + '/index.html'))


if __name__ == '__main__':
    wide_size = 180
    narrow_size = 45
    generate_characters(wide_size, narrow_size, test=True)
