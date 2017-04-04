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
Pa.style = 'line', Pb.style = 'outer-corner', Pc.style = 'inner-corner'とかにしておけばいいか．

Pointクラス
  ・coordinate （実座標，y座標は上が正）
  ・style

Pa.style='corner'の場合に円を描きたい場合のために，Pcの座標も持たせた方が良いのだろうか．

#-----------------------------------------------------------------------------


端点の処理
start_style='stop'
#
#  b
#    P--->---
#  a
#
#  forward_path.append(Pa)
#  backward_path.insert(0, Pb)
#
#  Pa.style = 'stop'
#  Pb.style = 'line'
#
#  とかか．

start_style='l-corner'
#
#  a    c
#    P----->---
#       b
# ここの処理は曲がり角と同じだが，innner-cornerは処理しないので，Pc.style='line'にするべきという点だけ違う．
'''

class Char:

    def __init__(self, char_name, polylines, dots):
        '''
        :param str char_name:
        :param list[tuple[int]] polylines:
        :param list[tuple[int]] dots:

        polylines, dotsに格納する座標は，cell address.
        y座標は上が正．
        '''
        self.char_name = char_name
        self._polylines = polylines
        self._dots = dots

    def generate_svg(self, wide_size, narrow_size, line_width,
                     size=1000, color='black', scale=1, grid_display=False):
        '''
        :param int wide_size:
        :param int narrow_size:
        :param int line_width:
        :rtype: str
        :return: SVG source of this character.
        '''
        pass

    def save_svg(self, wide_size, narrow_size, line_width,
                 size=1000, color='black', scale=1, grid_display=False):
        '''
        テスト時のマニュアルセーブ用
        '''
        svg = self.generate_svg(wide_size, narrow_size, line_width,
                 size, color, scale, grid_display)
        fname = tkinter.filedialog.asksaveasfilename(
                    filetypes =[('svg files', '*.svg')])
        if fname:
            f = open(fname, 'w')
            f.write(svg)
            f.close()


class Polyline:

    def __init__(self, points, start_style, end_style):
        self.points = points
        self.start_style = start_style
        self.end_style = end_style

    def generate_path(self, wide_size, narrow_size, line_width,
                      line_join='bevel', stop_style=None,
                      inner_corner_radius=None):
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

        pass


class Point:

    def __init__(self, coordinate, style):
        self.coordinate = coordinate
        self.style = style



# ---------------------------------------------------------------------

if __name__ == '__main__':

    wide_size = 180
    narrow_size = 45
    line_width_a = wide_size # alphabet
    line_width_d = narrow_size # digit

    alphabet_characters = []
    digit_characters = []

    for c in alphabet_characters:
        svg = c.generate_svg(wide_size, narrow_size, line_width_a)
        f = open('test_{0}_{1}_{2}.svg'.format(
                    c.char_name, wide_size, narrow_size),
                'w')
        f.write(svg)
        f.close()

        svg = c.generate_svg(wide_size, narrow_size, line_width_a,
                             color='cyan', grid_display=True)
        f = open('test_{0}_{1}_{2}.svg'.format(
                    c.char_name, wide_size, narrow_size),
                'w')
        f.write(svg)
        f.close()

    for c in digit_characters:
        svg = c.generate_svg(wide_size, narrow_size, line_width_d)
        f = open('test_{0}_{1}_{2}.svg'.format(
                    c.char_name, wide_size, narrow_size),
                'w')
        f.write(svg)
        f.close()

        svg = c.generate_svg(wide_size, narrow_size, line_width_d,
                             color='cyan', grid_display=True)
        f = open('test_{0}_{1}_{2}.svg'.format(
                    c.char_name, wide_size, narrow_size),
                'w')
        f.write(svg)
        f.close()
