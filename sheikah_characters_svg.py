import tkinter.filedialog

'''
#--------------------------------------------------------------------
Sheikah文字SVGの作成用．
フォントの作成を考えて，デフォルトでは1000px x 1000pxのSVGを生成させる．
METAFONTのpenposやpenstrokeに近い考え方で作り始めたが，結局だいぶ変わった．
#--------------------------------------------------------------------

文字は，
    +-------+---+-------+---+-------+---+-------+
    |       |   |       |   |       |   |       |
  6 |       |   |       |   |       |   |       |
    |       |   |       |   |       |   |       |
    +-------+---+-------+---+-------+---+-------+
  5 |       |   |       |   |       |   |       |
    +-------+---+-------+---+-------+---+-------+
    |       |   |       |   |       |   |       |
  4 |       |   |       |   |       |   |       |
    |       |   |       |   |       |   |       |
    +-------+---+-------+---+-------+---+-------+
  3 |       |   |       |   |       |   |       |
    +-------+---+-------+---+-------+---+-------+
    |       |   |       |   |       |   |       |
  2 |       |   |       |   |       |   |       |
    |       |   |       |   |       |   |       |
    +-------+---+-------+---+-------+---+-------+
  1 |       |   |       |   |       |   |       |
    +-------+---+-------+---+-------+---+-------+
    |       |   |       |   |       |   |       |
  0 |       |   |       |   |       |   |       |
    |       |   |       |   |       |   |       |
    +-------+---+-------+---+-------+---+-------+
        0     1     2     3     4     5     6

のようなマス目内で描かれていると考えられる．

    +-------+---+-------+---+-------+---+-------+
    |    ///|   |    ///|///|///////|///|///    |
  6 |  /////|   |  /////|///|///////|///|/////  |
    |///////|   |///////|///|///////|///|///////|
    +-------+---+-------+---+-------+---+-------+
  5 |///////|   |///////|   |       |   |///////|
    +-------+---+-------+---+-------+---+-------+
    |///////|   |///////|   |///////|   |///////|
  4 |///////|   |///////|   |///////|   |///////|
    |///////|   |///////|   |///////|   |///////|
    +-------+---+-------+---+-------+---+-------+
  3 |///////|   |///////|   |       |   |///////|
    +-------+---+-------+---+-------+---+-------+
    |///////|   |///////|///|///////|   |///////|
  2 |///////|   |  /////|///|///////|   |///////|
    |///////|   |    ///|///|///////|   |///////|
    +-------+---+-------+---+-------+---+-------+
  1 |///////|   |       |   |       |   |///////|
    +-------+---+-------+---+-------+---+-------+
    |///////|///|///////|///|///////|///|///////|
  0 |  /////|///|///////|///|///////|///|/////  |
    |    ///|///|///////|///|///////|///|///    |
    +-------+---+-------+---+-------+---+-------+
        0     1     2     3     4     5     6

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
  ・リストpolylines （2個以上のセルを結ぶ線たちのリスト，要素はPolylineクラスのオブジェクト）
  ・リストdots      （単一セルが塗られる点たちのリスト，要素はDotクラスのオブジェクト）
  ・char_name        ("a"とか"b"とか)
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

往路：[.., Pc]     --> [.., Pc, Qa, Qb]  (Qa, Qbを（この順に）末尾に追加)
帰路：[Pb, Pa, ..] --> [Qc, Pb, Pa, ..]  (Qcを先頭に追加)


(ex.2) 頂点Qで左に曲がる（図は，頂点Pは左曲がりのとき）

#    |           |
#    v           ^
#    |           |
# a  |  c     c  |  b
#    P----->-----Q
#       b     a

往路：[.., Pc]     --> [.., Pc, Qc]          (Qcを末尾に追加)
帰路：[Pb, Pa, ..] --> [Qb, Qa, Pb, Pa, ..]  (Qa, Qbを（この順に）先頭に追加)

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

def det(A, B):
    '''
    determinant of 2x2 matrix.
    '''
    return A[0] * B[1] - A[1] * B[0]

def rot_sgn(A, B, C):
    '''
    :param tuple[int] A, B, C: coordinate or cell address
    :rtype: int
    :return: sgn (left --> 1, right --> -1)

    三角形ABCがこの順に右回りか左回りか調べて，符号を返す．
    '''
    if det(A, B) + det(B, C) + det(C, A) > 0:
        return 1
    else:
        return -1

class Char:

    def __init__(self, char_name, polylines, dots, test_print=None):
        '''
        :param str char_name:
        :param list[Polyline] polylines:
        :param list[Dot] dots:
        :param str test_print:

        各文字のデータ．
        Charオブジェクトを追加していくことで文字の登録を行っていく．

        (cf) example --> test_char_data.py
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
    '''
    Polyline と Dot の親クラス．
    セル番地からセルの座標を求めるメソッドしかないが．
    '''

    def coordinate(self, cell_address, wide_size, narrow_size):
        '''
        :param tuple[int] cell_address:
        :param int wide_size:
        :param int narrow_width:
        :rtype: tuple[int]
        :return: (x, y)

        セル番地から，セルの中心の座標を求める．
        y座標は上が正．
        '''
        (i, j) = cell_address
        x = (wide_size * (i+1) + narrow_size * i) / 2
        y = (wide_size * (j+1) + narrow_size * j) / 2
        return (x, y)



