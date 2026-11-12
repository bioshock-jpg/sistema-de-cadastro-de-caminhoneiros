
import json
import os
import shutil
from tkinter import filedialog, messagebox
import customtkinter as ctk

# --- 1. SUA LÓGICA DE CONFIGURAÇÃO DE PASTAS ---
PASTA_RAIZ = "central_documentos"
PASTA_MOTORISTAS = os.path.join(PASTA_RAIZ, "motoristas")
ARQUIVO_BANCO = os.path.join(PASTA_RAIZ, "banco_dados.json")

os.makedirs(PASTA_MOTORISTAS, exist_ok=True)
if not os.path.exists(ARQUIVO_BANCO):
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump({}, f)


def carregar_banco():
    with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_banco(dados):
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


# --- 2. ESTRUTURA DA INTERFACE GRÁFICA ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AppSistemaCNH(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("SISTEMA DE ARMAZENAMENTO DE CNH")
        self.geometry("750x550")
        self.resizable(False, False)
        self.caminho_documento_selecionado = ""

        # Variável temporária para guardar o arquivo selecionado no cadastro
        self.caminho_documento_selecionado = ""

        # --- CRIAÇÃO DAS ABAS (Menu Principal) ---
        self.abas = ctk.CTkTabview(self, width=720, height=520)
        self.abas.pack(pady=10, padx=10)

        self.tab_cadastro = self.abas.add("Cadastrar Motorista")
        self.tab_busca = self.abas.add("Buscar Motorista")

        # Configurar o conteúdo de cada aba
        self.montar_aba_cadastro()
        self.montar_aba_busca()

    # ================= CONSTRUÇÃO DA TELA DE CADASTRO =================
    def montar_aba_cadastro(self):
        # Título
        lbl = ctk.CTkLabel(
            self.tab_cadastro,
            text="Cadastro do Novo Motorista",
            font=("Arial", 20, "bold"),
        )
        lbl.pack(pady=15)

        # Container dos campos
        frame_campos = ctk.CTkFrame(self.tab_cadastro)
        frame_campos.pack(pady=10, padx=20, fill="x")

        # Campo Nome
        ctk.CTkLabel(frame_campos, text="Nome Completo:").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.txt_nome = ctk.CTkEntry(frame_campos, width=450)
        self.txt_nome.grid(row=0, column=1, padx=10, pady=10, columnspan=2)

        # Campo CPF
        ctk.CTkLabel(frame_campos, text="CPF (apenas números):").grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )
        self.txt_cpf = ctk.CTkEntry(frame_campos, width=200)
        self.txt_cpf.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Campo Placa
        ctk.CTkLabel(frame_campos, text="Placa do Veículo:").grid(
            row=2, column=0, padx=10, pady=10, sticky="w"
        )
        self.txt_placa = ctk.CTkEntry(
            frame_campos, width=200, placeholder_text="Ex: ABC-1D23"
        )
        self.txt_placa.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        #Campo da Placa da Carga Caminhao
        ctk.CTkLabel(frame_campos, text="Placa da Carga Caminhão").grid(
            row=3, column=0, padx=10, pady=10, sticky="w"
        )
        self.txt_carga = ctk.CTkEntry(
            frame_campos, width=200, placeholder_text="Ex: ABC-1D23"
        )
        self.txt_carga.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # Seção de Documento
        frame_doc = ctk.CTkFrame(self.tab_cadastro)
        frame_doc.pack(pady=10, padx=20, fill="x")

        self.btn_selecionar_doc = ctk.CTkButton(
            frame_doc,
            text="Selecionar CNH / CRLV / CARGA",
            command=self.selecionar_arquivo,
            fg_color="blue",
            hover_color="darkblue",
        )
        self.btn_selecionar_doc.grid(row=0, column=0, padx=10, pady=10)

        self.lbl_status_doc = ctk.CTkLabel(
            frame_doc, text="Nenhum arquivo selecionado", text_color="white"
        )
        self.lbl_status_doc.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Botão Final de Salvar
        self.btn_salvar = ctk.CTkButton(
            self.tab_cadastro,
            text="Salvar Cadastro",
            command=self.executar_cadastro,
            fg_color="blue",
            hover_color="darkblue",
            width=200,
            height=40,
            font=("Arial", 14, "bold"),
        )
        self.btn_salvar.pack(pady=20)

    def selecionar_arquivo(self):
        """Abre a janela nativa do sistema para escolher o arquivo."""
        caminho = filedialog.askopenfilename(
            title="Selecione o Documento do Motorista",
            filetypes=[("Arquivos de Documento", "*.pdf *.png *.jpg *.jpeg")],
        )
        if caminho:
            self.caminho_documento_selecionado = caminho
            nome_breve = os.path.basename(caminho)
            self.lbl_status_doc.configure(
                text=f"✔ {nome_breve}", text_color="blue"
            )

    def executar_cadastro(self):
        """Função 'cadastrar_motorista' adaptada para a Interface Gráfica."""
        nome = self.txt_nome.get().strip()
        cpf = self.txt_cpf.get().strip()
        placa = self.txt_placa.get().strip().upper()
        carga = self.txt_carga.get().strip().upper()

        if not nome or not cpf or not placa or not carga:
            messagebox.showwarning(
                "Campos Vazios", "Por favor, preencha todos os campos de texto!"
            )
            return

        banco = carregar_banco()

        if cpf in banco:
            messagebox.showerror(
                "Erro", "⚠️ Este CPF já está cadastrado no sistema!"
            )
            return

        # Cria pasta do motorista
        pasta_do_motorista = os.path.join(PASTA_MOTORISTAS, nome)
        os.makedirs(pasta_do_motorista, exist_ok=True)

        documentos_salvos = []
        # Valida se o usuário selecionou o documento pela janela flutuante
        if (
            self.caminho_documento_selecionado
            and os.path.exists(self.caminho_documento_selecionado)
        ):
            nome_arquivo = os.path.basename(self.caminho_documento_selecionado)
            destino_final = os.path.join(pasta_do_motorista, nome_arquivo)

            shutil.copy(self.caminho_documento_selecionado, destino_final)
            documentos_salvos.append(nome_arquivo)

        # Salva no JSON
        banco[cpf] = {
            "nome": nome,
            "placa": placa,
            "carga": carga,
            "pasta": pasta_do_motorista,
            "documentos": documentos_salvos,
        }
        salvar_banco(banco)

        messagebox.showinfo(
            "Sucesso", f"🎉 Motorista {nome} cadastrado com sucesso!"
        )

        # Limpa o formulário para o próximo
        self.txt_nome.delete(0, "end")
        self.txt_cpf.delete(0, "end")
        self.txt_placa.delete(0, "end")
        self.txt_carga.delete(0, "end")
        self.caminho_documento_selecionado = ""
        self.lbl_status_doc.configure(
            text="Nenhum arquivo selecionado", text_color="yellow"
        )

    # ================= CONSTRUÇÃO DA TELA DE BUSCA =================
    def montar_aba_busca(self):
        lbl = ctk.CTkLabel(
            self.tab_busca,
            text="Buscar Motorista / Localizar Pasta",
            font=("Arial", 20, "bold"),
        )
        lbl.pack(pady=15)

        # Barra de Busca
        frame_busca = ctk.CTkFrame(self.tab_busca)
        frame_busca.pack(pady=10, padx=20, fill="x")

        self.txt_busca = ctk.CTkEntry(
            frame_busca,
            placeholder_text="Digite o Nome ou CPF para buscar...",
            width=450,
        )
        self.txt_busca.grid(row=0, column=0, padx=10, pady=10)

        # Vincula a tecla 'Enter' para também disparar a busca automaticamente
        self.txt_busca.bind("<Return>", lambda event: self.executar_busca())

        btn_buscar = ctk.CTkButton(
            frame_busca, text="Buscar", command=self.executar_busca, width=120
        )
        btn_buscar.grid(row=0, column=1, padx=10, pady=10)

        # Caixa de Resultados (Substitui o print do terminal)
        self.txt_resultado = ctk.CTkTextbox(self.tab_busca, width=680, height=280)
        self.txt_resultado.pack(pady=15)
        self.txt_resultado.configure(state="disabled")

    def executar_busca(self):
        """Função 'buscar_motorista' adaptada para a Interface Gráfica."""
        termo_busca = self.txt_busca.get().strip().lower()

        if not termo_busca:
            return

        banco = carregar_banco()
        encontrado = False

        """Variavel para juntar o texto dos resultados"""
        texto_acumulado =""

        """Loop que varre o banco de dados"""
        for cpf, info in banco.items():
            """Evita erro caso o nome venha vazio"""
            nome_motorista = info.get("nome", "").lower()

        # Ativa o campo de texto para conseguir limpar e escrever os resultados
        self.txt_resultado.configure(state="normal")
        self.txt_resultado.delete("1.0", "end")

        texto_acumulado = ""

        for cpf, info in banco.items():
            if termo_busca in cpf or termo_busca in info.get("nome", "").lower():
                texto_acumulado += f"📌 Motorista Encontrado:\n"
                texto_acumulado += f"   Nome: {info.get('nome', 'Não informado')}\n"
                texto_acumulado += f"   CPF: {cpf}\n"
                texto_acumulado += f"   Placa: {info.get('placa', 'Não informada')}\n"

                """Correção caso o valor JSON for None ou não exitir"""
                carga_salva = info.get('carga')
                carga_exibida = carga_salva if carga_salva else 'Não informada'
                texto_acumulado += f"   Carga: {carga_exibida}\n"

                documentos = info.get('documentos', [])
                texto_acumulado += f"   Arquivos Salvos: {', '.join(documentos) if documentos else 'Nenhum'}\n"

                pasta = info.get('pasta', '.')
                texto_acumulado += f"   📂 Pasta no PC: {os.path.abspath(pasta)}\n"

                texto_acumulado += f"{'-'*60}\n\n"
                encontrado = True

                """Exibe o resultado na interface (ajusta o nome do componente de texto se for diferente)"""
                if encontrado:
                    self.txt_resultado.configure(state="normal")
                    self.txt_resultado.delete("1.0", "end")
                    self.txt_resultado.insert("1.0", texto_acumulado)
                    self.txt_resultado.configure(state="disable")
                else:
                    # Caso não encontre ninguém
                    self.txt_resultado.configure(state="normal")
                    self.txt_resultado.delete("1.0", "end")
                    self.txt_resultado.insert("1.0", "❌ Nenhum motorista encontrado.")
                    self.txt_resultado.configure(state="disabled")

        self.txt_resultado.insert("1.0", texto_acumulado)
        # Bloqueia o campo novamente para o usuário não apagar o resultado sem querer
        self.txt_resultado.configure(state="disabled")


if __name__ == "__main__":
    app = AppSistemaCNH()
    app.mainloop()
