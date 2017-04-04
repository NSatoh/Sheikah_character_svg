import tkinter.filedialog

'''
#--------------------------------------------------------------------
Sheikah文字SVGの作成用．
フォントの作成を考えて，デフォルトでは1000px x 1000pxのSVGを生成させる．
METAFONTのpenposやpenstrokeに近い考え方で作り始めたが，結局だいぶ変わった．
#--------------------------------------------------------------------

文字は，
        0     1     2     3     4     5     6
    +-------+---+-------+---+-------+---+-------+
    |       |   |       |   |       |   |       |
  0 |       |   |       |   |       |   |       |
    |       |   |       |   |       |   |       |
    +-------+---+-------+---+-------+---+-------+
  1 |       |   |       |   |       |   |       |
    +-------+---+-------+---+-------+---+-------+
    |       |   |       |   |       |   |       |
  2 |       |   |       |   |       |   |       |
    |       |   |       |   |       |   |       |
    +-------+---+-------+---+-------+---+-------+
  3 |       |   |       |   |       |   |       |
    +-------+---+-------+---+-------+---+-------+
    |       |   |       |   |       |   |       |
  4 |       |   |       |   |       |   |       |
    |       |   |       |   |       |   |       |
    +-------+---+-------+---+-------+---+-------+
  5 |       |   |       |   |       |   |       |
    +-------+---+-------+---+-------+---+-------+
    |       |   |       |   |       |   |       |
  6 |       |   |       |   |       |   |       |
    |       |   |       |   |       |   |       |
    +-------+---+-------+---+-------+---+-------+

のようなマス目内で描かれていると考えられる．

        0     1     2     3     4     5     6
    +-------+---+-------+---+-------+---+-------+
    |    ///|   |    ///|///|///////|///|///    |
  0 |  /////|   |  /////|///|///////|///|/////  |
    |///////|   |///////|///|///////|///|///////|
    +-------+---+-------+---+-------+---+-------+
  1 |///////|   |///////|   |       |   |///////|
    +-------+---+-------+---+-------+---+-------+
    |///////|   |///////|   |///////|   |///////|
  2 |///////|   |///////|   |///////|   |///////|
    |///////|   |///////|   |///////|   |///////|
    +-------+---+-------+---+-------+---+-------+
  3 |///////|   |///////|   |       |   |///////|
    +-------+---+-------+---+-------+---+-------+
    |///////|   |///////|///|///////|   |///////|
  4 |///////|   |  /////|///|///////|   |///////|
    |///////|   |    ///|///|///////|   |///////|
    +-------+---+-------+---+-------+---+-------+
  5 |///////|   |       |   |       |   |///////|
    +-------+---+-------+---+-------+---+-------+
    |///////|///|///////|///|///////|///|///////|
  6 |  /////|///|///////|///|///////|///|/////  |
    |    ///|///|///////|///|///////|///|///    |
    +-------+---+-------+---+-------+---+-------+

例えば「a」はこれ．お？なんかイイのではこれ．

曲がり角は基本的に面取りされているようだが，
ぶっといlineを作ってline-join="bevel"で実現しようとすると
面取りが浅い．調整できないようなので，直接polygonで実現することにした．

数字0～9が，どうやら細い方のマスに線が引かれる文字のようなので，
最初上のマスの幅2種類をwide-size, narrow-sizeと呼ぶことにし，
line-widthとは区別する．
# alphabet --> line-width = wide-size
# digit    --> line-width = narrow-size

#--------------------------------------------------------------------

Charクラス：
  ・リストpolylines
  ・リストdots
  ・char_name ("a"とか"b"とか)
  ・SVGソースを生成するメソッド．y座標はここで反転させる．


Polylineクラス：
  ・リスト points（端点のセル番地たちを順番に格納する．y座標は上が正）
  ・start_style, end_style
        stroke-linecapのような感じで．'square', 'l-corner', 'r-corner'の3つでよいか．
        'round'にも対応できるといいが，その場合はpolygon要素ではなくpath要素で実装が必要か．
        --> line_join='round'でgenerate_svgが呼ばれたときに，自動でlinecapもround系にしたい．
            なので，'square'はやめて，'stop'としよう．
  ・SVGを生成するメソッド
        wide-size, narrow-size, line-width, line-join属性, stop_style=None, inner_corner_radius=None
        を与えると，SVGソースを生成するようにしたい．
        line-joinはデフォルトは'bevel'で，頂点を通るように45度で面取りする．
        面取りしない'square'にも対応するか．これも'round'に対応させるならpathか．
        stop_styleは，'square'か'round'を想定している．指定されていればそれを優先して使う．
        指定されていない(Noneのままの）場合は，line-joinで分岐して，square, bevelなら'square',
        roundなら'round'

        forward_pathとbackward_pathを中間生成してからSVGを作る．

#--------------------------------------------------------------------

各頂点でのpathの更新規則：
右回りに囲んでいくようにpathをとる．
（数学的には左回りにするべきなんだろうか．文字を書くとき普通右回りなためこうした）

(ex.1) 頂点Qで右に曲がる（図は，頂点Pは左曲がりのとき）

#    |
#    v
#    |
# a  |  c     a
#    P----->-----Q
#       b     c  |  b
#                v
#                |

往路：[.., Pc]         --> [.., Pc, Qa, Qb]  (Qa, Qbを（この順に）末尾に追加)
帰路：[Pb, Pa, ..]     --> [Qc, Pb, Pa, ..]  (Qcを先頭に追加)


(ex.2) 頂点Qで左に曲がる（図は，頂点Pは左曲がりのとき）

#    |           |
#    v           ^
#    |           |
# a  |  c     c  |  b
#    P----->-----Q
#       b     a

往路：[.., Pa, Pb]     --> [.., Pa, Pb, Qc]  (Qcを末尾に追加)
帰路：[Pc, ..]         --> [Qb, Qa, Pc, ..]  (Qa, Qbを（この順に）先頭に追加)

各点Pa, Pb, Pcは，Pointクラスのオブジェクトとして，
Pa.style = 'line', Pb.style = 'line' or 'corner',
Pc.style = 'line'にする．

line_join=='round'の場合は，PaからPbへ行く中継点Pabも作る．一気に90度だとベジェの精度は
やや悪いようなので．また，制御点の座標も計算して，Pab.ctrl_pt, Pb.ctrl_ptに入れておく．
inner_corner_radiusが指定されているときは，さらにPc側にもPp, Pqとかを追加する．

Pointクラス
  ・coordinate （実座標，y座標は上が正）
  ・style

#-----------------------------------------------------------------------------


端点の処理
start_style='stop'
#
#  b
#    P--->---
#  a=d
#
#  forward_path.append(Pa)
#  backward_path.insert(0, Pb)
#
#  Pa.style = 'start'
#  Pb.style = 'line'
#  Pd.style = 'line'
#  とかか．処理を簡単にするために，スタート地点については，第4の点dをaと同じ座標でとる．

start_style='l-corner'
#
#  a   (c)
#    P----->---
#       b
# ここの処理は曲がり角と同じ．
# Pc付け加えるの無駄な予感がするのだが，処理の分岐を減らす意味で常にPc.style='line'で
# 入れておくべきか．
'''

