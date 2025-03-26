import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer

class PlaylistError(Exception):
    """Custom exception for playlist-related errors"""

    pass


class PlaylistManager:
    def __init__(self):
        # Initialize the playlist dictionary
        self.playlist = {}

    def add_song(self, title, artist, genre):
        """
        Add a new song to the playlist with exception handling
        """
        try:
            # Validate input types
            if not all(isinstance(x, str) for x in [title, artist, genre]):
                raise TypeError("Title, artist, and genre must be strings")

            # Trim whitespace
            title = title.strip()
            artist = artist.strip()
            genre = genre.strip()

            # Check for empty strings
            if not title or not artist or not genre:
                raise ValueError("Title, artist, and genre cannot be empty")

            # Check for duplicate song
            if title in self.playlist:
                raise PlaylistError(f"Song '{title}' already exists!")

            # Add song to playlist
            self.playlist[title] = {"artist": artist, "genre": genre}
            return f"Song '{title}' added successfully!"

        except (TypeError, ValueError, PlaylistError) as e:
            return str(e)

    def view_playlist(self):
        """
        Generate a formatted view of the playlist with exception handling
        """
        try:
            # Check if playlist is empty
            if not self.playlist:
                raise PlaylistError("Playlist is empty")

            playlist_view = ""
            for title, details in self.playlist.items():
                playlist_view += f"Title: {title}\n"
                playlist_view += f"Artist: {details['artist']}\n"
                playlist_view += f"Genre: {details['genre']}\n\n"

            return playlist_view

        except PlaylistError as e:
            return str(e)

    def update_song(self, title, artist=None, genre=None):
        """
        Update artist or genre of a specific song with exception handling
        """
        try:
            # Validate input types
            if not isinstance(title, str):
                raise TypeError("Title must be a string")

            # Trim whitespace
            title = title.strip()

            # Check if song exists
            if title not in self.playlist:
                raise PlaylistError(f"Song '{title}' not found in playlist!")

            # Validate and update artist if provided
            if artist is not None:
                if not isinstance(artist, str):
                    raise TypeError("Artist must be a string")
                artist = artist.strip()
                if artist:
                    self.playlist[title]["artist"] = artist

            # Validate and update genre if provided
            if genre is not None:
                if not isinstance(genre, str):
                    raise TypeError("Genre must be a string")
                genre = genre.strip()
                if genre:
                    self.playlist[title]["genre"] = genre

            return f"Song '{title}' updated successfully!"

        except (TypeError, PlaylistError) as e:
            return str(e)

    def delete_song(self, title):
        """
        Remove a song from the playlist with exception handling
        """
        try:
            # Validate input type
            if not isinstance(title, str):
                raise TypeError("Title must be a string")

            # Trim whitespace
            title = title.strip()

            # Check if song exists
            if title not in self.playlist:
                raise PlaylistError(f"Song '{title}' not found in playlist!")

            # Delete the song
            del self.playlist[title]
            return f"Song '{title}' deleted successfully!"

        except (TypeError, PlaylistError) as e:
            return str(e)