class Polyline(GryphElement):

    def __init__(self, cells, start_style, end_style):
        r'''
        :param list[tuple[int]] cells: セル番地のリスト．この順に線を結ぶ．
        :param str start_style: 'stop'|'l-corner'|'r-corner'
        :param str end_style:    same above

        2個以上のセルを結ぶ線．


        #--------------------------#
        #  start styles example    #
        #--------------------------#

        'stop'          'l-corner'       'r-corner'
                            :
        +-----------    +---:-------         +--------
        |                \  :               /
        |   X--->---      \ X--->---       / X--->---
        | start            \              /  :
        +-----------        +--------    +---:-------
                                             :

        #--------------------------#
        #  end styles example      #
        #--------------------------#

        'stop'          'l-corner'      'r-corner'
                              :
        ----------+    -------:---+   -------+
                  |           :  /            \
        --->---X  |    --->---X /     --->---X \
              end |            /             :  \
        ----------+    --------+      -------:---+
                                             :
        '''
        self.cells = cells
        self.start_style = start_style
        self.end_style = end_style

    def generate_path(self, wide_size, narrow_size, line_width,
                      color='black', scale=1, line_join='bevel',
                      stop_style=None, inner_corner_radius=None):
        r'''
        :param int wide_size:
        :param int narrow_size:
        :param int line_width:
        :param str line_join: 'bevel'|'square'|'round'
        :param str stop_style: 'square'|'round' --> stop style start/end shape (like as stroke-linecap in SVG.)
        :param str inner_corner_radius:
        :rtype: str
        :return: '  <path d="M ...."/>'


        #--------------------------#
        #  line_join example:      #
        #--------------------------#

        'bevel(default)'    'square'

        |       |           |       |
        |   |   |           |   |   |
        +   v   +------     |   v   +------
         \  |               |   |
          \ X--->---        |   X--->---
           \                |
            +----------     +--------------

        'round'

         |              |*
         |              |*
         |              |**
         |       |      |****     <-- circled if inner_corner_radius
         |       |      |********
         +       v      +-----------
         *       |
          *      |
           *     X------>------
             *
                 *
                      * +----------


        #--------------------------#
        #  stop_style example:     #
        #--------------------------#

        if stop_style is None:
            line_join: 'bevel' or 'square' --> stop_style: 'square'
            line_join: 'round'             --> stop_style: 'round'

        'square'           'round'

        -------------+     ----------+*
                     |                   *
                     |                    *
           --->---X  |        --->---X    *
                     |                    *
                     |                   *
        -------------+     ----------+*              :

        '''

        forward_path = []  # 往路
        turning_path = []  # 折り返し
        backward_path = [] # 復路

        #-- startの処理 ---------------------------------------------------------------
        (start_i, start_j) = self.cells[0]
        (start_x, start_y) = self.coordinate((start_i, start_j), wide_size, narrow_size)
        (next_i, next_j) = self.cells[1]

        # 'l-corner', 'r-corner'の場合は先頭にダミーを追加する．
        start_dummy = []

        if self.start_style == 'stop':

            # style判定
            if line_join == 'round':
                _stop_style = 'round'
            else:
                _stop_style = 'sqruare'

            # 指定されている場合は優先
            if stop_style:
                _stop_style = stop_style

            # pt_a, pt_b, pt_d の位置を決定
            # ここ'l-corner', 'r-corner'のときとなんか共通の処理にできないものか．
            if start_i < next_i:                                          #   b
                a_x, a_y = start_x - line_width/2, start_y - line_width/2 #     s-->
                b_x, b_y = start_x - line_width/2, start_y + line_width/2 # d=a

            elif start_i > next_i:                                        #      a=d
                a_x, a_y = start_x + line_width/2, start_y + line_width/2 # <--s
                b_x, b_y = start_x + line_width/2, start_y - line_width/2 #      b

            elif start_j < next_j:                                        #    |
                a_x, a_y = start_x + line_width/2, start_y - line_width/2 #    s
                b_x, b_y = start_x - line_width/2, start_y - line_width/2 #  b   a=d

            else: # start_j > next_j                                      #  d=a   b
                a_x, a_y = start_x - line_width/2, start_y + line_width/2 #      s
                b_x, b_y = start_x + line_width/2, start_y + line_width/2 #      |

            pt_a = Point(coordinate=(a_x, a_y), style='start')
            pt_d = Point(coordinate=(a_x, a_y), style='line')
            pt_b = Point(coordinate=(b_x, b_y), style='line')

            if _stop_style == 'round':
                # pt_d.style = 'arc'
                # pt_d.ctrl_pt = (foo, bar)
                # pt_p = Point(hoge)
                # pt_q = Point(hoge)
                # pt_r = Point(hoge)
                pass

            # 往路は末尾に，復路は先頭に追加
            forward_path.append(pt_a)
            backward_path.insert(0, pt_d)

            if _stop_style == 'round':
                # backward_path.insert(0, pt_r)
                # backward_path.insert(0, pt_q)
                # backward_path.insert(0, pt_p)
                pass

            forward_path.append(pt_b)


        elif self.start_style == 'l-corner':
            '''
            先頭にdummyセルを追加して，あとは道中の処理に任せる．
            style='start'の点pt_aを，往路へに追加する処理だけやる．
            (道中の処理で，復路の末尾にpt_aと同じ座標の点が入る）

            この方法だと，スタートだけ他の曲がり角と違う処理にすることは
            できないが，そこまで対応する必要はなさそうか．
            スタートだけ別処理を追加したければ，'l-corner', 'r-corner'以外に
            新たにstyleを定義して分岐を増やせばできる．
            '''
            if start_i < next_i:                                          # a D c
                a_x, a_y = start_x - line_width/2, start_y + line_width/2 #   s-->
                D_i, D_j = start_i, start_j + 1                           #     b

            elif start_i > next_i:                                        #  b
                a_x, a_y = start_x + line_width/2, start_y - line_width/2 # <--s
                D_i, D_j = start_i , start_j - 1                          #  c D a

            elif start_j < next_j:                                        #  c | b
                a_x, a_y = start_x - line_width/2, start_y - line_width/2 #  D s
                D_i, D_j = start_i - 1, start_j                           #  a

            else: # start_j > next_j                                      #      a
                a_x, a_y = start_x + line_width/2, start_y + line_width/2 #    s D
                D_i, D_j = start_i + 1, start_j                           #  b | c

            start_dummy = [(D_i, D_j)]
            pt_a = Point(coordinate=(a_x, a_y), style='start')
            forward_path.append(pt_a)


        elif self.start_style == 'r-corner':
            '''
            dummy追加して道中の処理に任せる．
            往路への，style='start'の点pt_c追加だけやる．
            inner_cornerを'round'で処理する場合も分岐の必要はない．
            （ここのpt_cはinnner-cornerの処理が必要ない）
            '''
            if start_i < next_i:                                          #     b
                c_x, c_y = start_x + line_width/2, start_y - line_width/2 #   s-->
                D_i, D_j = start_i, start_j - 1                           # a D c

            elif start_i > next_i:                                        #  c D a
                c_x, c_y = start_x - line_width/2, start_y + line_width/2 # <--s
                D_i, D_j = start_i , start_j + 1                          #  b

            elif start_j < next_j:                                        #  b | c
                c_x, c_y = start_x + line_width/2, start_y + line_width/2 #    s D
                D_i, D_j = start_i + 1, start_j                           #      a

            else: # start_j > next_j                                      #  a
                c_x, c_y = start_x - line_width/2, start_y - line_width/2 #  D s
                D_i, D_j = start_i - 1, start_j                           #  c | b

            start_dummy = [(D_i, D_j)]
            pt_c = Point(coordinate=(c_x, c_y), style='start')
            forward_path.append(pt_c)

        #-- endの処理 ---------------------------------------------------------------
        '''
        dummy追加があるかもしれないので，ここも先にやる．
        stopの場合はあとでまたやるのでもいいが，ここで処理はやっておいて，
        折り返し点用のリストを作っておく．
        '''
        (end_i, end_j) = self.cells[-1]
        (end_x, end_y) = self.coordinate((end_i, end_j), wide_size, narrow_size)
        (prev_i, prev_j) = self.cells[-2]

        # 'l-corner', 'r-corner'の場合は末尾にダミーを追加する．
        end_dummy = []

        if self.end_style == 'stop':

            # style判定
            if line_join == 'round':
                _stop_style = 'round'
            else:
                _stop_style = 'sqruare'

            # 指定されている場合は優先
            if stop_style:
                _stop_style = stop_style

            # pt_a, pt_b, pt_d の位置を決定
            # ここの座標計算部分は，startと全く同じであることが判明．
            # まとめられるかもしれん．
            if end_i < prev_i:                                        # b
                a_x, a_y = end_x - line_width/2, end_y - line_width/2 #   e--<--
                b_x, b_y = end_x - line_width/2, end_y + line_width/2 # a

            elif end_i > prev_i:                                      #        a
                a_x, a_y = end_x + line_width/2, end_y + line_width/2 # -->--e
                b_x, b_y = end_x + line_width/2, end_y - line_width/2 #        b

            elif end_j < prev_j:                                      #    |
                a_x, a_y = end_x + line_width/2, end_y - line_width/2 #    e
                b_x, b_y = end_x - line_width/2, end_y - line_width/2 #  b   a

            else: # end_j > prev_j                                    #  a   b
                a_x, a_y = end_x - line_width/2, end_y + line_width/2 #    e
                b_x, b_y = end_x + line_width/2, end_y + line_width/2 #    |

            pt_a = Point(coordinate=(a_x, a_y), style='line')
            pt_b = Point(coordinate=(b_x, b_y), style='line')

            if _stop_style == 'round':
                # pt_b.style = 'arc'
                # pt_b.ctrl_pt = (foo, bar)
                # pt_p = Point(hoge)
                # pt_q = Point(hoge)
                # pt_r = Point(hoge)
                pass

            # 折り返しリストに追加
            turning_path.append(pt_a)
            if _stop_style == 'round':
                # turning_path.append(pt_p)
                # turning_path.append(pt_q)
                # turning_path.append(pt_r)
                pass

            turning_path.append(pt_b)

        elif self.end_style == 'l-corner':
            '''
            末尾にdummyセルを追加して，あとは道中の処理に任せる．
            この場合はturning_pathは空のまま．
            '''
            # ここの計算は，startの'r-corner'とほぼ同じ
            if end_i < prev_i:                #     b
                #                             #   e--<--
                D_i, D_j = end_i, end_j - 1   # a D c

            elif end_i > prev_i:              #  c D a
                #                             # <--e
                D_i, D_j = end_i , end_j + 1  #  b

            elif end_j < prev_j:              #  b | c
                #                             #    e D
                D_i, D_j = end_i + 1, end_j   #      a

            else: # end_j > prev_j            #  a
                #                             #  D e
                D_i, D_j = end_i - 1, end_j   #  c | b

            end_dummy = [(D_i, D_j)]


        elif self.end_style == 'r-corner':

            if end_i < prev_i:                # a D c
                #                             #   e-->
                D_i, D_j = end_i, end_j + 1   #     b

            elif end_i > prev_i:              #  b
                #                             # <--e
                D_i, D_j = end_i , end_j - 1  #  c D a

            elif end_j < prev_j:              #  c | b
                #                             #  D e
                D_i, D_j = end_i - 1, end_j   #  a

            else: # end_j > prev_j            #      a
                #                             #    s D
                D_i, D_j = end_i + 1, end_j   #  b | c

            end_dummy = [(D_i, D_j)]
            # なんか，よく考えると根本的な処理はやってるんだよなすでに．
            # 道中の処理に任せないでここでやっちゃう方がよかったかもしれない．
            # あと，道中の処理で同じような処理が行われるので，やはり関数に
            # まとめた方がいい．


        #-- 道中の処理 ---------------------------------------------------------------

        corner_cells = start_dummy + self.cells + end_dummy
        prev_cell = corner_cells[0]
        cell = corner_cells[1]
        for next_cell in corner_cells[2:]:
            (i, j) = cell
            (x, y) = self.coordinate(cell, wide_size, narrow_size)
            (prev_i, prev_j) = prev_cell
            if rot_sgn(prev_cell, cell, next_cell) > 0:# 左まわり
                if i < prev_i:                                    #     a
                    a_x, a_y = x + line_width/2, y + line_width/2 #   +--<--+
                    b_x, b_y = x - line_width/2, y - line_width/2 # b | c
                    c_x, c_y = x + line_width/2, y - line_width/2 #   v

                elif i > prev_i:                                  #         ^
                    a_x, a_y = x - line_width/2, y - line_width/2 #       c | b
                    b_x, b_y = x + line_width/2, y + line_width/2 #   +-->--+
                    c_x, c_y = x - line_width/2, y + line_width/2 #       a

                elif j < prev_j:                                  #   +
                    a_x, a_y = x - line_width/2, y + line_width/2 # a | c
                    b_x, b_y = x + line_width/2, y - line_width/2 #   +-->--
                    c_x, c_y = x + line_width/2, y + line_width/2 #     b

                else: # j > prev_j                                #    b
                    a_x, a_y = x + line_width/2, y - line_width/2 # --<--+
                    b_x, b_y = x - line_width/2, y + line_width/2 #    c | a
                    c_x, c_y = x - line_width/2, y - line_width/2 #      +

                pt_a = Point(coordinate=(a_x, a_y), style='line')
                pt_b = Point(coordinate=(b_x, b_y), style='line')
                pt_c = Point(coordinate=(c_x, c_y), style='line')

                backward_path.insert(0, pt_a)

                if line_join == 'round':
                    # pt_b.style = 'arc'
                    # pt_b.ctrl_pt = (foo, bar)
                    # pt_ab = Point(hoge)
                    # backward_path.insert(0, pt_ab)
                    pass

                backward_path.insert(0, pt_b)

                if inner_corner_radius:
                    # pt_p = Point(hoge)
                    # pt_q = Point(hoge)
                    # pt_r = Point(hoge)
                    # forward_path.append(pt_p)
                    # forward_path.append(pt_q)
                    # forward_path.append(pt_r)
                    pass
                else:
                    forward_path.append(pt_c)

            else: # 右まわり
                if i < prev_i:                                    #   ^
                    a_x, a_y = x + line_width/2, y - line_width/2 # b | c
                    b_x, b_y = x - line_width/2, y + line_width/2 #   +--<--+
                    c_x, c_y = x + line_width/2, y + line_width/2 #     a

                elif i > prev_i:                                  #     a
                    a_x, a_y = x - line_width/2, y + line_width/2 # +-->--+
                    b_x, b_y = x + line_width/2, y - line_width/2 #     c | b
                    c_x, c_y = x - line_width/2, y - line_width/2 #       v

                elif j < prev_j:                                  #      +
                    a_x, a_y = x + line_width/2, y + line_width/2 #    c | a
                    b_x, b_y = x - line_width/2, y - line_width/2 # --<--+
                    c_x, c_y = x - line_width/2, y + line_width/2 #    b

                else: # j > prev_j                                #     b
                    a_x, a_y = x - line_width/2, y - line_width/2 #   +-->--
                    b_x, b_y = x + line_width/2, y + line_width/2 # a | c
                    c_x, c_y = x + line_width/2, y - line_width/2 #   +

                pt_a = Point(coordinate=(a_x, a_y), style='line')
                pt_b = Point(coordinate=(b_x, b_y), style='line')
                pt_c = Point(coordinate=(c_x, c_y), style='line')

                forward_path.append(pt_a)

                if line_join == 'round':
                    # pt_b.style = 'arc'
                    # pt_b.ctrl_pt = (foo, bar)
                    # pt_ab = Point(hoge)
                    # forward_path.append(pt_ab)
                    pass

                forward_path.append(pt_b)


                if inner_corner_radius:
                    # pt_p = Point(hoge)
                    # pt_q = Point(hoge)
                    # pt_r = Point(hoge)
                    # backward_path.insert(0, pt_p)
                    # backward_path.insert(0, pt_q)
                    # backward_path.insert(0, pt_r)
                    pass
                else:
                    backward_path.insert(0, pt_c)

            prev_cell = cell
            cell = next_cell


        path = SvgPath(color, scale)
        for point in forward_path:
            path.append(point)
        for point in turning_path:
            path.append(point)
        for point in backward_path:
            path.append(point)

        return path



