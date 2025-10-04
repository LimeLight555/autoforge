#py -m pip install numpy, pulp, opencv-python
from time import sleep
from ctypes import Structure, WinDLL, create_string_buffer, sizeof, byref, pointer
from ctypes.wintypes import DWORD, LONG, WORD, RECT
from numpy import frombuffer, uint8, all, any, where, max, min, ceil, zeros, array
from cv2 import inRange, findNonZero, dilate, connectedComponentsWithStats, CC_STAT_LEFT, CC_STAT_TOP
from pulp import LpProblem, LpMinimize, LpVariable, LpInteger, lpSum, PULP_CBC_CMD
WINDOW_TITLE = 'HardRock TerraFirmaCraft 3 - 1.6.2 - //1.18.2//'
CLICK_DELAY, FORGING_STEPS = 0.025, {"LIGHT_HIT":-3,"MEDIUM_HIT":-6,"HARD_HIT":-9,"DRAW":-15,"PUNCH":2,"BEND":7,"UPSET":13,"SHRINK":16}
FORGING_ORDER = {"NONE":0,"LAST":1,"SECOND_LAST":2,"NOT_THIRD_LAST":3,"THIRD_LAST":4,"NOT_SECOND_LAST":5,"NOT_LAST":6,"ANY":7}
STEP_NAMES = list(FORGING_STEPS.keys())
COLOR_HEX_LIST = ["#228B22","#4682B4","#FF8C00","#800080","#DC143C","#FFD700","#00BFFF","#9ACD32","#FF4500"]
COLOR_RGB_LIST = [(34,139,34),(70,130,180),(255,140,0),(128,0,128),(220,20,60),(255,215,0),(0,191,255),(154,205,50),(255,69,0)]
BATCH_COLORS = ["#d85600","#00822b"]
BATCH_RGBS = array([(216,86,0),(0,130,43)])
BIT_RGB_MAP = {"#d85600":{"first":(127,0,0),"middle":(255,72,0),"last":(0,61,0)},"#00822b":{"first":(0,0,51),"middle":(0,107,0),"last":(0,92,20)}}
COLOR_TO_STEP = {"#228B22":"PUNCH","#4682B4":"BEND","#FF8C00":"UPSET","#800080":"SHRINK","#DC143C":"LIGHT_HIT","#FFD700":"MEDIUM_HIT","#00BFFF":"HARD_HIT","#9ACD32":"DRAW","#FF4500":"HIT"}
STEP_TO_COLOR = {v:k for k,v in COLOR_TO_STEP.items()}
TARGET_RGB, OUTLINE_RGB, START_RGB, END_RGB = (165,42,42), (58,122,254), (30,144,255), (255,218,185)
SCROLL_RGBS = [(139,69,19), (64,224,208)]
VK_Z, VK_X, VK_C, VK_BACKSLASH = 0x5A, 0x58, 0x43, 0xDC
last_steps, last_buttons, running = None, None, True


user32 = WinDLL("user32")
gdi32 = WinDLL("gdi32")
shcore = WinDLL("shcore")

TARGET_MASK_RGBS = array([(137,2,2),(51,115,54)])
DILATION_KERNEL = array([[0,1,0],[1,1,1],[0,1,0]], dtype=uint8)
class BITMAPINFOHEADER(Structure):
    _fields_ = [("biSize",DWORD),("biWidth",LONG),("biHeight",LONG),("biPlanes",WORD),("biBitCount",WORD),("biCompression",DWORD),("biSizeImage",DWORD),("biXPelsPerMeter",LONG),("biYPelsPerMeter",LONG),("biClrUsed",DWORD),("biClrImportant",DWORD)]
def monitor_keyboard():
    global running
    while running:
        if user32.GetAsyncKeyState(VK_Z) & 0x8000: 
            process_forge(True)
            sleep(0.1)
        elif user32.GetAsyncKeyState(VK_X) & 0x8000: 
            execute_saved_steps()
            sleep(0.1)
        elif user32.GetAsyncKeyState(VK_C) & 0x8000: 
            process_forge(False)
            sleep(0.1)
        elif user32.GetAsyncKeyState(VK_BACKSLASH) & 0x8000: 
            running = False
        sleep(0.1)
def fast_click(x, y):
    user32.SetCursorPos(int(x), int(y))
    sleep(CLICK_DELAY)
    user32.mouse_event(2, 0, 0, 0, 0)
    user32.mouse_event(4, 0, 0, 0, 0)
