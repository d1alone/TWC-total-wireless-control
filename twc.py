#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Benyvan (@benyvan)
"""TWC - Total Wireless Control."""

import os
import re
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk


class TWCApp:
    COLORS = {
        "background": "#0f172a",
        "surface": "#1e293b",
        "surface_light": "#334155",
        "text": "#e2e8f0",
        "muted": "#94a3b8",
        "accent": "#38bdf8",
        "success": "#4ade80",
        "warning": "#fbbf24",
        "danger": "#fb7185",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("TWC — Total Wireless Control")
        self.root.geometry("990x613")
        self.root.minsize(990, 613)
        self.root.configure(bg=self.COLORS["background"])
        icon_path = "/usr/share/pixmaps/twc.png"
        if not os.path.isfile(icon_path):
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "twc.png")
        if os.path.isfile(icon_path):
            self.window_icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, self.window_icon)
        self.busy = False
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() - width) // 2
        self.root.geometry("{}x{}+{}+0".format(width, height, x))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TCombobox",
            fieldbackground=self.COLORS["surface_light"],
            background=self.COLORS["surface_light"],
            foreground=self.COLORS["text"],
            arrowcolor=self.COLORS["text"],
            bordercolor=self.COLORS["surface_light"],
            lightcolor=self.COLORS["surface_light"],
            darkcolor=self.COLORS["surface_light"],
            padding=7,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.COLORS["surface_light"])],
            foreground=[("readonly", self.COLORS["text"])],
        )

        header = tk.Frame(root, bg=self.COLORS["background"])
        header.pack(fill=tk.X, padx=24, pady=(22, 14))
        tk.Label(
            header,
            text="TWC",
            font=("Arial", 25, "bold"),
            fg=self.COLORS["accent"],
            bg=self.COLORS["background"],
        ).pack(side=tk.LEFT)
        tk.Label(
            header,
            text="TOTAL WIRELESS CONTROL",
            font=("Arial", 12, "bold"),
            fg=self.COLORS["text"],
            bg=self.COLORS["background"],
        ).pack(side=tk.LEFT, padx=(12, 0), pady=(8, 0))
        header_info = tk.Frame(header, bg=self.COLORS["background"])
        header_info.pack(side=tk.RIGHT, pady=(3, 0))
        tk.Label(
            header_info,
            text="Idealizado em 08/11/2026 • @benyvan",
            font=("Arial", 10, "bold"),
            fg=self.COLORS["accent"],
            bg=self.COLORS["background"],
            anchor="e",
        ).pack(anchor="e")
        tk.Label(
            header_info,
            text="Controle de interfaces wireless",
            font=("Arial", 9),
            fg=self.COLORS["muted"],
            bg=self.COLORS["background"],
            anchor="e",
        ).pack(anchor="e", pady=(3, 0))

        self._section_label(root, "INTERFACE")
        interface_frame = tk.Frame(root, bg=self.COLORS["surface"], padx=16, pady=14)
        interface_frame.pack(fill=tk.X, padx=24, pady=(7, 16))

        tk.Label(
            interface_frame,
            text="Dispositivo",
            font=("Arial", 10, "bold"),
            fg=self.COLORS["text"],
            bg=self.COLORS["surface"],
        ).pack(side=tk.LEFT, padx=(0, 12))

        self.iface_var = tk.StringVar()
        self.iface_combo = ttk.Combobox(
            interface_frame,
            textvariable=self.iface_var,
            state="readonly",
            width=24,
            font=("Arial", 10),
        )
        self.iface_combo.pack(side=tk.LEFT)
        self._button(
            interface_frame,
            "Atualizar",
            self.load_interfaces,
            self.COLORS["surface_light"],
        ).pack(side=tk.LEFT, padx=(10, 0))

        self.status_label = tk.Label(
            interface_frame,
            text="Pronto",
            font=("Arial", 9),
            fg=self.COLORS["muted"],
            bg=self.COLORS["surface"],
        )
        self.status_label.pack(side=tk.RIGHT)

        self._section_label(root, "AÇÕES")
        actions = tk.Frame(root, bg=self.COLORS["background"])
        actions.pack(fill=tk.X, padx=24, pady=(7, 16))
        for column in range(4):
            actions.grid_columnconfigure(column, weight=1, uniform="action")

        self.action_buttons = []
        choices = [
            ("Parar NetworkManager", self.stop_network_manager, self.COLORS["danger"]),
            ("Parar processos Wi-Fi", self.kill_processes, self.COLORS["danger"]),
            ("↓  Descer interface", self.bring_down, self.COLORS["warning"]),
            ("Monitor", self.set_monitor_mode, self.COLORS["accent"]),
            ("Managed", self.set_managed_mode, self.COLORS["accent"]),
            ("↑  Subir interface", self.bring_up, self.COLORS["success"]),
            ("Reiniciar NetworkManager", self.restart_network_manager, self.COLORS["success"]),
            ("Teste rápido (iw)", self.test_interface, self.COLORS["surface_light"]),
        ]
        for index, (label, command, color) in enumerate(choices):
            button = self._button(actions, label, command, color, prominent=True)
            button.grid(
                row=index // 4,
                column=index % 4,
                sticky="ew",
                padx=5,
                pady=5,
                ipady=9,
            )
            self.action_buttons.append(button)

        self._section_label(root, "LOG DE ATIVIDADE")
        log_frame = tk.Frame(root, bg=self.COLORS["surface"], padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(7, 12))
        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            bg="#111827",
            fg=self.COLORS["text"],
            insertbackground=self.COLORS["text"],
            selectbackground="#334155",
            relief=tk.FLAT,
            font=("DejaVu Sans Mono", 9),
            padx=10,
            pady=9,
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_menu = tk.Menu(
            self.root,
            tearoff=False,
            bg=self.COLORS["surface"],
            fg=self.COLORS["text"],
            activebackground=self.COLORS["accent"],
            activeforeground=self.COLORS["background"],
        )
        self.log_menu.add_command(label="Copiar seleção", command=self.copy_log_selection)
        self.log_menu.add_command(label="Selecionar tudo", command=self.select_all_log)
        self.log_area.bind("<Button-3>", self.show_log_menu)
        self.log_area.bind("<Control-c>", self.copy_log_selection)
        self.log_area.bind("<Control-C>", self.copy_log_selection)

        footer = tk.Frame(root, bg=self.COLORS["background"])
        footer.pack(fill=tk.X, padx=24, pady=(0, 15))
        tk.Label(
            footer,
            text="TWC • Total Wireless Control",
            font=("Arial", 9),
            fg=self.COLORS["muted"],
            bg=self.COLORS["background"],
        ).pack(side=tk.LEFT)
        self._button(
            footer,
            "Limpar log",
            self.clear_log,
            self.COLORS["surface_light"],
        ).pack(side=tk.RIGHT)

        self.load_interfaces()

    def _section_label(self, parent, text):
        tk.Label(
            parent,
            text=text,
            font=("Arial", 9, "bold"),
            fg=self.COLORS["muted"],
            bg=self.COLORS["background"],
            anchor="w",
        ).pack(fill=tk.X, padx=26)

    def _button(self, parent, text, command, color, prominent=False):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="#0f172a" if color in (
                self.COLORS["success"],
                self.COLORS["warning"],
                self.COLORS["accent"],
            ) else self.COLORS["text"],
            activebackground=self.COLORS["text"],
            activeforeground=self.COLORS["background"],
            disabledforeground=self.COLORS["muted"],
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            font=("Arial", 9 if prominent else 10, "bold" if prominent else "normal"),
            padx=5 if prominent else 13,
            pady=8,
        )
        return button

    def _ui(self, callback, *args, **kwargs):
        self.root.after(0, lambda: callback(*args, **kwargs))

    def log(self, message):
        def append():
            self.log_area.insert(tk.END, message.rstrip() + "\n")
            self.log_area.see(tk.END)

        self._ui(append)

    def clear_log(self):
        self.log_area.delete("1.0", tk.END)

    def copy_log_selection(self, _event=None):
        try:
            selected_text = self.log_area.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return "break"
        self.root.clipboard_clear()
        self.root.clipboard_append(selected_text)
        return "break"

    def select_all_log(self, _event=None):
        self.log_area.tag_add(tk.SEL, "1.0", tk.END)
        self.log_area.mark_set(tk.INSERT, "1.0")
        self.log_area.see(tk.INSERT)
        self.log_area.focus_set()
        return "break"

    def show_log_menu(self, event):
        self.log_menu.tk_popup(event.x_root, event.y_root)

    def load_interfaces(self):
        interfaces = set()
        try:
            result = subprocess.run(
                ["iw", "dev"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            interfaces.update(
                match.group(1)
                for match in re.finditer(r"^\s*Interface\s+(\S+)", result.stdout, re.M)
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            self.log("[ERRO] Não foi possível consultar `iw dev`: {}".format(error))

        try:
            for name in os.listdir("/sys/class/net"):
                if os.path.exists("/sys/class/net/{}/wireless".format(name)):
                    interfaces.add(name)
        except OSError as error:
            self.log("[AVISO] Não foi possível listar interfaces: {}".format(error))

        values = sorted(interfaces)
        self.iface_combo["values"] = values
        if self.iface_var.get() not in values:
            self.iface_var.set(values[0] if values else "")
        self.log(
            "[INFO] Interfaces wireless: {}".format(", ".join(values) if values else "nenhuma detectada")
        )

    def get_iface(self):
        iface = self.iface_var.get().strip()
        if not iface:
            messagebox.showerror("Interface necessária", "Selecione uma interface wireless detectada.")
            return None
        return iface

    def _privileged_command(self, command):
        if os.geteuid() != 0:
            raise RuntimeError("O TWC precisa ser iniciado com privilégios administrativos.")
        return command

    def _run_commands(self, title, commands, privileged=True, stop_on_error=True):
        if self.busy:
            return

        self.busy = True
        self._ui(self.status_label.configure, text="Executando…", fg=self.COLORS["warning"])
        for button in self.action_buttons:
            self._ui(button.configure, state=tk.DISABLED)

        def worker():
            succeeded = True
            self.log("\n[INÍCIO] {}".format(title))
            for command in commands:
                actual_command = command
                if privileged:
                    try:
                        actual_command = self._privileged_command(command)
                    except RuntimeError as error:
                        self.log("[ERRO] {}".format(error))
                        succeeded = False
                        break

                displayed_command = ["sudo"] + command if privileged and os.geteuid() != 0 else command
                self.log("$ {}".format(" ".join(displayed_command)))
                try:
                    result = subprocess.run(
                        actual_command,
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=60,
                    )
                except subprocess.TimeoutExpired:
                    self.log("[ERRO] O comando excedeu o limite de 60 segundos.")
                    succeeded = False
                    if stop_on_error:
                        break
                    continue
                except OSError as error:
                    self.log("[ERRO] Não foi possível iniciar o comando: {}".format(error))
                    succeeded = False
                    if stop_on_error:
                        break
                    continue

                output = (result.stdout or "") + (result.stderr or "")
                for line in output.splitlines():
                    self.log(line)
                if result.returncode == 0:
                    self.log("[SUCESSO] Comando concluído.")
                else:
                    self.log("[ERRO] Comando finalizado com código {}.".format(result.returncode))
                    succeeded = False
                    if stop_on_error:
                        break

            self.log(
                "[SUCESSO] {}".format(title)
                if succeeded
                else "[AVISO] {} terminou com erro.".format(title)
            )
            self._ui(self._finish_action, succeeded)

        threading.Thread(target=worker, daemon=True).start()

    def _finish_action(self, succeeded):
        self.busy = False
        for button in self.action_buttons:
            button.configure(state=tk.NORMAL)
        self.status_label.configure(
            text="Pronto" if succeeded else "Ação concluída com erro",
            fg=self.COLORS["success"] if succeeded else self.COLORS["danger"],
        )

    def bring_up(self):
        iface = self.get_iface()
        if iface:
            self._run_commands("Subindo {}".format(iface), [["ip", "link", "set", iface, "up"]])

    def bring_down(self):
        iface = self.get_iface()
        if iface and messagebox.askyesno(
            "Descer interface",
            "Desconectar e desativar {} agora?".format(iface),
        ):
            self._run_commands("Descendo {}".format(iface), [["ip", "link", "set", iface, "down"]])

    def set_monitor_mode(self):
        iface = self.get_iface()
        if iface:
            commands = [
                ["ip", "link", "set", iface, "down"],
                ["iw", "dev", iface, "set", "type", "monitor"],
                ["ip", "link", "set", iface, "up"],
            ]
            self._run_commands("Configurando {} em modo monitor".format(iface), commands)

    def set_managed_mode(self):
        iface = self.get_iface()
        if iface:
            commands = [
                ["ip", "link", "set", iface, "down"],
                ["iw", "dev", iface, "set", "type", "managed"],
                ["ip", "link", "set", iface, "up"],
            ]
            self._run_commands("Restaurando {} para managed".format(iface), commands)

    def test_interface(self):
        iface = self.get_iface()
        if iface:
            self._run_commands(
                "Teste rápido da interface {}".format(iface),
                [["iw", "dev", iface, "info"]],
                privileged=False,
            )

    def kill_processes(self):
        if messagebox.askyesno(
            "Parar processos Wi-Fi",
            "O airmon-ng check kill pode interromper conexões e serviços de rede. Continuar?",
        ):
            self._run_commands(
                "Parando processos que interferem com o modo monitor",
                [["airmon-ng", "check", "kill"]],
            )

    def stop_network_manager(self):
        if messagebox.askyesno(
            "Parar NetworkManager",
            "Isso pode desconectar o computador da rede. Deseja parar o NetworkManager?",
        ):
            self._run_commands(
                "Parando NetworkManager",
                [["systemctl", "stop", "NetworkManager.service"]],
            )

    def restart_network_manager(self):
        if messagebox.askyesno(
            "Reiniciar NetworkManager",
            "A conexão de rede pode ser interrompida brevemente. Deseja reiniciar o NetworkManager?",
        ):
            self._run_commands(
                "Reiniciando NetworkManager",
                [["systemctl", "restart", "NetworkManager.service"]],
            )


if __name__ == "__main__":
    if os.geteuid() != 0:
        if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
            print(
                "TWC precisa de uma sessão gráfica ativa. Abra-o pelo menu "
                "ou por um terminal dentro da área de trabalho.",
                file=sys.stderr,
            )
            sys.exit(1)

        pkexec = shutil.which("pkexec")
        if not pkexec:
            print(
                "TWC precisa do PolicyKit (pkexec), mas ele não está instalado.",
                file=sys.stderr,
            )
            sys.exit(1)

        executable = os.path.realpath(sys.executable)
        script = os.path.realpath(__file__)
        env_command = shutil.which("env")
        if not env_command:
            print("TWC não encontrou o comando env necessário para iniciar.", file=sys.stderr)
            sys.exit(1)

        command = [pkexec, env_command]
        for name in (
            "DISPLAY",
            "XAUTHORITY",
            "WAYLAND_DISPLAY",
            "XDG_RUNTIME_DIR",
            "DBUS_SESSION_BUS_ADDRESS",
        ):
            value = os.environ.get(name)
            if value:
                command.append("{}={}".format(name, value))
        command.extend([executable, script] + sys.argv[1:])
        try:
            os.execv(pkexec, command)
        except OSError as error:
            print("TWC não conseguiu iniciar a autenticação gráfica: {}".format(error), file=sys.stderr)
            sys.exit(1)

    try:
        root = tk.Tk()
    except tk.TclError as error:
        print(
            "TWC não conseguiu acessar a tela gráfica (DISPLAY/XAUTHORITY): {}".format(error),
            file=sys.stderr,
        )
        sys.exit(1)
    app = TWCApp(root)
    root.mainloop()
