elif event.type == SDL_MOUSEBUTTONUP:
# get position of click
mouse_x, mouse_y = ctypes.c_int(), ctypes.c_int()
SDL_GetMouseState(mouse_x, mouse_y)