SVG_HEADER = r'''<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{size}px" height="{size}px" viewBox="{x_min} {y_min} {size} {size}">

'''


class Char:

    def __init__(self, char_name, polylines, dots, test_print=None):
        '''
        :param str char_name:
        :param list[tuple[int]] polylines:
        :param list[tuple[int]] dots:

        polylines, dotsに格納する座標は，cell address.
        y座標は上が正．
        '''
        self.char_name = char_name
        self.polylines = polylines
        self.dots = dots
        self.test_print=test_print

    def generate_svg(self, wide_size, narrow_size, line_width,
                     size=1000, color='black', scale=1, grid_display=False,
                     line_join='bevel', stop_style=None, inner_corner_radius=None,
                     dot_style=None):
        '''
        :param int wide_size:
        :param int narrow_size:
        :param int line_width:
        :rtype: str
        :return: SVG source of this character.
        '''
        margin_width = (size - wide_size * 4 - narrow_size * 3)/2
        grid_margin = 0
        if grid_display:
            grid_margin = 200
        viewbox_size = size + grid_margin * 2

        x_min = -grid_margin - margin_width
        y_min = -grid_margin - margin_width - 4 * wide_size - 3 * narrow_size

        svg_header = SVG_HEADER.format(size=viewbox_size * scale,
                                       x_min=x_min * scale,
                                       y_min=y_min * scale)
        svg_body = ''
        svg_footer = '\n</svg>'

        for polyline in self.polylines:
            path = polyline.generate_path(
                      wide_size, narrow_size, line_width,
                      color, scale,
                      line_join, stop_style, inner_corner_radius)

            svg_body += '\n' + path.output_svg()

        if line_join == 'round':
            style = 'round'
        else:
            style = 'square'
        if dot_style:
            # 指定があればそれを優先して，ここで強制上書き．
            style = dot_style

        for dot in self.dots:
            path = dot.generate_path(
                      wide_size, narrow_size, line_width,
                      color, scale, style)
            svg_body += '\n' + path.output_svg()


        if grid_display:
            ws = wide_size
            ns = narrow_size

            for i in range(8):
                svg_body += '\n  <line x1="0" y1="{y}" x2="{x}" y2="{y}"'.format(
                                    x=4*ws+3*ns, y=-((i+1)//2)*ws - (i//2)*ns)
                svg_body += '\n     stroke="red" stroke-width="1" stroke-dasharray="20,5"/>'

            for i in range(8):
                svg_body += '\n  <line x1="{x}" y1="0" x2="{x}" y2="{y}"'.format(
                                    y=-(4*ws+3*ns), x=((i+1)//2)*ws + (i//2)*ns)
                svg_body += '\n     stroke="red" stroke-width="1" stroke-dasharray="20,5"/>'

            svg_body += '\n  <line x1="0" y1="0" x2="0" y2="{y}"'.format(y=grid_margin)
            svg_body += '\n     stroke="red" stroke-width="1"/>'

            svg_body += '\n  <line x1="{x}" y1="0" x2="{x}" y2="{y}"'.format(x=ws,y=grid_margin)
            svg_body += '\n     stroke="red" stroke-width="1"/>'

            svg_body += '\n  <line x1="{x}" y1="0" x2="{x}" y2="{y}"'.format(x=ws+ns,y=grid_margin)
            svg_body += '\n     stroke="red" stroke-width="1"/>'

            svg_body += '\n  <text x="{x}" y="{y}" fill="black" text-anchor="middle" font-size="{fs}">'.format(
                x=ws/2, y=grid_margin * 7/16, fs=grid_margin//8)
            svg_body += '\n     {ws}</text>'.format(ws=ws)

            svg_body += '\n  <text x="{x}" y="{y}" fill="black" text-anchor="middle" font-size="{fs}">'.format(
                x=ws+ns/2, y=grid_margin * 7/16, fs=grid_margin//8)
            svg_body += '\n     {ns}</text>'.format(ns=ns)

        return svg_header + svg_body + svg_footer


    def save_svg(self, wide_size, narrow_size, line_width,
                     size=1000, color='black', scale=1, grid_display=False,
                     line_join='bevel', stop_style=None, inner_corner_radius=None,
                     dot_style=None):

        '''
        テスト時のマニュアルセーブ用
        '''
        svg_output = self.generate_svg(wide_size, narrow_size, line_width,
                 size, color, scale, grid_display, line_join, stop_style,
                 inner_corner_radius, dot_style)
        fname = tkinter.filedialog.asksaveasfilename(
                    filetypes =[('svg files', '*.svg')])
        if fname:
            f = open(fname, 'w')
            f.write(svg_output)
            f.close()


class GryphElement:

    def coordinate(self, cell_address, wide_size, narrow_size):
        '''
        セル番地から，セルの中心の座標を求める．
        y座標は上が正．
        '''
        (i, j) = cell_address
        x = (wide_size * (i+1) + narrow_size * i) / 2
        y = (wide_size * (j+1) + narrow_size * j) / 2
        return (x, y)



class Polyline(GryphElement):

    def __init__(self, points, start_style, end_style):
        self.points = points
        self.start_style = start_style
        self.end_style = end_style

    def generate_path(self, wide_size, narrow_size, line_width,
                      color='black', scale=1, line_join='bevel',
                      stop_style=None, inner_corner_radius=None):
        '''
        :param int wide_size:
        :param int narrow_size:
        :param int line_width:
        :param str line_join:
        :param str stop_style:
        :param str inner_corner_radius:
        :rtype: str
        :return: '<path d="M ...."/>'
        '''

        forward_path = []
        backward_path = []
        # ここで色々処理

        path = SvgPath(color, scale)
        for point in forward_path:
            path.append(point)
        for point in backward_path:
            path.append(point)

        return path



class Dot(GryphElement):

    def __init__(self, i, j):
        '''
        (i, j): cell address
        y座標は上が正．
        '''
        self.cell_address = (i, j)

    def generate_path(self, wide_size, narrow_size, line_width,
                      color='black', scale=1, style='square'):
        '''
        :param int wide_size:
        :param int narrow_size:
        :param int line_width:
        :param str style: 'square' or 'round'
        :rtype: str
        :return: '<path d="M ...."/>'
        '''

        (center_x, center_y) = self.coordinate(self.cell_address,
                                               wide_size, narrow_size)
        forward_path = []

        if style == 'square':
            lw = line_width
            forward_path += [Point(
                                 coordinate=(center_x - lw/2, center_y - lw/2),
                                 style='start'
                            )]
            forward_path += [Point(
                                    coordinate=(center_x + lw/2, center_y - lw/2),
                                    style='line'
                            )]
            forward_path += [Point(
                                    coordinate=(center_x + lw/2, center_y + lw/2),
                                    style='line'
                            )]
            forward_path += [Point(
                                    coordinate=(center_x - lw/2, center_y + lw/2),
                                    style='line'
                            )]

        path = SvgPath(color, scale)
        for point in forward_path:
            path.append(point)

        return path


class Point:

    def __init__(self, coordinate, style, ctrl_pt=None):
        '''
        :param tuple[int] coordinate:
        :param str style: 'start' or 'line' or 'arc'
        :param tuple[int] ctrl_pt:
        '''
        self.x = coordinate[0]
        self.y = coordinate[1]
        self.style = style
        self.ctrl_pt = ctrl_pt


class SvgPath:

    def __init__(self, color, scale):
        self.path_header = '  <path stroke="none" fill="{color}" d="'.format(color=color)
        self.path_body = ''
        self.path_footer = '\n    Z\n  "/>'
        self.scale = scale

    def append(self, point):

        if point.style == 'start':
            self.path_body += '\n    M'
        elif point.style == 'line':
            self.path_body += '\n    L' # HやVも使った方がいいんだろうか．
        elif point.style == 'arc':
            self.path_body += '\n    Q {x} {y}'.format(
                                   x=point.ctrl_pt[0] * self.scale,
                                   y=-point.ctrl_pt[1] * self.scale)

        self.path_body += ' {x} {y}'.format(x=point.x * self.scale, y=-point.y * self.scale)


    def output_svg(self):
        return self.path_header + self.path_body + self.path_footer


# ---------------------------------------------------------------------

if __name__ == '__main__':

    import test_char_data
    alphabet_characters = test_char_data.characters
    digit_characters = []

    wide_size = 180
    narrow_size = 45
    line_width_a = wide_size # alphabet
    line_width_d = narrow_size # digit

    for c in alphabet_characters:
        svg_output = c.generate_svg(wide_size, narrow_size, line_width_a)
        fname = 'test_{0}_{1}_{2}.svg'.format(c.char_name, wide_size, narrow_size)
        f = open(fname, 'w')
        f.write(svg_output)
        f.close()
        print('write --> {}'.format(fname))
        if c.test_print:
            print(c.test_print)

        svg_output = c.generate_svg(wide_size, narrow_size, line_width_a,
                             color='cyan', grid_display=True)
        fname = 'test_{0}_{1}_{2}_grid.svg'.format(c.char_name, wide_size, narrow_size)
        f = open(fname, 'w')
        f.write(svg_output)
        f.close()
        print('write --> {}'.format(fname))
        if c.test_print:
            print(c.test_print)

    for c in digit_characters:
        svg_output = c.generate_svg(wide_size, narrow_size, line_width_d)
        fname = 'test_{0}_{1}_{2}.svg'.format(c.char_name, wide_size, narrow_size)
        f = open(fname, 'w')
        f.write(svg_output)
        f.close()
        print('write --> {}'.format(fname))
        if c.test_print:
            print(c.test_print)

        svg_output = c.generate_svg(wide_size, narrow_size, line_width_d,
                             color='cyan', grid_display=True)
        fname = 'test_{0}_{1}_{2}_grid.svg'.format(c.char_name, wide_size, narrow_size)
        f = open(fname, 'w')
        f.write(svg_output)
        f.close()
        print('write --> {}'.format(fname))
        if c.test_print:
            print(c.test_print)

    print('finish test')


