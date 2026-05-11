from django.shortcuts import render, redirect, get_object_or_404
from .models import VideoUpload, ComicPanel
from .forms import VideoUploadForm
from .utils import ComicGenerator
import os
from django.conf import settings
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# Configure Gemini (ensure key is set)
genai.configure(api_key="AIzaSyBBS6Nh_b2BTciQ2XWdnAKj1xdc8X1HBYA")

def ziatalks_setup(request):
    if request.method == 'POST':
        youtube_url = request.POST.get('youtube_url')
        print(f"[DEBUG] Received YouTube URL: {youtube_url}")
        
        # Simple validation
        if not youtube_url or not ('youtube.com' in youtube_url or 'youtu.be' in youtube_url):
            return render(request, 'core/ziatalks_setup.html', {'error': "Please enter a valid YouTube URL"})
        
        try:
            # Extract video ID
            if "v=" in youtube_url:
                video_id = youtube_url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in youtube_url:
                video_id = youtube_url.split("youtu.be/")[1].split("?")[0]
            else:
                video_id = youtube_url.split("/")[-1].split("?")[0]
            
            print(f"[DEBUG] Video ID: {video_id}")
            
            # Ensure media directory exists
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            
            # Download video using yt-dlp
            import yt_dlp
            
            video_filename = f'temp_video_{video_id}.mp4'
            video_path = os.path.join(settings.MEDIA_ROOT, video_filename)
            
            ydl_opts = {
                'format': 'worst[ext=mp4]/worst',  # Download smallest MP4 for faster processing
                'outtmpl': video_path,
                'quiet': False,
                'no_warnings': False,
            }
            
            print("[DEBUG] Downloading video...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            print(f"[DEBUG] Video downloaded to: {video_path}")
            print("[DEBUG] Uploading to Gemini...")
            
            # Upload to Gemini
            video_file = genai.upload_file(path=video_path)
            
            print(f"[DEBUG] Uploaded file: {video_file.name}")
            
            # Wait for file to be processed
            import time
            print("[DEBUG] Waiting for file to be processed...")
            max_wait = 60  # Maximum 60 seconds
            wait_time = 0
            while video_file.state.name == "PROCESSING" and wait_time < max_wait:
                time.sleep(2)
                video_file = genai.get_file(video_file.name)
                wait_time += 2
                print(f"[DEBUG] File state: {video_file.state.name}")
            
            if video_file.state.name != "ACTIVE":
                raise Exception(f"File processing failed. State: {video_file.state.name}")
            
            print("[DEBUG] File is ready!")
            
            # Store file reference in session
            request.session['gemini_video_file'] = video_file.name
            request.session['chat_history'] = []
            
            print("[DEBUG] Redirecting to chat")
            return redirect('ziatalks_chat')
            
        except Exception as e:
            print(f"[ERROR] {e}")
            import traceback
            traceback.print_exc()
            return render(request, 'core/ziatalks_setup.html', {'error': f"Could not process video: {str(e)}"})
            
    return render(request, 'core/ziatalks_setup.html')

def ziatalks_chat(request):
    if 'gemini_video_file' not in request.session:
        return redirect('ziatalks_setup')
    
    chat_history = request.session.get('chat_history', [])
    video_file_name = request.session['gemini_video_file']
    
    if request.method == 'POST':
        user_message = request.POST.get('message')
        chat_history.append({'role': 'user', 'text': user_message})
        
        # Generate response using Gemini with uploaded video
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Get the file reference
        video_file = genai.get_file(video_file_name)
        
        # Create a conversational prompt
        prompt = f"""You are ZiaTalks, a friendly and helpful AI assistant. 

The user asks: {user_message}

Please provide a helpful, conversational answer based on the video content. Keep your response:
- Natural and friendly (like talking to a friend)
- Clear and easy to understand
- Concise but complete
- Without phrases like "According to the video" or "The video mentions" - just answer naturally

Answer:"""
        
        try:
            response = model.generate_content([video_file, prompt])
            bot_reply = response.text
        except Exception as e:
            bot_reply = f"Error: {str(e)}"
            print(f"[ERROR] Gemini error: {e}")
            import traceback
            traceback.print_exc()
            
        chat_history.append({'role': 'bot', 'text': bot_reply})
        request.session['chat_history'] = chat_history
        
    return render(request, 'core/ziatalks_chat.html', {'chat_history': chat_history})

def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            return redirect('process_video', video_id=video.id)
    else:
        form = VideoUploadForm()
    return render(request, 'core/index.html', {'form': form})

def process_video(request, video_id):
    video = get_object_or_404(VideoUpload, id=video_id)
    
    if not video.processed:
        generator = ComicGenerator()
        video_path = video.video_file.path
        output_dir = os.path.join(settings.MEDIA_ROOT, 'comics', str(video.id))
        
        # Generate panels
        panel_filenames = generator.generate_comic_from_video(video_path, output_dir)
        
        # Save to DB
        for i, filename in enumerate(panel_filenames):
            ComicPanel.objects.create(
                video=video,
                image_file=f"comics/{video.id}/{filename}",
                panel_number=i
            )
        
        video.processed = True
        video.save()
        
    return redirect('result', video_id=video.id)

def result(request, video_id):
    video = get_object_or_404(VideoUpload, id=video_id)
    panels = video.panels.all()
    return render(request, 'core/result.html', {'video': video, 'panels': panels})
