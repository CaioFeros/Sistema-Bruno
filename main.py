"""
Sistema de Extração de Dados de Recibos PDF
Interface principal com tkinter.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from pathlib import Path
import sys
import threading

# Tentar importar tkinterdnd2 (opcional para drag and drop)
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    TkinterDnD = None

from pdf_extractor import extract_from_pdf
from data_processor import process_receipt_data, process_multiple_receipts, validate_data, calculate_seller_statistics
from excel_exporter import export_to_excel


class ReceiptExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Extração de Recibos PDF")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.current_pdf_path = None
        self.current_dataframe = None
        self.progress_window = None
        self.is_processing = False
        
        # Configurar tema dark
        self.setup_dark_theme()
        
        self.setup_ui()
    
    def setup_dark_theme(self):
        """Configura o tema dark mode moderno."""
        # Cores do tema dark
        self.colors = {
            'bg_main': '#1e1e1e',           # Fundo principal (muito escuro)
            'bg_secondary': '#252525',      # Fundo secundário
            'bg_tertiary': '#2d2d2d',       # Fundo terciário
            'bg_widget': '#323232',         # Fundo de widgets
            'bg_button': '#3a3a3a',         # Fundo de botões
            'bg_button_hover': '#4a4a4a',   # Botão hover
            'bg_tree': '#252525',           # Fundo do treeview
            'bg_tree_select': '#404040',    # Seleção no treeview
            'text_primary': '#ffffff',      # Texto principal
            'text_secondary': '#b0b0b0',    # Texto secundário
            'text_disabled': '#666666',     # Texto desabilitado
            'border': '#404040',            # Borda
            'border_focus': '#0078d4',      # Borda foco (azul)
            'accent': '#0078d4',            # Cor de destaque (azul)
            'accent_hover': '#1084e0',      # Accent hover
            'success': '#28a745',           # Verde sucesso
            'warning': '#ffc107',           # Amarelo aviso
            'error': '#dc3545',             # Vermelho erro
        }
        
        # Configurar fundo da janela principal
        self.root.configure(bg=self.colors['bg_main'])
        
        # Criar estilo para ttk widgets
        style = ttk.Style()
        
        # Tentar usar tema dark nativo (se disponível)
        try:
            style.theme_use('clam')
        except:
            try:
                style.theme_use('alt')
            except:
                pass
        
        # Configurar estilos para diferentes widgets
        self._configure_ttk_styles(style)
    
    def _configure_ttk_styles(self, style):
        """Configura estilos específicos para widgets ttk."""
        # Frame
        style.configure('TFrame', 
                       background=self.colors['bg_main'],
                       borderwidth=0)
        
        # LabelFrame
        style.configure('TLabelframe',
                       background=self.colors['bg_main'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='flat')
        style.configure('TLabelframe.Label',
                       background=self.colors['bg_main'],
                       foreground=self.colors['text_primary'],
                       font=('Arial', 10, 'bold'))
        
        # Label
        style.configure('TLabel',
                       background=self.colors['bg_main'],
                       foreground=self.colors['text_primary'],
                       font=('Arial', 9))
        
        # Button
        style.configure('TButton',
                       background=self.colors['bg_button'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='flat',
                       padding=8,
                       font=('Arial', 9))
        style.map('TButton',
                 background=[('active', self.colors['bg_button_hover']),
                            ('pressed', self.colors['bg_tertiary'])],
                 foreground=[('disabled', self.colors['text_disabled'])])
        
        # Progressbar
        style.configure('TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['bg_tertiary'],
                       borderwidth=0,
                       lightcolor=self.colors['accent'],
                       darkcolor=self.colors['accent'])
        
        # Scrollbar
        style.configure('TScrollbar',
                       background=self.colors['bg_tertiary'],
                       troughcolor=self.colors['bg_main'],
                       borderwidth=0,
                       arrowcolor=self.colors['text_secondary'],
                       darkcolor=self.colors['bg_tertiary'],
                       lightcolor=self.colors['bg_tertiary'])
        style.map('TScrollbar',
                 background=[('active', self.colors['bg_widget'])],
                 arrowcolor=[('active', self.colors['text_primary'])])
        
        # Treeview
        style.configure('Treeview',
                       background=self.colors['bg_tree'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_tree'],
                       borderwidth=0,
                       font=('Arial', 9))
        style.configure('Treeview.Heading',
                       background=self.colors['bg_widget'],
                       foreground=self.colors['text_primary'],
                       relief='flat',
                       borderwidth=1,
                       font=('Arial', 9, 'bold'))
        style.map('Treeview',
                 background=[('selected', self.colors['bg_tree_select'])],
                 foreground=[('selected', self.colors['text_primary'])])
        style.map('Treeview.Heading',
                 background=[('active', self.colors['bg_button'])])
    
    def setup_ui(self):
        """Configura a interface do usuário."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Sistema de Extração de Recibos PDF",
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Frame de upload
        upload_frame = ttk.LabelFrame(main_frame, text="Upload de PDF", padding="10")
        upload_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        upload_frame.columnconfigure(0, weight=1)
        
        # Área de drag and drop
        self.drop_area = tk.Text(
            upload_frame,
            height=4,
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=1,
            bg=self.colors['bg_tertiary'],
            fg=self.colors['text_secondary'],
            insertbackground=self.colors['text_primary'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['text_primary'],
            font=("Arial", 10),
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['accent']
        )
        self.drop_area.insert("1.0", "Arraste o arquivo PDF aqui ou clique em 'Selecionar PDF'")
        self.drop_area.config(state=tk.DISABLED)
        self.drop_area.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botão selecionar PDF
        select_btn = ttk.Button(
            upload_frame,
            text="Selecionar PDF",
            command=self.select_pdf
        )
        select_btn.grid(row=1, column=0, padx=(0, 5))
        
        # Botão processar
        self.process_btn = ttk.Button(
            upload_frame,
            text="Processar PDF",
            command=self.process_pdf,
            state=tk.DISABLED
        )
        self.process_btn.grid(row=1, column=1)
        
        # Frame de preview
        preview_frame = ttk.LabelFrame(main_frame, text="Preview dos Dados", padding="10")
        preview_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Treeview para preview
        columns = ('Nº Recibo', 'Vendedor', 'Cliente', 'Descrição do Produto', 'Quantidade', 'Valor Unitário')
        self.tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=15)
        
        # Configurar colunas
        self.tree.heading('Nº Recibo', text='Nº Recibo')
        self.tree.heading('Vendedor', text='Vendedor')
        self.tree.heading('Cliente', text='Cliente')
        self.tree.heading('Descrição do Produto', text='Descrição do Produto')
        self.tree.heading('Quantidade', text='Quantidade')
        self.tree.heading('Valor Unitário', text='Valor Unitário')
        
        # Larguras das colunas
        self.tree.column('Nº Recibo', width=100)
        self.tree.column('Vendedor', width=150)
        self.tree.column('Cliente', width=180)
        self.tree.column('Descrição do Produto', width=250)
        self.tree.column('Quantidade', width=80)
        self.tree.column('Valor Unitário', width=120)
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Frame de ações
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        # Status label
        self.status_label = ttk.Label(
            action_frame,
            text="Pronto para processar PDF",
            font=("Arial", 9),
            foreground=self.colors['text_secondary']
        )
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Botão limpar dados
        self.clear_btn = ttk.Button(
            action_frame,
            text="Limpar Dados",
            command=self.clear_data,
            state=tk.NORMAL
        )
        self.clear_btn.grid(row=0, column=1, sticky=tk.E, padx=(10, 5))
        
        # Botão exportar
        self.export_btn = ttk.Button(
            action_frame,
            text="Exportar para Excel",
            command=self.export_to_excel,
            state=tk.DISABLED
        )
        self.export_btn.grid(row=0, column=2, sticky=tk.E, padx=(0, 0))
        
        action_frame.columnconfigure(0, weight=1)
        
        # Configurar drag and drop
        self.setup_drag_drop()
    
    def setup_drag_drop(self):
        """Configura funcionalidade de drag and drop."""
        if DND_AVAILABLE:
            try:
                self.drop_area.drop_target_register(DND_FILES)
                self.drop_area.dnd_bind('<<Drop>>', self.on_drop)
            except:
                # Se houver erro ao configurar drag and drop, continuar sem ele
                pass
    
    def on_drop(self, event):
        """Handler para evento de drop de arquivo."""
        if not DND_AVAILABLE:
            return
        
        try:
            files = self.root.tk.splitlist(event.data)
            if files:
                file_path = files[0]
                if file_path.lower().endswith('.pdf'):
                    self.current_pdf_path = file_path
                    self.drop_area.config(state=tk.NORMAL, fg=self.colors['text_primary'])
                    self.drop_area.delete("1.0", tk.END)
                    self.drop_area.insert("1.0", f"Arquivo selecionado: {Path(file_path).name}")
                    self.drop_area.config(state=tk.DISABLED)
                    self.process_btn.config(state=tk.NORMAL)
                    self.status_label.config(text="Arquivo carregado. Clique em 'Processar PDF'", foreground=self.colors['text_primary'])
                else:
                    messagebox.showerror("Erro", "Por favor, selecione um arquivo PDF.")
        except Exception:
            pass
    
    def select_pdf(self):
        """Abre diálogo para selecionar arquivo PDF."""
        file_path = filedialog.askopenfilename(
            title="Selecionar PDF",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.current_pdf_path = file_path
            self.drop_area.config(state=tk.NORMAL, fg=self.colors['text_primary'])
            self.drop_area.delete("1.0", tk.END)
            self.drop_area.insert("1.0", f"Arquivo selecionado: {Path(file_path).name}")
            self.drop_area.config(state=tk.DISABLED)
            self.process_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Arquivo carregado. Clique em 'Processar PDF'", foreground=self.colors['text_primary'])
    
    def create_progress_window(self):
        """Cria janela de progresso."""
        if self.progress_window:
            return
        
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Processando PDF")
        self.progress_window.geometry("400x150")
        self.progress_window.resizable(False, False)
        self.progress_window.transient(self.root)
        self.progress_window.grab_set()
        
        # Aplicar tema dark na janela de progresso
        self.progress_window.configure(bg=self.colors['bg_main'])
        
        # Centralizar janela
        self.progress_window.update_idletasks()
        x = (self.progress_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.progress_window.winfo_screenheight() // 2) - (150 // 2)
        self.progress_window.geometry(f"400x150+{x}+{y}")
        
        # Frame principal
        frame = ttk.Frame(self.progress_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Label de status
        self.progress_label = ttk.Label(
            frame, 
            text="Iniciando processamento...", 
            font=("Arial", 10),
            foreground=self.colors['text_primary']
        )
        self.progress_label.pack(pady=(0, 10))
        
        # Barra de progresso
        self.progress_bar = ttk.Progressbar(frame, mode='determinate', length=350)
        self.progress_bar.pack(pady=(0, 10))
        
        # Label de contador
        self.progress_counter = ttk.Label(
            frame, 
            text="", 
            font=("Arial", 9),
            foreground=self.colors['text_secondary']
        )
        self.progress_counter.pack()
        
        # Botão cancelar (desabilitado por enquanto)
        self.cancel_btn = ttk.Button(
            frame, 
            text="Cancelar", 
            command=self.cancel_processing, 
            state=tk.DISABLED
        )
        self.cancel_btn.pack(pady=(10, 0))
    
    def update_progress(self, current, total, message=""):
        """Atualiza a janela de progresso."""
        if not self.progress_window:
            return
        
        try:
            if total > 0:
                percentage = (current / total) * 100
                self.progress_bar['value'] = percentage
                self.progress_counter.config(text=f"{current} de {total} páginas")
            else:
                self.progress_bar['mode'] = 'indeterminate'
                self.progress_bar.start()
            
            if message:
                self.progress_label.config(text=message)
            
            self.progress_window.update()
        except:
            pass
    
    def close_progress_window(self):
        """Fecha a janela de progresso."""
        if self.progress_window:
            try:
                self.progress_bar.stop()
                self.progress_window.destroy()
                self.progress_window = None
            except:
                pass
    
    def cancel_processing(self):
        """Cancela o processamento."""
        self.is_processing = False
        self.close_progress_window()
        self.status_label.config(text="Processamento cancelado", foreground=self.colors['warning'])
    
    def process_pdf(self):
        """Processa o PDF selecionado e exibe os dados."""
        if not self.current_pdf_path:
            messagebox.showerror("Erro", "Nenhum arquivo PDF selecionado.")
            return
        
        if self.is_processing:
            messagebox.showwarning("Aviso", "Já existe um processamento em andamento.")
            return
        
        # Desabilitar botão de processar
        self.process_btn.config(state=tk.DISABLED)
        self.is_processing = True
        
        # Criar janela de progresso
        self.create_progress_window()
        
        # Processar em thread separada
        thread = threading.Thread(target=self._process_pdf_thread, daemon=True)
        thread.start()
    
    def _process_pdf_thread(self):
        """Processa o PDF em thread separada."""
        try:
            # Callback de progresso
            def progress_callback(current, total, message=""):
                if not self.is_processing:
                    return
                self.root.after(0, self.update_progress, current, total, message)
            
            # Extrair dados do PDF (pode retornar múltiplos recibos)
            receipts_data = extract_from_pdf(self.current_pdf_path, progress_callback)
            
            if not self.is_processing:
                return
            
            # Processar dados (suporta múltiplos recibos)
            self.root.after(0, self.update_progress, 0, 0, "Processando dados extraídos...")
            
            if isinstance(receipts_data, list):
                self.current_dataframe = process_multiple_receipts(receipts_data)
                num_recibos = len(receipts_data)
            else:
                # Compatibilidade com formato antigo (único recibo)
                self.current_dataframe = process_receipt_data(receipts_data)
                num_recibos = 1
            
            if not self.is_processing:
                return
            
            # Validar dados
            is_valid, errors = validate_data(self.current_dataframe)
            
            # Atualizar interface na thread principal
            self.root.after(0, self._finish_processing, is_valid, errors, num_recibos)
            
        except FileNotFoundError as e:
            self.root.after(0, self._handle_error, f"Arquivo não encontrado:\n{str(e)}")
        except Exception as e:
            self.root.after(0, self._handle_error, f"Erro ao processar PDF:\n{str(e)}")
    
    def _finish_processing(self, is_valid, errors, num_recibos):
        """Finaliza o processamento na thread principal."""
        self.is_processing = False
        self.close_progress_window()
        
        if not is_valid:
            error_msg = "\n".join(errors)
            messagebox.showwarning("Aviso", f"Alguns problemas foram encontrados:\n\n{error_msg}")
        
        # Atualizar preview
        self.update_preview(self.current_dataframe)
        
        # Habilitar botão de exportar
        self.export_btn.config(state=tk.NORMAL)
        self.process_btn.config(state=tk.NORMAL)
        
        num_linhas = len(self.current_dataframe)
        status_msg = f"Dados processados com sucesso! {num_recibos} recibo(s) e {num_linhas} linha(s) encontrada(s)."
        self.status_label.config(text=status_msg, foreground=self.colors['success'])
    
    def _handle_error(self, error_msg):
        """Trata erros na thread principal."""
        self.is_processing = False
        self.close_progress_window()
        messagebox.showerror("Erro", error_msg)
        self.status_label.config(text="Erro ao processar PDF", foreground=self.colors['error'])
        self.process_btn.config(state=tk.NORMAL)
    
    def update_preview(self, df: pd.DataFrame):
        """Atualiza o preview com os dados do DataFrame."""
        # Limpar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar dados
        for _, row in df.iterrows():
            values = (
                str(row.get('Nº Recibo', '')),
                str(row.get('Vendedor', '')),
                str(row.get('Cliente', '')),
                str(row.get('Descrição do Produto', '')),
                str(row.get('Quantidade', '')),
                str(row.get('Valor Unitário', ''))
            )
            self.tree.insert('', tk.END, values=values)
    
    def clear_data(self):
        """Limpa os dados processados e permite importar novos dados."""
        # Confirmar com o usuário se há dados para limpar
        if self.current_dataframe is not None and not self.current_dataframe.empty:
            resposta = messagebox.askyesno(
                "Limpar Dados",
                "Deseja realmente limpar os dados processados?\n\nIsso removerá:\n- Dados do preview\n- Informações do PDF processado\n\nVocê poderá importar novos dados depois.",
                icon='question'
            )
            if not resposta:
                return
        
        # Cancelar qualquer processamento em andamento
        if self.is_processing:
            self.is_processing = False
            self.close_progress_window()
        
        # Limpar DataFrame
        self.current_dataframe = None
        
        # Limpar caminho do PDF
        self.current_pdf_path = None
        
        # Limpar preview (treeview)
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Resetar área de drop
        self.drop_area.config(state=tk.NORMAL, fg=self.colors['text_secondary'])
        self.drop_area.delete("1.0", tk.END)
        self.drop_area.insert("1.0", "Arraste o arquivo PDF aqui ou clique em 'Selecionar PDF'")
        self.drop_area.config(state=tk.DISABLED)
        
        # Desabilitar botão de exportar
        self.export_btn.config(state=tk.DISABLED)
        
        # Desabilitar botão de processar (sem PDF selecionado)
        self.process_btn.config(state=tk.DISABLED)
        
        # Resetar status
        self.status_label.config(text="Dados limpos. Pronto para processar novo PDF.", foreground=self.colors['text_secondary'])
        
        messagebox.showinfo("Sucesso", "Dados limpos com sucesso!\n\nVocê pode agora selecionar e processar um novo PDF.")
    
    def export_to_excel(self):
        """Exporta os dados processados para Excel."""
        if self.current_dataframe is None or self.current_dataframe.empty:
            messagebox.showerror("Erro", "Nenhum dado para exportar.")
            return
        
        try:
            # Perguntar onde salvar
            file_path = filedialog.asksaveasfilename(
                title="Salvar como Excel",
                defaultextension=".xlsx",
                filetypes=[("Arquivos Excel", "*.xlsx"), ("Todos os arquivos", "*.*")]
            )
            
            if file_path:
                self.status_label.config(text="Calculando estatísticas e exportando para Excel...")
                self.root.update()
                
                # Calcular estatísticas por vendedor
                df_stats = calculate_seller_statistics(self.current_dataframe)
                
                # Exportar
                from excel_exporter import export_to_excel_with_path
                export_to_excel_with_path(self.current_dataframe, file_path, df_stats)
                
                messagebox.showinfo("Sucesso", f"Arquivo Excel salvo com sucesso!\n\nAba 'Recibos': Dados detalhados\nAba 'Estatísticas por Vendedor': Estatísticas agrupadas\n\n{file_path}")
                self.status_label.config(text="Exportação concluída com sucesso!", foreground=self.colors['success'])
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar para Excel:\n{str(e)}")
            self.status_label.config(text="Erro ao exportar", foreground=self.colors['error'])


def main():
    """Função principal."""
    if DND_AVAILABLE and TkinterDnD:
        try:
            root = TkinterDnD.Tk()
        except:
            root = tk.Tk()
    else:
        root = tk.Tk()
    
    app = ReceiptExtractorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

