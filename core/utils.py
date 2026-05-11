import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import os
import shutil
import re
from django.conf import settings
from moviepy.video.io.VideoFileClip import VideoFileClip

try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("[Warning] SpeechRecognition not available. Audio transcription will be skipped.")

try:
    import tensorflow as tf
    import tensorflow_hub as hub
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("[Warning] TensorFlow/Hub not available. Style transfer will use simple effect.")

class ComicGenerator:
    def __init__(self, style_path=None, model_type="tiny", frame_interval=30, target_size=(512, 288)):
        """
        Initialize the Comic Generator with configuration parameters
        """
        # Use default style path relative to static files if not provided
        if style_path is None:
            self.style_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'styles', 'comic_style.jpg')
        else:
            self.style_path = style_path
            
        self.model_type = model_type
        self.frame_interval = frame_interval
        self.target_size = target_size
        self.style_model = None
        self.style_image = None
        
        # Add ffmpeg to path if configured in settings, otherwise assume it's in system PATH
        if hasattr(settings, 'FFMPEG_PATH'):
             os.environ['PATH'] += f";{settings.FFMPEG_PATH}"
    
    def check_ffmpeg(self):
        """Check if ffmpeg is installed and available in PATH"""
        if not shutil.which("ffmpeg"):
            pass
    
    def extract_audio_from_video(self, video_path):
        try:
            video = VideoFileClip(video_path)
            audio = video.audio
            return audio
        except Exception as e:
            print(f"[Error] Audio extraction failed: {e}")
            return None
    
    def audio_to_text(self, audio):
        if not audio:
            return []
        
        temp_audio_path = os.path.join(settings.MEDIA_ROOT, 'temp_audio.wav')
        try:
            # Write audio to wav file
            audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
            
            # Configure Gemini
            import google.generativeai as genai
            genai.configure(api_key=os.environ.get('GEMINI_API_KEY', ''))
            
            # Upload file
            myfile = genai.upload_file(temp_audio_path)
            
            # Generate content
            model = genai.GenerativeModel("gemini-1.5-flash")
            result = model.generate_content([myfile, "Transcribe this audio. Return only the text."])
            
            text = result.text
            
            # Split into sentences
            sentences = re.split(r'(?<=[.!?]) +', text)
            return sentences
            
        except Exception as e:
            print(f"[Error] Gemini transcription failed: {e}")
            return []
        finally:
            if os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                except:
                    pass
    
    def extract_frames(self, video_path):
        cap = cv2.VideoCapture(video_path)
        frames = []
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if count % self.frame_interval == 0:
                resized_frame = cv2.resize(frame, self.target_size)
                frames.append(resized_frame)
            count += 1
        cap.release()
        return frames
    
    def load_style_model_and_image(self):
        if not TF_AVAILABLE:
            self.style_model = None
            return

        print("[Info] Loading style model and style image...")
        try:
            # Load from local cache or download
            # Using a specific handle or path if you want to bundle the model
            self.style_model = hub.load('https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2')
        except Exception as e:
            print(f"[Warning] Could not load style model: {e}")
            self.style_model = None
            return

        if os.path.exists(self.style_path):
            self.style_image = cv2.imread(self.style_path)
            if self.style_image is not None:
                self.style_image = cv2.cvtColor(self.style_image, cv2.COLOR_BGR2RGB)
                self.style_image = cv2.resize(self.style_image, (256, 256))
                self.style_image = self.style_image.astype(np.float32)[np.newaxis, ...] / 255.
            else:
                self.style_image = None
        else:
            self.style_image = None

    def apply_comic_filter(self, frame):
        if self.style_model is None or self.style_image is None:
            return self.apply_simple_comic_effect(frame)
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = frame_rgb.astype(np.float32)[np.newaxis, ...] / 255.
        
        stylized = self.style_model(tf.constant(frame_rgb), tf.constant(self.style_image))[0]
        stylized = np.array(stylized) * 255
        stylized = stylized.astype(np.uint8)
        
        return cv2.cvtColor(stylized[0], cv2.COLOR_RGB2BGR)
    
    def apply_simple_comic_effect(self, frame):
        if frame.shape[:2] != self.target_size:
            frame = cv2.resize(frame, self.target_size)
        
        frame = cv2.medianBlur(frame, 7)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY, 9, 9
        )
        color = cv2.bilateralFilter(frame, 9, 250, 250)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        cartoon = cv2.bitwise_and(color, edges)
        return cartoon

    def trim_text(self, text, max_length=100):
        return text if len(text) <= max_length else text[:max_length] + "..."
    
    def add_speech_bubble(self, image, text, position='top-right'):
        text = self.trim_text(text)
        img = Image.fromarray(image)
        draw = ImageDraw.Draw(img, "RGBA")
        img_w, img_h = img.size
        bubble_width = int(img_w * 0.5)
        bubble_height = int(img_h * 0.2)
        padding = 10
        positions = {
            'top-left': (padding, padding),
            'top-right': (img_w - bubble_width - padding, padding),
            'bottom-left': (padding, img_h - bubble_height - padding),
            'bottom-right': (img_w - bubble_width - padding, img_h - bubble_height - padding)
        }
        bubble_x, bubble_y = positions.get(position, (padding, padding))
        bubble_color = (255, 255, 255, 200)
        outline_color = (0, 0, 0, 255)
        radius = 10
        draw.rounded_rectangle(
            [bubble_x, bubble_y, bubble_x + bubble_width, bubble_y + bubble_height],
            radius=radius, 
            fill=bubble_color, 
            outline=outline_color
        )
        try:
            font = ImageFont.truetype("Arial", 14)
        except IOError:
            font = ImageFont.load_default()
        text_color = (0, 0, 0, 255)
        text_padding = 15
        draw.text(
            (bubble_x + text_padding, bubble_y + text_padding),
            text,
            font=font,
            fill=text_color
        )
        return np.array(img)
    
    def generate_comic_from_video(self, video_path, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        self.check_ffmpeg()
        
        audio_path = self.extract_audio_from_video(video_path)
        captions = self.audio_to_text(audio_path)
        frames = self.extract_frames(video_path)
        self.load_style_model_and_image()
        
        output_paths = []
        positions = ['top-right', 'top-left', 'bottom-right', 'bottom-left']
        
        for i, frame in enumerate(frames):
            if len(captions) > 0:
                caption_index = int((i / len(frames)) * len(captions))
                caption = captions[min(caption_index, len(captions) - 1)]
            else:
                caption = ""
            
            stylized = self.apply_comic_filter(frame)
            
            position = positions[i % 4]
            if caption and caption.strip():
                final_image = self.add_speech_bubble(stylized, caption, position)
            else:
                final_image = stylized
            
            panel_filename = f"panel_{i:03d}.jpg"
            panel_path = os.path.join(output_dir, panel_filename)
            cv2.imwrite(panel_path, final_image)
            output_paths.append(panel_filename) # Return relative filenames for DB
        
        return output_paths
