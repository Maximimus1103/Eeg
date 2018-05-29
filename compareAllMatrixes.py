import random
import tkFont
from Tkconstants import RIDGE, DISABLED

import nmsimilarity as nm


class OvalTags:
    active = None

    def __init__(self, text1, text2, oval, line1, line2):
        """initialize oval(node)"""

        self.text1 = text1
        self.oval = oval
        self.line1 = line1
        self.text2 = text2
        self.line2 = line2




def un_click(init, oval, discolor):
    """if you did not click on node"""

    init.canvas.itemconfig(oval.oval, fill=discolor)
    init.show_comparison.configure(state="disabled")
    OvalTags.active = None
   


def select_oval(init, oval, color):
    """oval selected"""

    init.canvas.itemconfig(oval.oval, fill=color)
    init.show_comparison.configure(state="normal")
    OvalTags.active = oval
    


def click_on_node(index, init, act_color, discolor):
    """what happening if you clikc on node"""

    my_oval = init.ovals_list[index]

    if OvalTags.active == my_oval:  # is_active(init.canvas, oval, act_color):
        un_click(init, my_oval, discolor)
    else:
        for tag in init.ovals_list:
            if OvalTags.active == tag:  # is_active(init.canvas, tag.oval, act_color):
                un_click(init, tag, discolor)
                break
        select_oval(init, my_oval, act_color)


def canvas_draw_auto_compare(init):
    """draing 'Auto Compare'"""
    init.canvas.configure(borderwidth="2", background="#86A390", relief=RIDGE)
    init.matrix_right_info = init.vector
    init.matrix_left_info = init.vector
    num_of_matrices = len(init.matrices)
    font = tkFont.Font(family='Helvetica', size=10, weight='bold')
    r = 7
    discolor = "white"
    act_color = "blue"
    draw_pad_left = 40
    draw_pad_right = 20
    draw_pad_top = 20
    draw_pad_bottom = 30
    pips = 10
    x_len = init.c_width - (draw_pad_left + draw_pad_right)
    y_len = init.c_height - (draw_pad_top + draw_pad_bottom)
    step_on_x = x_len / num_of_matrices - 1
    text_x = []
    for i in range(num_of_matrices - 1):
        text_x.append(draw_pad_left + step_on_x * (i + 1))
    
    comparison = []
    text = []
    for i in range(num_of_matrices - 1):
        text.append("{}-{}".format(i + 1, i + 2))
        comparison.append(
            nm.NmSimilarity(nm.nmGraph(init.matrices[i]), nm.nmGraph(init.matrices[i + 1]), 0.5).final_graph_similarity)

    comparison_y = []
    output_start = draw_pad_top + pips
    output_end = init.c_height - draw_pad_bottom
    slope = (output_end - output_start)  # output = 35 + slope * (input - maximal_similarity)
    for i in range(num_of_matrices - 1):
        comparison_y.append(round(output_end - slope * 0.01 * comparison[i], 3))
   
    init.canvas.create_line(draw_pad_left, init.c_height - draw_pad_bottom, draw_pad_left + x_len,
                            init.c_height - draw_pad_bottom,
                            width=3, fill="black")  # 0X axe horizontal
    init.canvas.create_line(draw_pad_left, draw_pad_top, draw_pad_left, init.c_height - draw_pad_bottom,
                            width=3, fill="black")  # 0Y axe vertical

    init.ovals_list = []
    for i in range(num_of_matrices - 1):

        text1 = init.canvas.create_text(text_x[i], draw_pad_top + pips + y_len, text=text[i], fill="black")
        oval = init.canvas.create_oval(text_x[i] - r, comparison_y[i] - r, text_x[i] + r, comparison_y[i] + r,
                                       fill=discolor, width=1)
        line1 = init.canvas.create_line(draw_pad_left, comparison_y[i], draw_pad_left + x_len, comparison_y[i], width=1,
                                        fill="gray80")
        text2 = init.canvas.create_text(text_x[i] + 4 * r, comparison_y[i] - 2 * r, text="{}%".format(comparison[i]),
                                        font=font, fill="yellow")
        if i != num_of_matrices - 2:  # last matrix had no "next"
            line2 = init.canvas.create_line(text_x[i], comparison_y[i], text_x[i + 1], comparison_y[i + 1], width=1,
                                            fill="blue3")
        else:
            line2 = None
        init.ovals_list.append(OvalTags(text1, text2, oval, line1, line2))
    for i in range(num_of_matrices - 2):
        # if ovals_tags[i].line2 is not None:  # last matrix had no "next"
        init.canvas.tag_lower(init.ovals_list[i].line2)  # line (3-4)
    step_on_y_scale = 1. / 10
    
    step_on_y_place = (output_end - output_start) / 10.
    y_scale_text = []  # what to write
    y_scale_place = []  # where to write
    for i in range(11):
        y_scale_text.append(round(i * step_on_y_scale, 3))
        y_scale_place.append(output_end - i * step_on_y_place)
        init.canvas.create_text(pips * 2, y_scale_place[i], text=y_scale_text[i], fill="black")
        
        lines = init.canvas.create_line(draw_pad_left, y_scale_place[i], draw_pad_left + x_len, y_scale_place[i],
                                        width=2, fill="gray30")  # gray50
        init.canvas.tag_lower(lines)

    for i in range(num_of_matrices - 1):
        init.canvas.tag_raise(init.ovals_list[i].text1)  # text[i] (3-4)
        init.canvas.tag_lower(init.ovals_list[i].line1)  # line (gray80)
        init.canvas.tag_raise(init.ovals_list[i].text2)  # text ({}%)

        init.canvas.tag_raise(init.ovals_list[i].oval)  # oval
        init.canvas.tag_bind(init.ovals_list[i].oval, "<Button-1>",
                             lambda event, index=i, init=init: click_on_node(index, init, act_color, discolor))