def capture_screen():
    shcore.SetProcessDpiAwareness(2)
    hwnd = user32.FindWindowW(None, WINDOW_TITLE)
    rect = RECT()
    user32.GetWindowRect(hwnd, pointer(rect))
    left, top, width, height = rect.left, rect.top, rect.right-rect.left, rect.bottom-rect.top
    srcdc = user32.GetDC(0)
    memdc = gdi32.CreateCompatibleDC(srcdc)
    bmp = gdi32.CreateCompatibleBitmap(srcdc, width, height)
    gdi32.SelectObject(memdc, bmp)
    gdi32.BitBlt(memdc, 0, 0, width, height, srcdc, left, top, 0x00CC0020|0x40000000)
    bmi = BITMAPINFOHEADER()
    bmi.biSize, bmi.biWidth, bmi.biHeight, bmi.biPlanes, bmi.biBitCount = sizeof(BITMAPINFOHEADER), width, -height, 1, 32
    buffer = create_string_buffer(width*height*4)
    gdi32.GetDIBits(memdc, bmp, 0, height, buffer, byref(bmi), 0)
    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(memdc)
    user32.ReleaseDC(0, srcdc)
    return frombuffer(buffer, dtype=uint8).reshape((height,width,4))[:,:,[2,1,0]], left, top, width, height
def process_image(img):
    ys, xs = where(all(img==TARGET_RGB, axis=-1))
    batch_width, batch_height = max(xs)-min(xs)+1, max(ys)-min(ys)+1
    img = img[::batch_height, ::batch_width]
    ys, xs = where(all(img==OUTLINE_RGB, axis=-1))
    return img[min(ys):max(ys)+1, min(xs):max(xs)+1], min(xs), min(ys), batch_width, batch_height
def find_ui_elements(img, left, top, min_x, min_y, batch_width, batch_height):
    button_locations, click_locations = {}, {}
    rgb_arrays = [array(rgb) for rgb in COLOR_RGB_LIST]
    for _, (hex_code, rgb_array) in enumerate(zip(COLOR_HEX_LIST, rgb_arrays)):
        non_zero = findNonZero(inRange(img, rgb_array, rgb_array))
        if non_zero is not None and len(non_zero) > 0 and (hex_code != "#FF4500" or len(button_locations) < len(COLOR_HEX_LIST) - 1):
            button_locations[hex_code] = non_zero.reshape(-1, 2).tolist()
    target_mask = zeros(img.shape[:2], dtype=uint8)
    for rgb in TARGET_MASK_RGBS:
        target_mask |= all(img == rgb, axis=-1)
    
    neighbors_mask = dilate(target_mask, DILATION_KERNEL) & ~target_mask
    for hex_code, coords in button_locations.items():
        for x, y in coords:
            if 0 <= x < img.shape[1] and 0 <= y < img.shape[0] and neighbors_mask[y, x]:
                click_locations[hex_code] = (left + (x + min_x) * batch_width, top + (y + min_y) * batch_height)
                break
    button_candidates = []
    for idx, (hex_code, rgb_array) in enumerate(zip(COLOR_HEX_LIST, rgb_arrays)):
        mask = all(img == rgb_array, axis=-1).astype(uint8)
        if not any(mask): 
            continue
        _, _, stats, _ = connectedComponentsWithStats(mask, connectivity=4)
        for label in range(1, len(stats)):
            x, y = stats[label, CC_STAT_LEFT], stats[label, CC_STAT_TOP]
            if y > 0 and tuple(img[y-1, x]) == (5, 5, 5):
                button_candidates.append(((left + (x + min_x) * batch_width, top + (y + min_y) * batch_height), hex_code))
    
    return click_locations, [hex_code for _, hex_code in sorted(button_candidates, key=lambda i: i[0][0])]
def find_progress_and_constraints(img, detected_hex_codes):
    start_mask = all(img == START_RGB, axis=-1)
    end_mask = all(img == END_RGB, axis=-1)
    
    if not any(start_mask) or not any(end_mask):
        return None, None, []
    
    _, start_xs = where(start_mask)
    _, end_xs = where(end_mask)
    
    progress_width = min(end_xs) - (max(start_xs) + 1)
    progress_region = img[:, max(start_xs) + 1:min(end_xs)]
    
    red_value = green_value = None
    for idx, color in enumerate(SCROLL_RGBS):
        color_mask = all(progress_region == color, axis=-1)
        if any(color_mask):
            _, color_xs = where(color_mask)
            if len(color_xs) > 0:
                value = ceil((min(color_xs) / progress_width) * 150).astype(int)
                if idx == 0: 
                    red_value = value
                else: 
                    green_value = value
    
    step_groups = {}
    for idx, hex_color in enumerate(BATCH_COLORS):
        color_mask = all(img == BATCH_RGBS[idx], axis=-1).astype(uint8)
        if not any(color_mask): 
            continue
        _, _, stats, _ = connectedComponentsWithStats(color_mask)
        bit_rgbs = BIT_RGB_MAP[hex_color]
        for label in range(1, len(stats)):
            x, y = stats[label, CC_STAT_LEFT], stats[label, CC_STAT_TOP]
            if x not in step_groups: 
                step_groups[x] = [False, False, False]
            if y > 0:
                pix_above = tuple(img[y-1, x])
                if pix_above == bit_rgbs["first"]: 
                    step_groups[x][0] = True
                elif pix_above == bit_rgbs["middle"]: 
                    step_groups[x][1] = True
                elif pix_above == bit_rgbs["last"]: 
                    step_groups[x][2] = True
    
    detected = []
    for i, (_, bits) in enumerate(sorted(step_groups.items())):
        if i >= len(detected_hex_codes): 
            continue
        hex_code = detected_hex_codes[i]
        step_name = COLOR_TO_STEP.get(hex_code, "").upper()
        if not step_name:
            continue
        
        bits_count = bits.count(True)
        if bits_count == 3: 
            detected.append((step_name, 'ANY'))
        elif bits == [True, True, False]: 
            detected.append((step_name, 'NOT_LAST'))
        elif bits[0]: 
            detected.append((step_name, 'THIRD_LAST'))
        elif bits[1]: 
            detected.append((step_name, 'SECOND_LAST'))
        elif bits[2]: 
            detected.append((step_name, 'LAST'))
    
    return red_value, green_value, detected
