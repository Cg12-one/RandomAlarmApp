import random
import datetime
import os
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

# 注册中文字体
if os.name == 'nt':
    font_path = 'C:/Windows/Fonts/simhei.ttf'
else:
    font_path = None

if font_path and os.path.exists(font_path):
    LabelBase.register(name='Chinese', fn_regular=font_path)
else:
    LabelBase.register(name='Chinese', fn_regular='Arial')

Window.size = (360, 640)

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 20
        
        self.title_label = Label(
            text='随机午休闹钟',
            font_name='Chinese',
            font_size='24sp',
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.title_label)
        
        input_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=50
        )
        
        self.min_input = TextInput(
            hint_text='最小分钟 (如 30)',
            input_filter='int',
            multiline=False,
            size_hint_x=0.5,
            font_name='Chinese',  # 添加字体
            font_size='16sp'
        )
        self.max_input = TextInput(
            hint_text='最大分钟 (如 60)',
            input_filter='int',
            multiline=False,
            size_hint_x=0.5,
            font_name='Chinese',  # 添加字体
            font_size='16sp'
        )
        
        input_layout.add_widget(self.min_input)
        input_layout.add_widget(self.max_input)
        self.add_widget(input_layout)
        
        self.result_label = Label(
            text='等待设定...',
            font_name='Chinese',
            font_size='28sp',
            color=(0, 1, 0, 1),
            size_hint_y=None,
            height=100
        )
        self.add_widget(self.result_label)
        
        self.status_label = Label(
            text='',
            font_name='Chinese',
            font_size='16sp',
            size_hint_y=None,
            height=40
        )
        self.add_widget(self.status_label)
        
        self.start_button = Button(
            text='开始随机闹钟',
            size_hint_y=None,
            height=50,
            background_color=(0, 0.5, 1, 1),
            font_name='Chinese',  # 添加字体
            font_size='18sp',
            color=(1, 1, 1, 1)  # 白色文字
        )
        self.add_widget(self.start_button)
        
        self.stop_button = Button(
            text='停止铃声',
            size_hint_y=None,
            height=50,
            background_color=(1, 0.2, 0.2, 1),
            font_name='Chinese',  # 添加字体
            font_size='18sp',
            color=(1, 1, 1, 1)  # 白色文字
        )
        self.add_widget(self.stop_button)

class RandomAlarmApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scheduled_event = None
        self.alarm_sound = None
        self.target_time_str = ""
        
    def build(self):
        self.title = '随机午休闹钟'
        layout = MainLayout()
        layout.start_button.bind(on_release=self.start_alarm)
        layout.stop_button.bind(on_release=self.stop_sound)
        return layout
    
    def start_alarm(self, instance):
        layout = self.root
        try:
            min_min = int(layout.min_input.text) if layout.min_input.text else 30
            max_min = int(layout.max_input.text) if layout.max_input.text else 60
        except ValueError:
            layout.status_label.text = "请输入有效数字"
            return
        
        if min_min >= max_min:
            layout.status_label.text = "最小时间必须小于最大时间"
            return
        
        if min_min < 1 or max_min > 120:
            layout.status_label.text = "时间范围应在 1-120 分钟之间"
            return
        
        if self.scheduled_event:
            self.scheduled_event.cancel()
        
        random_minutes = random.randint(min_min, max_min)
        now = datetime.datetime.now()
        target_time = now + datetime.timedelta(minutes=random_minutes)
        
        self.target_time_str = target_time.strftime("%H:%M:%S")
        layout.result_label.text = f"将在 {self.target_time_str} 响铃\n(休息 {random_minutes} 分钟)"
        layout.status_label.text = "闹钟已设定，请勿关闭应用"
        
        self._target_timestamp = target_time.timestamp()
        self.scheduled_event = Clock.schedule_interval(self.check_alarm, 1)
    
    def check_alarm(self, dt):
        if datetime.datetime.now().timestamp() >= self._target_timestamp:
            self.trigger_alarm()
            return False
    
    def trigger_alarm(self):
        layout = self.root
        layout.status_label.text = "⏰ 时间到！起床！"
        
        audio_path = os.path.join(os.path.dirname(__file__), 'alarm_sound.mp3')
        
        if self.alarm_sound is None:
            self.alarm_sound = SoundLoader.load(audio_path)
            if self.alarm_sound:
                self.alarm_sound.play()
            else:
                layout.status_label.text = "⏰ 时间到！起床！\n(音频文件加载失败)"
        else:
            self.alarm_sound.stop()
            self.alarm_sound.play()
    
    def stop_sound(self, instance):
        if self.alarm_sound:
            self.alarm_sound.stop()
        self.root.status_label.text = "已关闭闹钟"

if __name__ == '__main__':
    app = RandomAlarmApp()
    app.run()