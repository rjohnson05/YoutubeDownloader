import os
import validators
from moviepy.editor import VideoFileClip, AudioFileClip
from pytube import YouTube


class YoutubeDownloader:
    def __init__(self, url=None):
        self.url = url
        self.youtube_object = None
        self.desired_media = "v"
        self.res = "720"
        self.save_title = None
        self.save_location = None

    # Gets a valid YouTube video URL from the user
    def get_valid_url(self):
        """
        Gets a valid URL from the user. This URL must be to a working YouTube video in order to be considered valid.
        """
        correct_url = False
        while not correct_url:
            url_input = input("\nEnter the URL of the video you wish to download: ")
            # Confirms that the given URL is to a legit YouTube video
            if validators.url(url_input) and url_input.__contains__("youtube.com"):
                correct_url = True
                self.url = url_input
                self.youtube_object = YouTube(self.url, on_progress_callback=self.get_progress)
            else:
                print("\nThe provided URL wasn't valid. Please try again.")

    def get_desired_media(self):
        """
        Determines whether the user wishes to download the YouTube video or the audio from the video.
        """
        valid_media_input = False
        while not valid_media_input:
            desired_media = input("Would you like to download the video or just audio? (V/A)")
            if desired_media.lower() == "v" or desired_media.lower() == "a":
                valid_media_input = True
                self.desired_media = desired_media
            else:
                print("\nYour input was invalid. Please enter 'V' for video or 'A' for audio.")

    def get_res(self):
        """
        Gets the resolution the user wants to download the YouTube video in.
        """
        yt = self.youtube_object
        valid_res_input = False
        while not valid_res_input:
            res_list = ["144", "240", "360", "480", "720", "1080"]
            res_input = input(f"Which resolution would you like to download your video in? ({res_list})")
            if res_input in res_list:
                if len(yt.streams.filter(res=f"{res_input}p")) > 0:
                    valid_res_input = True
                    self.res = res_input
                else:
                    print(
                        "\nThe provided resolution isn't provided for this video. Please pick a different resolution.")
                if res_input == "1080":
                    download = input("NOTE: Downloading this video in HD will take considerably longer than other "
                                     "resolutions. Would you like to continue with this resolution? (Y/N)")
                    if download.lower() == "n":
                        valid_res_input = False
            else:
                print("\nThe provided resolution is invalid. Please try again.")

    def get_save_title(self):
        """
        Asks the user what they want the downloaded file to be named.
        """
        title_input = input("What would you like the name of your downloaded file to be?")
        self.save_title = title_input

    def get_save_location(self):
        """
        Asks the user where they want to save the downloaded file.
        """
        valid_location_input = False
        while not valid_location_input:
            location_input = input("Where would you like to save this file?")
            if os.path.exists(location_input):
                valid_location_input = True
                self.save_location = location_input
            else:
                print("\nThat file location is invalid. Please enter a valid file location.")

    def download_video(self, yt):
        """
        Downloads a YouTube video using the designated YouTube object. This video is saved to a file location
        designated by the user in .mp4 format. If an HD(1080p) is downloaded, the video and audio are downloaded
        separately and then combined before being saved at the designated file location.
        :param yt: YouTube object that contains the available stream options for the designated URL
        """
        if self.desired_media == "v":
            desired_video_stream = yt.streams.filter(file_extension="mp4", res=f"{self.res}p")[0]
            # If HD is desired for the video, the audio will be downloaded separately. As such, the video file is
            # stored in a location different from that designated by the user, in order to avoid confusion during the
            # downloading process.
            if self.res == "1080":
                print("Preparing for Download...")
                desired_video_stream.download(filename=f"{self.save_title}.mp4")  # Downloads HD video w/o audio

                # Downloads the audio file for the video
                desired_audio_stream = yt.streams.filter(only_audio=True)[0]
                desired_audio_stream.download(filename=f"{self.save_title}_audio.mp4")

                # Pieces together the separate video and audio files and saves the final video to the file location
                # designated by the user
                video_clip = VideoFileClip(f"{self.save_title}.mp4")
                audio_clip = AudioFileClip(f"{self.save_title}_audio.mp4")
                final_clip = video_clip.set_audio(audio_clip)
                final_clip.write_videofile(f"{self.save_location}/{self.save_title}.mp4")

                # Delete the original video & audio files used to create the final file
                os.remove(f"{self.save_title}.mp4")
                os.remove(f"{self.save_title}_audio.mp4")
            else:
                # Downloads the video if HD is not desired or available
                print("Downloading...")
                desired_video_stream.download(output_path=self.save_location, filename=f"{self.save_title}.mp4")

    def download_audio(self, yt):
        """
        Downloads audio from a YouTube video using the designated YouTube object. This audio is saved to a file location
        designated by the user in .mp3 format.
        :param yt: YouTube object that contains the available stream options for the designated URL
        """
        if self.desired_media == "a":
            desired_audio_stream = yt.streams.filter(only_audio=True)[0]
            desired_audio_stream.download(output_path=self.save_location, filename=f"{self.save_title}.mp3")

    def get_progress(self, stream, chunk, bytes_remaining):
        """
        Prints the progress of the current download
        :param stream: Stream object being downloaded
        :param chunk: Group of bytes currently being downloaded
        :param bytes_remaining: Integer indicating the number of bytes still to be downloaded for the current file being downloaded
        """
        if self.res == "1080":
            print(f'Download Setup: {round((1 - bytes_remaining / stream.filesize) * 100)}% done...')
        else:
            print(f'Downloading: {round((1 - bytes_remaining / stream.filesize) * 100)}% done...')


if __name__ == "__main__":
    print("Welcome to Ryan's Youtube Downloader!")
    downloader = YoutubeDownloader()

    quitting = False
    while not quitting:
        downloader.get_valid_url()
        downloader.get_desired_media()
        downloader.get_save_title()
        downloader.get_save_location()

        yt_object = downloader.youtube_object
        if downloader.desired_media == "v":
            downloader.get_res()
            downloader.download_video(yt_object)
        else:
            downloader.download_audio(yt_object)

        repeat = input("Would you like to download another video? (Y/N)")
        if repeat.lower() == "n":
            quitting = True
            print("\nThanks for using Ryan's YouTube Downloader!")
