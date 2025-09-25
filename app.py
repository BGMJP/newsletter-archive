#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴스레터 아카이브 관리 도구
- newsletters.json 파일을 GUI로 쉽게 관리
- 뉴스레터 추가, 삭제, 순서 변경 기능
- public 폴더의 HTML 파일 자동 탐지
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import json
import os
from pathlib import Path

class NewsletterManager:
    def __init__(self, root):
        self.root = root
        self.root.title("뉴스레터 아카이브 관리 도구")
        self.root.geometry("800x600")
        self.root.configure(bg='#F8F9FA')
        
        # 데이터 저장 변수
        self.newsletters = []
        self.json_file_path = "public/newsletters.json"
        self.public_folder = "public"
        
        self.setup_ui()
        self.load_newsletters()
        
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="뉴스레터 아카이브 관리", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 뉴스레터 목록 프레임
        list_frame = ttk.LabelFrame(main_frame, text="뉴스레터 목록", padding="10")
        list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # 리스트박스와 스크롤바
        self.listbox = tk.Listbox(list_frame, height=15, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        self.listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 20))
        
        # 버튼들
        ttk.Button(button_frame, text="새 뉴스레터 추가", 
                  command=self.add_newsletter).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text="선택 항목 삭제", 
                  command=self.delete_newsletter).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text="위로 이동", 
                  command=self.move_up).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="아래로 이동", 
                  command=self.move_down).grid(row=0, column=3, padx=(0, 10))
        
        # 저장 버튼 (강조)
        save_button = ttk.Button(main_frame, text="변경사항 저장", 
                                command=self.save_newsletters)
        save_button.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # 상태 표시
        self.status_label = ttk.Label(main_frame, text="준비됨", 
                                     foreground="green")
        self.status_label.grid(row=4, column=0, columnspan=3)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
    def load_newsletters(self):
        """newsletters.json 파일에서 데이터 로드"""
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r', encoding='utf-8') as f:
                    self.newsletters = json.load(f)
                self.update_listbox()
                self.update_status("뉴스레터 목록을 불러왔습니다.")
            else:
                self.newsletters = []
                self.update_status("새로운 뉴스레터 목록을 시작합니다.")
        except Exception as e:
            messagebox.showerror("오류", f"파일을 불러오는데 실패했습니다: {str(e)}")
            self.newsletters = []
            
    def update_listbox(self):
        """리스트박스 업데이트"""
        self.listbox.delete(0, tk.END)
        for i, newsletter in enumerate(self.newsletters):
            self.listbox.insert(tk.END, f"{i+1}. {newsletter['title']}")
            
    def add_newsletter(self):
        """새 뉴스레터 추가"""
        # HTML 파일 선택
        if not os.path.exists(self.public_folder):
            messagebox.showerror("오류", f"{self.public_folder} 폴더가 존재하지 않습니다.")
            return
            
        # public 폴더의 HTML 파일 목록 가져오기
        html_files = []
        try:
            for file in os.listdir(self.public_folder):
                if file.endswith('.html') and file != 'index.html':
                    html_files.append(file)
        except Exception as e:
            messagebox.showerror("오류", f"public 폴더를 읽는데 실패했습니다: {str(e)}")
            return
            
        if not html_files:
            # HTML 파일이 없으면 직접 선택
            file_path = filedialog.askopenfilename(
                title="뉴스레터 HTML 파일 선택",
                initialdir=self.public_folder,
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
            )
            if not file_path:
                return
            file_name = os.path.basename(file_path)
        else:
            # HTML 파일 목록에서 선택
            file_name = self.select_from_list("HTML 파일 선택", 
                                            "public 폴더의 HTML 파일을 선택하세요:", 
                                            html_files)
            if not file_name:
                return
        
        # 제목 입력
        title = simpledialog.askstring("제목 입력", 
                                      f"'{file_name}' 파일의 제목을 입력하세요:",
                                      initialvalue=file_name.replace('.html', ''))
        if not title:
            return
            
        # 뉴스레터 추가
        new_newsletter = {
            "title": title,
            "file": file_name
        }
        
        self.newsletters.insert(0, new_newsletter)  # 맨 위에 추가
        self.update_listbox()
        self.update_status(f"'{title}' 뉴스레터가 추가되었습니다.")
        
    def delete_newsletter(self):
        """선택된 뉴스레터 삭제"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 뉴스레터를 선택하세요.")
            return
            
        index = selection[0]
        newsletter = self.newsletters[index]
        
        if messagebox.askyesno("확인", f"'{newsletter['title']}' 뉴스레터를 삭제하시겠습니까?"):
            del self.newsletters[index]
            self.update_listbox()
            self.update_status(f"'{newsletter['title']}' 뉴스레터가 삭제되었습니다.")
            
    def move_up(self):
        """선택된 항목을 위로 이동"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "이동할 뉴스레터를 선택하세요.")
            return
            
        index = selection[0]
        if index == 0:
            messagebox.showinfo("정보", "이미 맨 위에 있습니다.")
            return
            
        # 위치 변경
        self.newsletters[index], self.newsletters[index-1] = \
            self.newsletters[index-1], self.newsletters[index]
        
        self.update_listbox()
        self.listbox.selection_set(index-1)
        self.update_status("항목이 위로 이동되었습니다.")
        
    def move_down(self):
        """선택된 항목을 아래로 이동"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "이동할 뉴스레터를 선택하세요.")
            return
            
        index = selection[0]
        if index == len(self.newsletters) - 1:
            messagebox.showinfo("정보", "이미 맨 아래에 있습니다.")
            return
            
        # 위치 변경
        self.newsletters[index], self.newsletters[index+1] = \
            self.newsletters[index+1], self.newsletters[index]
        
        self.update_listbox()
        self.listbox.selection_set(index+1)
        self.update_status("항목이 아래로 이동되었습니다.")
        
    def save_newsletters(self):
        """변경사항을 newsletters.json 파일에 저장"""
        try:
            # public 폴더가 없으면 생성
            os.makedirs(self.public_folder, exist_ok=True)
            
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.newsletters, f, ensure_ascii=False, indent=2)
            
            self.update_status("변경사항이 저장되었습니다!", "green")
            messagebox.showinfo("성공", "뉴스레터 목록이 성공적으로 저장되었습니다!")
            
        except Exception as e:
            messagebox.showerror("오류", f"저장에 실패했습니다: {str(e)}")
            self.update_status("저장 실패!", "red")
            
    def select_from_list(self, title, message, options):
        """리스트에서 선택하는 다이얼로그"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 중앙 정렬
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, 
                                   self.root.winfo_rooty() + 50))
        
        result = [None]
        
        ttk.Label(dialog, text=message).pack(pady=10)
        
        listbox = tk.Listbox(dialog, height=10)
        listbox.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        for option in options:
            listbox.insert(tk.END, option)
            
        def on_select():
            selection = listbox.curselection()
            if selection:
                result[0] = options[selection[0]]
                dialog.destroy()
            else:
                messagebox.showwarning("경고", "항목을 선택하세요.")
                
        def on_cancel():
            dialog.destroy()
            
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="선택", command=on_select).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="취소", command=on_cancel).pack(side=tk.LEFT, padx=5)
        
        # 더블클릭으로도 선택 가능
        listbox.bind('<Double-Button-1>', lambda e: on_select())
        
        dialog.wait_window()
        return result[0]
        
    def update_status(self, message, color="black"):
        """상태 메시지 업데이트"""
        self.status_label.config(text=message, foreground=color)
        self.root.after(3000, lambda: self.status_label.config(text="준비됨", foreground="green"))

def main():
    """메인 함수"""
    root = tk.Tk()
    app = NewsletterManager(root)
    
    # 창 닫기 이벤트 처리
    def on_closing():
        if messagebox.askokcancel("종료", "프로그램을 종료하시겠습니까?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