class Dot(GryphElement):

    def __init__(self, i, j):
        '''
        :param int i,j: cell address (i, j)
        y座標は上が正．

        単一セルのみからなる塗りつぶし点．
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

        セル座標ではない実際の座標（y座標は上が正）と，
        その点までを直線で結ぶか円弧で結ぶかのstyleを指定．
        円弧の場合はベジェで結ぶので，制御点の座標をctrl_ptに入れる．
        '''
        self.x = coordinate[0]
        self.y = coordinate[1]
        self.style = style
        self.ctrl_pt = ctrl_pt


class SvgPath:

    def __init__(self, color, scale=1):
        '''
        :param str color: 'black' or 'red' or 'blue' or 'cyan' or etc...
        :param int scale:

        色（fill属性）だけ指定．stroke="none"は固定．
        append(Point)で点を追加していくとSVGのpath要素が文字列で作られる．
        '''
        self.path_header = '  <path stroke="none" fill="{color}" d="'.format(color=color)
        self.path_body = ''
        self.path_footer = '\n    Z\n  "/>'
        self.scale = scale

    def append(self, point):
        '''
        :param Point point:

        Pointクラスのオブジェクトを受け取って，その座標とstyleを参照して
        path要素のd属性の末尾にコマンドと座標を追加していく．

        この埋め込みの際に，y座標の符号反転とscale倍が処理される．
        '''

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
        '''
          output SVG path strings like below:

        '  <path stroke="none" fill="{color}" d="
             M x0 y0
             L x1 y1
               :
             Z
           "/>'

        '''
        return self.path_header + self.path_body + self.path_footer


# ---------------------------------------------------------------------

if __name__ == '__main__':
    import sheikah_characters_svg_test as test
    wide_size = 180
    narrow_size = 45
    test.generate_characters(wide_size, narrow_size, test=True)

    print('finish test')
