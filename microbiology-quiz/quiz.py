import tkinter as tk
import tkinter.font
import tkinter.filedialog
from tkinter import ttk
import pandas as pd
import random
import os
from glob import glob


class QuizGenerator:
    def __init__(self, content):
        self.content = content
        self.categories = None
        self.only_jb = False

        self.qa = None
        self.indices = None
        self.cur_questions = None
        self.cur_answers = None
        self.cur_statements = None

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
        self.cur_statements = None

        self.cur_number = 0
        self.cur_input = None
        self.re = False

    def set_categories(self, categories):
        self.categories = categories

        if self.only_jb:
            tmps = []
            for i in range(len(self.categories)):
                prefix = f'{self.categories[i]}_1_'
                tmp = self.content[self.content['filename'].str.startswith(prefix)]
                tmps.append(tmp)

            temp = pd.concat(tmps, ignore_index=True)

        else:
            tmps = []
            for i in range(len(self.categories)):
                prefix = f'{self.categories[i]}_'
                tmp = self.content[self.content['filename'].str.startswith(prefix)]
                tmps.append(tmp)

            temp = pd.concat(tmps, ignore_index=True)

        def combine_to_list(series):
            return list(series)
        
        temp['RemarkA'] = temp.apply(lambda row: '' if row['RemarkA'] == '' else f"{row['Answer']} - {row['RemarkA']}", axis=1)
        temp = temp.groupby(['Question', 'filename']).agg(combine_to_list).reset_index()
        temp['Statement'] = temp['Statement'].apply(lambda x: x[0])
        temp['RemarkQ'] = temp['RemarkQ'].apply(lambda x: x[0])
        temp['RemarkQ'] = temp.apply(lambda row: '' if row['RemarkQ'] == '' else f"{row['Question']} - {row['RemarkQ']}", axis=1)
        temp['RemarkA'] = temp['RemarkA'].apply(lambda x: '\n'.join([item for item in x if item != '']))
        temp['Remark'] = temp.apply(lambda row: '\n'.join(filter(None, [row['RemarkQ'], row['RemarkA']])), axis=1)
        TMP = temp.groupby('filename')['Answer'].apply(lambda x: [item for sublist in x for item in sublist]).reset_index()
        TMP.rename(columns={'Answer': 'Choice'}, inplace=True)
        TMP['Choice'] = TMP['Choice'].apply(lambda x: list(set(x)))
        temp = temp.merge(TMP[['filename', 'Choice']], on='filename', how='left')
        self.qa = temp[['Question', 'Answer', 'Choice', 'Statement', 'Remark', 'filename']]


    def select_indices(self, num):
        self.indices = random.sample(range(len(self.qa)), num)
        self.cur_questions = [random.choice(question.split(' | ')) for question in list(self.qa.loc[self.indices, 'Question'])]
        self.cur_answers = list(self.qa.loc[self.indices, 'Answer'])
        self.cur_choices = list(self.qa.loc[self.indices, 'Choice'])
        self.cur_statements = list(self.qa.loc[self.indices, 'Statement'])
        self.cur_remarks = list(self.qa.loc[self.indices, 'Remark'])
        self.cur_filenames = list(self.qa.loc[self.indices, 'filename'])


class WrappingLabel(tk.Label):
    '''a type of Label that automatically adjusts the wrap to the size'''
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))

class WrappingCheckbutton(tk.Checkbutton):
    '''a type of Label that automatically adjusts the wrap to the size'''
    def __init__(self, master=None, **kwargs):
        tk.Checkbutton.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))

