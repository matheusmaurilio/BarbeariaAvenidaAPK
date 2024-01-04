from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from datetime import datetime
import json



class BarberShopApp(App):
    def build(self):
        return BarberShopLayout()

class BarberShopLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(BarberShopLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.screen_manager = ScreenManager()

        # Primeira Página
        first_page = FirstPage()
        first_page.bind(on_press=self.switch_to_second_page)
        screen = Screen(name='First')
        screen.add_widget(first_page)
        self.screen_manager.add_widget(screen)

        # Segunda Página
        second_page = SecondPage()
        screen = Screen(name='Second')        
        screen.add_widget(second_page)
        self.screen_manager.add_widget(screen)

        # Terceira Página
        self.third_page = ThirdPage()  # Inicialize self.third_page
        self.load_clients_from_json()  # Carrega clientes do arquivo JSON
        screen = Screen(name='Third')        
        screen.add_widget(self.third_page)
        self.screen_manager.add_widget(screen)

        self.add_widget(self.screen_manager)

        # Inicia a verificação do horário
        Clock.schedule_once(self.check_scheduled_appointments, 0)

    def switch_to_second_page(self, instance):
        self.screen_manager.transition = SlideTransition(direction='left')
        self.screen_manager.current = 'Second'

    def switch_to_first_page(self):
        self.screen_manager.transition = SlideTransition(direction='right')
        self.screen_manager.current = 'First'

    def add_scheduled_client(self, client_name, selected_time):
        self.third_page.add_client(client_name, selected_time)
        self.third_page.save_client_to_json(client_name, selected_time)

    def load_clients_from_json(self):
        clients = self.third_page.load_clients_from_json()
        for client in clients:
            client_name = client["client_name"]
            selected_time = client["selected_time"]
            self.third_page.add_client(client_name, selected_time)

    def check_scheduled_appointments(self, dt):
        self.check_appointments(dt)
        Clock.schedule_once(self.check_scheduled_appointments, 10)# Chama a função a cada 10 segundos

    def check_appointments(self, dt):
        if not App.get_running_app().root:
            return  # Verificação de agendamentos interrompida quando a aplicação é fechada

        current_time = datetime.now().strftime("%H:%M")
        scheduled_clients = self.third_page.load_clients_from_json()

class FirstPage(Button):
    def __init__(self, **kwargs):
        super(FirstPage, self).__init__(**kwargs)
        self.text = 'Barbearia Avenida'
        self.font_size = 94
        self.background_color = (1, 0.84, 0, 1)  # Cor dourada
        self.size_hint = (1, 1)  # Tamanho menor

class SecondPage(BoxLayout):
    def __init__(self, **kwargs):
        super(SecondPage, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 20

        vertical_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        self.client_name_input = TextInput(hint_text='Nome do Cliente', multiline=False, size_hint=(1, 0.1))
        self.time_input = TextInput(hint_text='Digite o Horário', multiline=False, size_hint=(1, 0.1))
        self.schedule_button = Button(text='Agendar', on_press=self.schedule, background_color=(1, 0.84, 0, 1), size_hint=(1, 0.1))

        horizontal_layout = BoxLayout(orientation='horizontal', spacing=10)
        self.back_button = Button(text='Voltar', on_press=self.back_to_first_page, background_color=(1, 0.84, 0, 1), size_hint=(0.4, 0.1))
        self.next_button = Button(text='Próxima', on_press=self.switch_to_third_page, background_color=(1, 0.84, 0, 1), size_hint=(0.4, 0.1))

        horizontal_layout.add_widget(self.back_button)
        horizontal_layout.add_widget(self.next_button)

        vertical_layout.add_widget(self.client_name_input)
        vertical_layout.add_widget(self.time_input)
        vertical_layout.add_widget(self.schedule_button)
        vertical_layout.add_widget(horizontal_layout)

        self.add_widget(vertical_layout)

    def schedule(self, instance):
        client_name = self.client_name_input.text.strip()
        selected_time = self.time_input.text.strip()
        if client_name and selected_time:
            App.get_running_app().root.add_scheduled_client(client_name, selected_time)
            popup = Popup(title='Agendamento Confirmado',
                          size_hint=(None, None), size=(460, 190))
            popup.open()

    def back_to_first_page(self, instance):
        App.get_running_app().root.switch_to_first_page()

    def switch_to_third_page(self, instance):
        App.get_running_app().root.screen_manager.transition = SlideTransition(direction='left')
        App.get_running_app().root.screen_manager.current = 'Third'

class ThirdPage(BoxLayout):
    def __init__(self, **kwargs):
        super(ThirdPage, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 5
        self.padding = 5

        self.back_button = Button(text='Voltar', on_press=self.switch_to_second_page, background_color=(1, 0.84, 0, 1), size_hint=(0.20, 0.25))
        self.client_list_label = Label(text='Clientes Agendados:')
        self.client_list = BoxLayout(orientation='vertical', spacing=3)

        # Adiciona os widgets na ordem desejada
        self.add_widget(self.back_button)
        self.add_widget(self.client_list_label)
        self.add_widget(self.client_list)

    def switch_to_second_page(self, instance):
        App.get_running_app().root.screen_manager.transition = SlideTransition(direction='right')
        App.get_running_app().root.screen_manager.current = 'Second'

    def add_client(self, client_name, selected_time):
        new_label = Label(text=f'{client_name} -  Horário: {selected_time}')

        # Botão para remover o agendamento
        remove_button = Button(text='Remover', on_press=lambda instance: self.confirm_removal_popup(client_name, selected_time, new_label),
                               background_color=(1, 0.84, 0, 1), size_hint=(0.5, 0.7))

        # Adiciona o label e o botão ao layout
        client_layout = BoxLayout(orientation='horizontal', spacing=5)
        client_layout.add_widget(new_label)
        client_layout.add_widget(remove_button)

        self.client_list.add_widget(client_layout)

    def confirm_removal_popup(self, client_name, selected_time, label):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=''))
        
        # Botões de sim e não
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10)
        yes_button = Button(text='Sim', on_press=lambda instance: self.remove_client(client_name, selected_time, label, popup))
        no_button = Button(text='Não', on_press=lambda instance: popup.dismiss())
        buttons_layout.add_widget(yes_button)
        buttons_layout.add_widget(no_button)

        content.add_widget(buttons_layout)

        # Criação e exibição do Popup
        popup = Popup(title='Confirmação de Remoção', content=content, size_hint=(None, None), size=(460, 300))
        popup.open()

    def remove_client(self, client_name, selected_time, label, popup):
        # Obtém o layout pai do botão (BoxLayout que contém o Label e o Button)
        client_layout = label.parent

        # Remove o cliente do layout
        self.client_list.remove_widget(client_layout)

        # Remove o cliente do arquivo JSON
        self.remove_client_from_json(client_name, selected_time)

        # Fecha o Popup
        popup.dismiss()

    def remove_client_from_json(self, client_name, selected_time):
        data = {"client_name": client_name, "selected_time": selected_time}

        try:
            with open("clientes.json", "r") as file:
                clients = json.load(file)
        except FileNotFoundError:
            clients = []

        # Remove o cliente da lista
        clients = [client for client in clients if client != data]

        # Atualiza o arquivo JSON
        with open("clientes.json", "w") as file:
            json.dump(clients, file, indent=2)

    def save_client_to_json(self, client_name, selected_time):
        data = {"client_name": client_name, "selected_time": selected_time}

        try:
            with open("clientes.json", "r") as file:
                clients = json.load(file)
        except FileNotFoundError:
            clients = []

        clients.append(data)

        with open("clientes.json", "w") as file:
            json.dump(clients, file, indent=2)

    def load_clients_from_json(self):
        try:
            with open("clientes.json", "r") as file:
                clients = json.load(file)
        except FileNotFoundError:
            clients = []

        return clients

if __name__ == '__main__':
    BarberShopApp().run()