def calculate_recipe(constraints, target, start_point):
    prob = LpProblem("AnvilRecipeOptimization", LpMinimize)
    low_bounds = {step:sum(1 for s,_ in constraints if s==step and s!="HIT") for step in STEP_NAMES}
    num_hits = sum(1 for s,_ in constraints if s=="HIT")
    step_vars = {step:LpVariable(step,lowBound=low_bounds[step],cat=LpInteger) for step in STEP_NAMES}
    prob += lpSum(FORGING_STEPS[step]*step_vars[step] for step in STEP_NAMES)+start_point==target, "PerfectForging"
    prob += lpSum(step_vars[i] for i in ["LIGHT_HIT","MEDIUM_HIT","HARD_HIT"])>=num_hits, "HitRuleHelper"
    prob += lpSum(step_vars.values()), "Total_Operations"
    prob.solve(PULP_CBC_CMD(msg=False))
    agg_steps = {step:int(step_vars[step].varValue) for step in STEP_NAMES}
    constraints.sort(key=lambda c:sum((FORGING_ORDER[c[1]]>>i)&1 for i in range(3)))
    last_three = [None,None,None]
    def take_step(op):
        if op=="HIT": op=next(h for h in sorted([f"{i}_HIT" for i in ["LIGHT","MEDIUM","HARD"]], key=lambda x:agg_steps[x]) if agg_steps[h])
        agg_steps[op]-=1; return op
    for step,order in constraints:
        spec=sum((FORGING_ORDER[order]>>i)&1 for i in range(3)); placed=False
        if spec==1:
            for i,b in enumerate([1,2,4]):
                if FORGING_ORDER[order]&b: last_three[i]=take_step(step); placed=True; break
        elif spec==2:
            for i,b in enumerate([1,2,4]):
                if FORGING_ORDER[order]&b:
                    for j in range(2,-1,-1):
                        if last_three[j] is None and FORGING_ORDER[order]^(1<<j): last_three[j]=take_step(step); placed=True; break
                    if placed: break
        elif spec==3:
            for j in range(2,-1,-1):
                if last_three[j] is None: last_three[j]=take_step(step); placed=True; break
    remaining = []
    for step in sorted(agg_steps.keys(),reverse=True,key=lambda x:agg_steps[x]+1000*(FORGING_STEPS[x]>0)):
        remaining.extend([step]*agg_steps[step])
    result = []
    if remaining:
        cur,cnt = remaining[0],1
        for step in remaining[1:]:
            if step!=cur: result.extend([cur]*cnt); cur,cnt = step,1
            else: cnt+=1
        result.extend([cur]*cnt)
    return result+[s for s in reversed(last_three) if s is not None]
def execute_steps(steps, buttons):
    step_to_color = STEP_TO_COLOR.get
    for step in steps:
        color = step_to_color(step)
        if color and color in buttons:
            button_pos = buttons[color]
            fast_click(int(button_pos[0]), int(button_pos[1]))
def execute_saved_steps():
    if last_steps and last_buttons: execute_steps(last_steps,last_buttons)
def process_forge(should_execute=True):
    global last_steps, last_buttons
    img, left, top, _, _ = capture_screen()
    processed_img, min_x, min_y, batch_width, batch_height = process_image(img)
    click_locations, detected_steps = find_ui_elements(processed_img, left, top, min_x, min_y, batch_width, batch_height)
    red_value, green_value, constraints = find_progress_and_constraints(processed_img, detected_steps)
    
    if red_value is None or green_value is None:
        return
        
    next_steps = calculate_recipe(constraints, red_value, green_value)
    step_buttons = {}
    step_to_color = STEP_TO_COLOR.get
    
    for s in set(next_steps):
        color = step_to_color(s)
        if color and color in click_locations:
            step_buttons[color] = click_locations[color]
    
    if should_execute: 
        execute_steps(next_steps, step_buttons)
    else: 
        print("\nCalculated steps:", next_steps)
    
    last_steps, last_buttons = next_steps, step_buttons
if __name__ == "__main__":
    print("Press Z to calculate and execute\nPress X to execute the last operation (without recomputing)\nPress C to calculate only (no execution)\nPress \\ to exit")
    monitor_keyboard()