def main():
    root = tk.Tk()                      # root라는 창을 생성
    root.geometry("600x500")       # 창 크기설정
    root.title("Microbiology Quiz")    # 창 제목설정
    font=tkinter.font.Font(family="맑은 고딕", size=15)
    root.option_add("*Font", font) # 폰트설정
    root.resizable(True, True)  # x, y 창 크기 변경 불가
    

    def clear():
        for ele in root.winfo_children():
            ele.destroy()

    def select_number():
        def ddd():
            curQuiz.select_indices(int(ent.get()))
            clear()
            make_quiz()
        tl = WrappingLabel(root)                    # root라는 창에 레이블 생성
        tl.config(text="문제 개수를 입력하세요. (1 이상 {} 이하의 정수)".format(len(curQuiz.qa)))        # 레이블 텍스트
        tl.pack(fill=tk.X)

        ent = tk.Entry(root)
        ent.pack()
        button = tk.Button(root)
        button.pack()
        button.config(text='입력', command=ddd)
        root.bind('<Return>', lambda event=None: button.invoke())
        root.iconify()
        root.deiconify()
        ent.focus_set()

    def invariant(str):
        capital = str.lower()
        And = capital.replace(' and ', ',')
        space = And.replace(' ', '')
        hyphen = space.replace('-', '')
        multiple = hyphen.split('|')
        order = [','.join(sorted(item.split(','))) for item in multiple]
        return order
    
    def intersection(list1, list2):
        return [value for value in list1 if value in list2]

    def checkanswer(input, answer):
        input = invariant(input)
        answer = invariant(answer)
        return all(item in answer for item in input)
        
    def make_quiz():
        clear()
        def check():
            curQuiz.cur_input = ent.get()
            if checkanswer(curQuiz.cur_input, ','.join(cur_answers[cur_num])):
                curQuiz.re = False
                curQuiz.cur_number += 1
            else:
                curQuiz.re = True
            make_quiz()

        
        def check_choice():
            selected_categories = []
            for i, chcvar in enumerate(chcvars):
                if chcvar.get() == 1:
                    selected_categories.append(choice[i])
            curQuiz.cur_input = selected_categories
            if sorted(curQuiz.cur_input) == sorted(intersection(choice,cur_answers[cur_num])):
                curQuiz.re = False
                curQuiz.cur_number += 1
            else:
                curQuiz.re = True
            make_quiz()     
    

        def show_answer():
            t3 = WrappingLabel(root)
            t3.config(text=',\n'.join(cur_answers[cur_num]))
            t3.pack(fill=tk.X)
            button3.config(state="disabled")

        def previous_q():
            clear()
            curQuiz.re = False
            curQuiz.cur_number -= 1
            make_quiz()

        def next_q():
            clear()
            curQuiz.re = False
            curQuiz.cur_number += 1
            make_quiz()

        def show_remark():
            t4 = WrappingLabel(root)
            t4.config(text=cur_remarks[cur_num])
            t4.pack(fill=tk.X)
            button4.config(state="disabled")

        cur_questions = curQuiz.cur_questions
        cur_answers = curQuiz.cur_answers
        cur_choices = curQuiz.cur_choices
        cur_statements = curQuiz.cur_statements
        cur_remarks = curQuiz.cur_remarks
        cur_filenames = curQuiz.cur_filenames

        cur_num = curQuiz.cur_number

        if cur_num < len(cur_questions):
            if cur_num < 0:
                restart()
            else:
                tl = WrappingLabel(root)                    
                question = cur_questions[cur_num]
                if curQuiz.re:
                    tl.config(text=f'문제 {cur_num+1}. 다시 시도하세요. {question}')
                else:
                    tl.config(text=f'문제 {cur_num+1}. {question}')
                tl.pack(fill=tk.X)
                t2 = WrappingLabel(root) 
                t2.config(text=cur_statements[cur_num])
                t2.pack(fill=tk.X)
                
                if cur_filenames[cur_num].endswith('주관식.tsv'):
                    ent = tk.Entry(root, width=30)
                    ent.pack()
                    ent.focus_set()
                    button1 = tk.Button(root)
                    button1.pack(side="left", anchor="nw")
                    button1.config(text='이전 문제', command=previous_q)
                    root.bind('<Left>', lambda event=None: button1.invoke())
                    button2 = tk.Button(root)
                    button2.pack(side="right", anchor="ne")
                    button2.config(text='다음 문제', command=next_q)
                    root.bind('<Right>', lambda event=None: button2.invoke())
                    button = tk.Button(root)
                    button.pack()
                    button.config(text='완료', command=check)
                    root.bind('<Return>', lambda event=None: button.invoke())
                    button3 = tk.Button(root)
                    button3.pack()
                    button3.config(text='정답 보기', command=show_answer)
                    root.bind('<Up>', lambda event=None: button3.invoke())
                    root.bind('<Return>', lambda event=None: button.invoke())
                else:
                    if len(cur_choices[cur_num])>5:
                        while True:
                            choice = random.sample(cur_choices[cur_num], 5)
                            if len(intersection(choice, cur_answers[cur_num])) > 0:
                                break
                    else:
                        choice = random.sample(cur_choices[cur_num], len(cur_choices[cur_num]))

                    canvas = tk.Canvas(root)
                    canvas.pack(side=tk.LEFT, fill=tk.BOTH)

                    scrollbar = ttk.Scrollbar(root, command=canvas.yview)
                    scrollbar.pack(side=tk.LEFT, fill=tk.Y)
                    canvas.configure(yscrollcommand=scrollbar.set)
                    def on_configure(event):
                        canvas.configure(scrollregion=canvas.bbox("all"))

                    def on_mousewheel(event):
                        canvas.yview_scroll(-1 * (event.delta // 120), "units")
                        
                    checkbox_frame = tk.Frame(canvas)
                    canvas.create_window((0, 0), window=checkbox_frame, anchor=tk.NW)

                    # Bind the frame to the canvas for scrolling
                    checkbox_frame.bind("<Configure>", on_configure)

                    root.bind_all("<MouseWheel>", on_mousewheel)

                    chcvars = []
                    vars = {}
                    boxes = {}
                    for i, cat in enumerate(choice):
                        var_name = f'chcvar_{i}'
                        box_name = f'chkbox_{i}'
                        vars[var_name] = tk.IntVar()
                        chcvars.append(vars[var_name])
                        boxes[box_name] = tk.Checkbutton(checkbox_frame, variable=vars[var_name])
                        boxes[box_name].config(text=random.choice(cat.split(' | ')), font=font, wraplength=350, justify='left')
                        boxes[box_name].grid(row=i, column=0, sticky='w')
                        root.bind(str(i+1), lambda event, x=boxes[box_name]: x.toggle())

                        

                    button1 = tk.Button(root)
                    button1.pack()
                    button1.config(text='이전 문제', command=previous_q)
                    root.bind('<Left>', lambda event=None: button1.invoke())
                    button2 = tk.Button(root)
                    button2.pack()
                    button2.config(text='다음 문제', command=next_q)
                    root.bind('<Right>', lambda event=None: button2.invoke())
                    button = tk.Button(root)
                    button.pack()
                    button.config(text='완료', command=check_choice)
                    root.bind('<Return>', lambda event=None: button.invoke())
                    button3 = tk.Button(root)
                    button3.pack()
                    button3.config(text='정답 보기', command=show_answer)
                    root.bind('<Up>', lambda event=None: button3.invoke())
                if cur_remarks[cur_num] == '':
                    pass
                else:
                    button4 = tk.Button(root)
                    button4.pack()
                    button4.config(text='참고', command=show_remark)
                    root.bind('<Down>', lambda event=None: button4.invoke())

        else:
            tl = WrappingLabel(root)
            tl.config(text='문제가 모두 끝났습니다.')
            tl.pack(fill=tk.X)
            button1 = tk.Button(root)
            button1.pack()
            button1.config(text='이전 문제', command=previous_q)
            root.bind('<Left>', lambda event=None: button1.invoke())
            button = tk.Button(root)
            button.pack(pady=100)
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
        for i, cat in enumerate(lecture_list):
            chkvar = tk.IntVar()                             # chkvar에 int 형으로 값을 저장
            chkvars.append(chkvar)
            chkbox = tk.Checkbutton(checkbox_frame, variable=chkvar)   # root라는 창에 체크박스 생성
            chkbox.config(text=cat, font=font)
            chkbox.grid(row=i, column=0, sticky="w")                  # 체크박스 내용 설정

        jb = tk.IntVar()                             # chkvar에 int 형으로 값을 저장
        chkbox = tk.Checkbutton(root, variable=jb)   # root라는 창에 체크박스 생성
        chkbox.config(text='족보만')                  # 체크박스 내용 설정
        chkbox.pack()

        checkboxes = chkvars
        select_all_button = tk.Button(root, text="Select All", command=select_all)
        select_all_button.pack()
        root.bind('<Up>', lambda event=None: select_all_button.invoke())


        deselect_all_button = tk.Button(root, text="Deselect All", command=deselect_all)
        deselect_all_button.pack()
        root.bind('<Down>', lambda event=None: deselect_all_button.invoke())

        button = tk.Button(root)
        button.pack()
        button.config(text='완료', command=select_categories)
        root.bind('<Return>', lambda event=None: button.invoke())
        root.iconify()
        root.deiconify()

    directory = tkinter.filedialog.askdirectory(parent=root, title='Please select a folder')

    lecture_name = pd.read_csv(os.path.join(directory, 'Lecture_Names.csv'), header=None)
    categories = lecture_name[0]
    lecture_list = lecture_name[1]
    file_list = glob(directory+'/*.tsv')
    dfs = []
    for filename in file_list:
        df = pd.read_table(filename, header=0).fillna('')
        df['filename'] = filename.replace(directory+'\\', '')
        dfs.append(df)
    content = pd.concat(dfs, ignore_index=True)
    curQuiz = QuizGenerator(content)
    restart()

    root.mainloop()                  # 창 실행

if __name__ == "__main__":
   main()