def main():
    # Initialize GLFW
    if not glfw.init():
        return

    # Get primary monitor and video mode
    primary_monitor = glfw.get_primary_monitor()
    video_mode = glfw.get_video_mode(primary_monitor)

    # Calculate center position for window
    window_width = 800
    window_height = 600
    pos_x = (video_mode.size.width - window_width) // 2
    pos_y = (video_mode.size.height - window_height) // 2

    # Set essential window hints
    glfw.window_hint(glfw.DECORATED, False)
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, False)
    glfw.window_hint(glfw.FOCUSED, True)
    glfw.window_hint(glfw.RESIZABLE, False)
    glfw.window_hint(glfw.DOUBLEBUFFER, True)
    glfw.window_hint(glfw.SAMPLES, 4)

    # Create window with fixed size
    window = glfw.create_window(800, 600, "Music Playlist Manager", None, None)
    if not window:
        glfw.terminate()
        return

    # Center the window
    glfw.set_window_pos(window, pos_x, pos_y)

    # Make the window's context current
    glfw.make_context_current(window)

    # Enable vsync
    glfw.swap_interval(1)

    # Initialize ImGui
    imgui.create_context()
    impl = GlfwRenderer(window)

    # Create playlist manager
    playlist_manager = PlaylistManager()

    # Input buffers - use empty strings directly
    input_buffers = {
        'title': [""],
        'artist': [""],
        'genre': [""],
        'message': [""],
        'new_artist': [""],
        'new_genre': [""],
        'selected_song': [""]
    }

    # Window dragging variables
    window_pos = list(glfw.get_window_pos(window))
    is_dragging = [False]
    drag_start = [0, 0]

    # Main loop
    while not glfw.window_should_close(window):
        glfw.poll_events()  # Move to start of frame
        impl.process_inputs()

        # Get framebuffer size for proper scaling
        fb_width, fb_height = glfw.get_framebuffer_size(window)
        gl.glViewport(0, 0, fb_width, fb_height)
        gl.glEnable(gl.GL_MULTISAMPLE)  # Enable MSAA properly

        # Clear and setup frame
        gl.glClearColor(0.15, 0.15, 0.15, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        # Update only when needed
        if glfw.get_window_attrib(window, glfw.ICONIFIED) == 0:
            imgui.new_frame()

            # Get window size for ImGui
            win_width, win_height = glfw.get_window_size(window)

            # Main window - set to use full window size
            imgui.set_next_window_size(win_width, win_height)
            imgui.set_next_window_position(0, 0)
            window_open = True
            _, window_open = imgui.begin(
                "Music Playlist Manager",
                True,
                imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE,
            )

            if not window_open:
                glfw.set_window_should_close(window, True)

            # Make only the title bar draggable
            title_bar_height = imgui.get_frame_height()

            # Check if mouse is in title bar area
            mouse_pos_x, mouse_pos_y = imgui.get_mouse_pos()
            title_bar_hovered = (
                0 <= mouse_pos_x <= win_width
                and 0 <= mouse_pos_y <= title_bar_height
                and imgui.is_window_hovered()
            )

            # Handle dragging start
            if title_bar_hovered and imgui.is_mouse_clicked(0):
                is_dragging[0] = True
                cursor_pos = glfw.get_cursor_pos(window)
                window_pos[0], window_pos[1] = glfw.get_window_pos(window)
                drag_start[0] = cursor_pos[0] - window_pos[0]
                drag_start[1] = cursor_pos[1] - window_pos[1]

            if is_dragging[0]:
                if imgui.is_mouse_down(0):
                    cursor_pos = glfw.get_cursor_pos(window)
                    new_x = int(cursor_pos[0] - drag_start[0])
                    new_y = int(cursor_pos[1] - drag_start[1])
                    glfw.set_window_pos(window, new_x, new_y)
                else:
                    is_dragging[0] = False
                    window_pos[0], window_pos[1] = glfw.get_window_pos(window)

            imgui.separator()

            # Add Song Section
            imgui.text("Add New Song")

            # Input fields section
            _, input_buffers['title'][0] = imgui.input_text("Title", input_buffers['title'][0], 255)
            _, input_buffers['artist'][0] = imgui.input_text("Artist", input_buffers['artist'][0], 255)
            _, input_buffers['genre'][0] = imgui.input_text("Genre", input_buffers['genre'][0], 255)

            # Add Song Button
            if imgui.button("Add Song"):
                input_buffers['message'][0] = playlist_manager.add_song(
                    input_buffers['title'][0], input_buffers['artist'][0], input_buffers['genre'][0]
                )
                # Clear input fields after adding
                input_buffers['title'][0] = ""
                input_buffers['artist'][0] = ""
                input_buffers['genre'][0] = ""

            # Display Message
            color = (1.0, 0.0, 0.0) if "error" in input_buffers['message'][0].lower() else (0.0, 1.0, 0.0)
            imgui.text_colored(input_buffers['message'][0], color[0], color[1], color[2])

            # Adjust playlist view size based on window height
            playlist_height = win_height - 250  # Reserve space for other elements
            imgui.begin_child("Playlist", 0, playlist_height, True)
            if playlist_manager.playlist:
                # Create a list of songs to delete
                to_delete = []

                # Check if clicking empty space in the playlist view
                if (
                    imgui.is_window_hovered()
                    and imgui.is_mouse_clicked(0)
                    and not imgui.is_any_item_hovered()
                ):
                    input_buffers['selected_song'][0] = ""

                for title, details in playlist_manager.playlist.items():
                    # Handle selection and right-click menu
                    is_clicked = imgui.selectable(
                        f"Title: {title}\nArtist: {details['artist']}\nGenre: {details['genre']}\n",
                        input_buffers['selected_song'][0] == title,
                    )[0]

                    # Update selection on left click
                    if is_clicked:
                        input_buffers['selected_song'][0] = title

                    # Handle context menu with popup flags
                    if imgui.begin_popup_context_item(
                        f"context_menu_{title}", imgui.POPUP_MOUSE_BUTTON_RIGHT
                    ):
                        input_buffers['selected_song'][0] = title  # Update selection when menu opens
                        imgui.text(f"Editing: {title}")
                        imgui.separator()

                        _, input_buffers['new_artist'][0] = imgui.input_text(
                            "New Artist##context", input_buffers['new_artist'][0], 255
                        )
                        _, input_buffers['new_genre'][0] = imgui.input_text(
                            "New Genre##context", input_buffers['new_genre'][0], 255
                        )

                        if imgui.button("Update##context"):
                            # Only update if there's input in either field
                            if input_buffers['new_artist'][0].strip() or input_buffers['new_genre'][0].strip():
                                input_buffers['message'][0] = playlist_manager.update_song(
                                    title,
                                    artist=input_buffers['new_artist'][0] if input_buffers['new_artist'][0].strip() else None,
                                    genre=input_buffers['new_genre'][0] if input_buffers['new_genre'][0].strip() else None,
                                )
                                input_buffers['new_artist'][0] = ""
                                input_buffers['new_genre'][0] = ""
                                imgui.close_current_popup()
                            else:
                                input_buffers['message'][0] = "Error: At least one field must be filled"

                        if imgui.button("Delete##context"):
                            to_delete.append(
                                title
                            )  # Mark for deletion instead of deleting immediately
                            input_buffers['new_artist'][0] = ""
                            input_buffers['new_genre'][0] = ""
                            imgui.close_current_popup()

                        if imgui.button("Cancel##context"):
                            input_buffers['new_artist'][0] = ""
                            input_buffers['new_genre'][0] = ""
                            imgui.close_current_popup()

                        imgui.end_popup()

                # Handle deletions after the loop
                for title in to_delete:
                    input_buffers['message'][0] = playlist_manager.delete_song(title)
                    if input_buffers['selected_song'][0] == title:
                        input_buffers['selected_song'][0] = ""
            else:
                imgui.text("Playlist is empty")
            imgui.end_child()

            imgui.end()

            imgui.render()
            impl.render(imgui.get_draw_data())
            glfw.swap_buffers(window)

        # Poll events at end of frame
        glfw.poll_events()

    # Cleanup
    impl.shutdown()
    glfw.terminate()


# Run the application
if __name__ == "__main__":
    main()
