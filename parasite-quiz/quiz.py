import tkinter as tk
import tkinter.font
import tkinter.filedialog
from tkinter import ttk
import pandas as pd
import random


class QuizGenerator:
    def __init__(self, parasites):
        self.parasites = parasites
        self.categories = None
        self.only_jb = False

        self.qa = None
        self.indices = None
        self.cur_questions = None
        self.cur_answers = None

        self.cur_number = 0
        self.cur_input = None
        self.re = False

    def reset(self):

        self.categories = None
        self.only_jb = False

        self.qa = None
        self.indices = None
        self.cur_questions = None
        self.cur_answers = None

        self.cur_number = 0
        self.cur_input = None
        self.re = False

    def set_categories(self, categories):
        self.categories = categories

        if self.only_jb:
            tmp = self.parasites.loc[self.parasites[self.categories].any(axis=1) & self.parasites.iloc[:, 2]]
        else:
            tmp = self.parasites.loc[self.parasites[self.categories].any(axis=1)]

        self.qa = pd.DataFrame({'Q': list(tmp['kname']) + list(tmp['sname']), 'A': list(tmp['sname']) + list(tmp['kname'])})

    def select_indices(self, num):
        self.indices = random.sample(range(0, len(self.qa)), num)
        self.cur_questions = list(self.qa.loc[self.indices, 'Q'])
        self.cur_answers = list(self.qa.loc[self.indices, 'A'])


def main():
    root = tk.Tk()                      # root라는 창을 생성
    root.geometry("600x400")       # 창 크기설정
    root.title("Parasite_quiz")    # 창 제목설정
    font=tkinter.font.Font(family="맑은 고딕", size=15)
    root.option_add("*Font", font) # 폰트설정
    root.resizable(False, False)  # x, y 창 크기 변경 불가

    def clear():
        for ele in root.winfo_children():
            ele.destroy()

    def select_number():
        def ddd():
            curQuiz.select_indices(int(ent.get()))
            clear()
            make_quiz()
        tl = tk.Label(root)                    # root라는 창에 레이블 생성
        tl.config(text="질문 개수를 입력하세요. (1 이상 {} 이하의 정수)".format(len(curQuiz.qa)))        # 레이블 텍스트
        tl.pack()

        ent = tk.Entry(root)
        ent.pack()
        button = tk.Button(root)
        button.pack()
        button.config(text='입력', command=ddd)
        root.bind('<Return>', lambda event=None: button.invoke())
        root.iconify()
        root.deiconify()
        ent.focus_set()
    
    def make_quiz():
        clear()
        def check():
            curQuiz.cur_input = ent.get()
            if curQuiz.cur_input == cur_answers[cur_num]:
                curQuiz.re = False
                curQuiz.cur_number += 1
            else:
                curQuiz.re = True
            make_quiz()

        def show_answer():
            tl = tk.Label(root)
            tl.config(text=cur_answers[cur_num])
            tl.pack()
            button2.config(text='다음 문제', command=next_q)

        def next_q():
            clear()
            curQuiz.re = False
            curQuiz.cur_number += 1
            make_quiz()

        cur_questions = curQuiz.cur_questions
        cur_answers = curQuiz.cur_answers
        cur_num = curQuiz.cur_number

        if cur_num < len(cur_questions):
            tl = tk.Label(root)                    # root라는 창에 레이블 생성
            if curQuiz.re:
                tl.config(text=f'{cur_num+1}. 다시 시도하세요. {cur_questions[cur_num]}')
            else:
                tl.config(text=f'{cur_num+1}. {cur_questions[cur_num]}')
            tl.pack()
            ent = tk.Entry(root, width=30)
            ent.pack()
            ent.focus_set()
            button = tk.Button(root)
            button.pack()
            button.config(text='입력', command=check)
            root.bind('<Return>', lambda event=None: button.invoke())
            if curQuiz.re:
                button2 = tk.Button(root)
                button2.pack()
                button2.config(text='정답 보기', command=show_answer)

        else:
            tl = tk.Label(root)
            tl.config(text='문제가 모두 끝났습니다.')
            tl.pack()
            button = tk.Button(root)
            button.pack()
            button.config(text='다시 시작하기', command=restart)
            root.bind('<Return>', lambda event=None: button.invoke())

    def restart():
        clear()
        curQuiz.reset()
        def on_configure(event):
        # Update the scrollable region to encompass the entire frame
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_mousewheel(event):
        # Scroll the canvas when the mousewheel is used
            canvas.yview_scroll(-1 * (event.delta // 120), "units")

        def select_all():
        # Iterate through all checkboxes and set their state to checked
            for checkbox in checkboxes:
                checkbox.set(1)

        def deselect_all():
        # Iterate through all checkboxes and set their state to unchecked
            for checkbox in checkboxes:
                checkbox.set(0)

        def select_categories():
            cur_categories = []
            for chkvar, cat in zip(chkvars, categories):
                if chkvar.get() == 1:
                    cur_categories.append(cat)
            if jb.get() == 1:
                curQuiz.only_jb = True
            else:
                curQuiz.only_jb = False
            curQuiz.set_categories(cur_categories)
            clear()
            select_number()

        canvas = tk.Canvas(root)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(root, command=canvas.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame to contain the checkboxes
        checkbox_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=checkbox_frame, anchor=tk.NW)

        # Bind the frame to the canvas for scrolling
        checkbox_frame.bind("<Configure>", on_configure)

        root.bind_all("<MouseWheel>", on_mousewheel)

        
        chkvars = []
        for i, cat in enumerate(categories):
            chkvar = tk.IntVar()                             # chkvar에 int 형으로 값을 저장
            chkvars.append(chkvar)
            chkbox = tk.Checkbutton(checkbox_frame, variable=chkvar)   # root라는 창에 체크박스 생성
            chkbox.config(text=cat, font=font)
            chkbox.grid(row=i+1, column=0, sticky="w")                  # 체크박스 내용 설정

            
        jb = tk.IntVar()                             # chkvar에 int 형으로 값을 저장
        chkbox = tk.Checkbutton(checkbox_frame, variable=jb)   # root라는 창에 체크박스 생성
        chkbox.config(text='족보만')                  # 체크박스 내용 설정
        chkbox.grid(row=0, column=0, sticky="w")

        checkboxes = chkvars + [jb]
        select_all_button = tk.Button(root, text="Select All", command=select_all)
        select_all_button.pack()

        deselect_all_button = tk.Button(root, text="Deselect All", command=deselect_all)
        deselect_all_button.pack()

        button = tk.Button(root)
        button.pack()
        button.config(text='완료', command=select_categories)
        root.bind('<Return>', lambda event=None: button.invoke())

    filepath = tkinter.filedialog.askopenfile(parent=root, title='Please select a file').name
    parasites = pd.read_csv(filepath, index_col=None, header=0).fillna(int(0))
    curQuiz = QuizGenerator(parasites)
    categories = parasites.columns[3:]
    chkvars = []
    
    restart()
    # root.destroy()
    # root = generate_root()

    # ####

    #          

    # ent = tk.Entry(root)
    # ent.pack()
    # button = tk.Button(root)
    # button.pack()
    # button.config(text='선택', command=select_categories)



    # root.bind('<Return>', lambda event=None: button.invoke())

    root.mainloop()                  # 창 실행

if __name__ == "__main__":
   main()