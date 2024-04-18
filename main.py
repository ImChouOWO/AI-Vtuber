import os
import torch
from openvoice import se_extractor
from openvoice.api import BaseSpeakerTTS, ToneColorConverter
from llama_cpp import Llama
from playsound import playsound
import requests
from bs4 import BeautifulSoup


class AiVtuber():
    def __init__(self) -> None:
        self.name ="test"
        self.mistral_prompt = ""


    def text_generate(self,text_input):
        LLM = Llama(
            model_path="C:/Users/Owner/Desktop/python/ai_vtuber/main/model/mistral-7b-instruct-v0.1.Q5_K_M.gguf",
            n_ctx=2048,
            verbose=True)

        # create a text prompt
        prompt = f"role:Your name is Mia, and you are a cheerful female college student who enjoys reading and just speak english, cooking, and video games.Q: {text_input} A:"

        # generate a response (takes several seconds)
        output = LLM(prompt)

        # display the response

        print(f"---\nLLM output :{output['choices'][0]['text']}\n---") 
        self.voice_generate(output["choices"][0]["text"])

    def play_audio(self,voice_status:bool):
        if not voice_status:
            print("audio file load fail")
            return
        
        playsound("C:/Users/Owner/Desktop/python/ai_vtuber/main/outputs/tmp_out_put.wav")


    def voice_generate(self,text_prompt):

        # initialze the parameter
        
        
        try:
            ckpt_base = 'checkpoints/base_speakers/EN'
            ckpt_converter = 'checkpoints/converter'
            device="cuda:0" if torch.cuda.is_available() else "cpu"
            output_dir = 'outputs'

            base_speaker_tts = BaseSpeakerTTS(f'{ckpt_base}/config.json', device=device)
            base_speaker_tts.load_ckpt(f'{ckpt_base}/checkpoint.pth')

            tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
            tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

            os.makedirs(output_dir, exist_ok=True)

            # pre-trainde tone
            source_se = torch.load(f'{ckpt_base}/en_default_se.pth').to(device)

            # few-shot resources
            reference_speaker = 'resources/clone_voice.mp3'

            target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, target_dir='processed', vad=True)
            save_path = f'{output_dir}/output_en_default.wav'

            base_speaker_tts = BaseSpeakerTTS(f'{ckpt_base}/config.json', device=device)
            base_speaker_tts.load_ckpt(f'{ckpt_base}/checkpoint.pth')

            source_se = torch.load(f'{ckpt_base}/en_style_se.pth').to(device)
            save_path = f'{output_dir}/tmp_out_put.wav'

            # Run the base speaker tts
            text = f"{text_prompt}"
            src_path = f'{output_dir}/tmp.wav'
            base_speaker_tts.tts(text, src_path, speaker='friendly', language='English', speed=1)

            # Run the tone color converter
            encode_message = "@MyShell"
            tone_color_converter.convert(
                audio_src_path=src_path, 
                src_se=source_se, 
                tgt_se=target_se, 
                output_path=save_path,
                message=encode_message)
            
            voice_status = True
            
        except:

            voice_status = False
            print("voice generate fail")
        
        self.play_audio(voice_status)





if __name__ == "__main__":
    ai_vtuber =AiVtuber()
   
    while True:
        print("---type 'out' to break session---")
        
        text_input = input("ask Mia : ")
        if text_input == "out":
            break
        ai_vtuber.text_generate(text_input)


