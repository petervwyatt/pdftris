PDF_FILE_TEMPLATE = """%PDF-1.6
%öäüß

% Root = Document catalog
1 0 obj
<<
	/Type /Catalog
	/AcroForm << 
		/Fields [ ###FIELDS_LIST### ] 
		/DA (/HeBo 0 Tf 0 g 0 G)
	>>
	/Pages 2 0 R
	/OpenAction 6 0 R
	/Names << 
		/JavaScript << 
			/Names [ (DocJS) 6 0 R ] 
		>>
	>>
	/PageLayout /SinglePage
	/PageMode /UseNone
	/ViewerPreferences << /FitWindow true >>
>>
endobj

2 0 obj
<<
	/Type /Pages
	/Count 1
	/Kids [ 3 0 R ]
>>
endobj

% Page 1
3 0 obj
<<
	/Type /Page
	/Annots [ ###ANNOTS_LIST### ]
	/Parent 2 0 R
	/Contents 4 0 R
	/MediaBox [ 0 0 612 792 ]
	/Resources << >>
>>
endobj

% Page content stream - empty
4 0 obj
<< /Length 3 >>
stream
q Q
endstream
endobj

% Font resource 
5 0 obj
<<
	/Type /Font
	/Subtype /Type1
	/BaseFont /Helvetica-Bold
	/Encoding /WinAnsiEncoding
>>
endobj

% JavaScript Action
6 0 obj
<<
	/Type /Action
	/S /JavaScript
	/JS 7 0 R
>>
endobj

 % Document OpenAction JavaScript
7 0 obj
<< /Length 6976 >>
stream
// Hacky wrapper to work with a callback instead of a string 
function setInterval(cb, ms) {
	var evalStr = "(" + cb.toString() + ")();";
	return app.setInterval(evalStr, ms);
}

// https://gist.github.com/blixt/f17b47c62508be59987b
var rand_seed = Date.now() % 2147483647;
function rand() {
	return rand_seed = rand_seed * 16807 % 2147483647;
}

// nr of unique rotations per piece
var piece_rotations = [1, 2, 2, 2, 4, 4, 4];

// Piece data: [piece_nr * 32 + rot_nr * 8 + brick_nr * 2 + j]
// with rot_nr between 0 and 4
// with the brick number between 0 and 4
// and j == 0 for X coord, j == 1 for Y coord
var piece_data = [
	// square block
	0, 0, -1, 0, -1, -1, 0, -1, 
	0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0,

	// line block
	0, 0, -2, 0, -1, 0, 1, 0,
	0, 0, 0, 1, 0, -1, 0, -2,
	0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0,

	// S-block
	0, 0, -1, -1, 0, -1, 1, 0, 
	0, 0, 0, 1, 1, 0, 1, -1, 
	0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0,

	// Z-block
	0, 0, -1, 0, 0, -1, 1, -1, 
	0, 0, 1, 1, 1, 0, 0, -1, 
	0, 0, 0, 0, 0, 0, 0, 0,
	0, 0, 0, 0, 0, 0, 0, 0,

	// L-block
	0, 0, -1, 0, -1, -1, 1, 0, 
	0, 0, 0, 1, 0, -1, 1, -1, 
	0, 0, -1, 0, 1, 0, 1, 1, 
	0, 0, -1, 1, 0, 1, 0, -1, 

	// J-block
	0, 0, -1, 0, 1, 0, 1, -1, 
	0, 0, 0, 1, 0, -1, 1, 1, 
	0, 0, -1, 1, -1, 0, 1, 0, 
	0, 0, 0, 1, 0, -1, -1, -1, 

	// T-block
	0, 0, -1, 0, 0, -1, 1, 0,	
	0, 0, 0, 1, 0, -1, 1, 0, 
	0, 0, -1, 0, 0, 1, 1, 0, 
	0, 0, -1, 0, 0, 1, 0, -1
]

var TICK_INTERVAL = 50;
var GAME_STEP_TIME = 400;

// Globals
var pixel_fields = [];
var field = [];
var score = 0;
var time_ms = 0;
var last_update = 0;
var interval = 0;

// Current piece
var piece_type = rand() % 7;
var piece_x = 0;
var piece_y = 0;
var piece_rot = 0;

function spawn_new_piece() {
	piece_type = rand() % 7;
	piece_x = 4;
	piece_y = 0;
	piece_rot = 0;
}

function set_controls_visibility(state) {
	this.getField("T_input").hidden = !state;
	this.getField("B_left").hidden = !state;
	this.getField("B_right").hidden = !state;
	this.getField("B_down").hidden = !state;
	this.getField("B_rotate").hidden = !state;
}

function game_init() {
	spawn_new_piece();

	// Gather references to pixel field objects
	// and initialize game state
	for (var x = 0; x < ###GRID_WIDTH###; ++x) {
		pixel_fields[x] = [];
		field[x] = [];
		for (var y = 0; y < ###GRID_HEIGHT###; ++y) {
			var f = "P_" + x + "_" + y;
			pixel_fields[x][y] = this.getField(f);
			field[x][y] = 0;
		}
	}

	last_update = time_ms;
	score = 0;

	// Start timer
	interval = setInterval(game_tick, TICK_INTERVAL);

	// Hide start button
	this.getField("B_start").hidden = true;

	// Show input box and controls
	set_controls_visibility(true);
}

function game_update() {
	if (time_ms - last_update >= GAME_STEP_TIME) {
		lower_piece();
		last_update = time_ms;
	}
}

function game_over() {
	app.clearInterval(interval);
	app.alert("Game over! Score: " + score + " - refresh to restart.");
}

function rotate_piece() {
	piece_rot++;
	if (piece_rot >= piece_rotations[piece_type]) {
		piece_rot = 0;
	}

	// If we're now out of bounds, undo the rotation
	var illegal = false;
	for (var square = 0; square < 4; ++square) {
		var x_off = piece_data[piece_type * 32 + piece_rot * 8 + square * 2 + 0];
		var y_off = piece_data[piece_type * 32 + piece_rot * 8 + square * 2 + 1];

		var abs_x = piece_x + x_off;
		var abs_y = piece_y + y_off;

		if (abs_x < 0 || abs_y < 0 || abs_x >= ###GRID_WIDTH### || abs_y >= ###GRID_HEIGHT###) {
			illegal = true;
			break;	
		}
	}
	if (illegal) {
		piece_rot--;
		if (piece_rot < 0) {
			piece_rot = piece_rotations[piece_type] - 1;
		}
	}
}

function is_side_collision() {
	for (var square = 0; square < 4; ++square) {
		var x_off = piece_data[piece_type * 32 + piece_rot * 8 + square * 2 + 0];
		var y_off = piece_data[piece_type * 32 + piece_rot * 8 + square * 2 + 1];

		var abs_x = piece_x + x_off;
		var abs_y = piece_y + y_off;

		// collision with walls
		if (abs_x < 0 || abs_x >= ###GRID_WIDTH###) {
			return true;
		}

		// collision with field blocks
		if (field[abs_x][abs_y]) {
			return true;
		}
	}
	return false;
}

function handle_input(event) {
	switch (event.change) {
		case 'w': rotate_piece(); break;
		case 'a': move_left(); break;
		case 'd': move_right(); break;
		case 's': lower_piece(); break;
	}
}

function move_left() {
	piece_x--;
	if (is_side_collision()) {
		piece_x++;
	}
}

function move_right() {
	piece_x++;
	if (is_side_collision()) {
		piece_x--;
	}
}

function check_for_filled_lines() {
	for (var row = 0; row < ###GRID_HEIGHT###; ++row) {
		var fill_count = 0;
		for (var column = 0; column < ###GRID_WIDTH###; ++column) {
			fill_count += field[column][row];
		}
		if (fill_count == ###GRID_WIDTH###) {
			// increase score
			score++;
			draw_updated_score();

			// remove line (shift down)
			for (var row2 = row; row2 > 0; row2--) {
				for (var column2 = 0; column2 < ###GRID_WIDTH###; ++column2) {
					field[column2][row2] = field[column2][row2-1];
				}
			}

		}
	}
}

function lower_piece() {
	piece_y++;

	var collision = false;
	for (var square = 0; square < 4; ++square) {
		var x_off = piece_data[piece_type * 32 + piece_rot * 8 + square * 2 + 0];
		var y_off = piece_data[piece_type * 32 + piece_rot * 8 + square * 2 + 1];

		var abs_x = piece_x + x_off;
		var abs_y = piece_y + y_off;

		if (abs_x < 0 || abs_y < 0 || abs_x >= ###GRID_WIDTH### || abs_y >= ###GRID_HEIGHT###) {
			collision = true;
			break;	
		}

		if (abs_y >= ###GRID_HEIGHT### || field[abs_x][abs_y]) {
			collision = true;
			break;
		}
	}

	if (collision) {
		// if at the top, game over
		if (piece_y == 1) {
			game_over();
			return;
		}

		// add to field
		piece_y--;
		for (var square = 0; square < 4; ++square) {
			var x_off = piece_data[piece_type * 32 + piece_rot * 8 + square * 2 + 0];
			var y_off = piece_data[piece_type * 32 + piece_rot * 8 + square * 2 + 1];

			var abs_x = piece_x + x_off;
			var abs_y = piece_y + y_off;

			if (abs_x < 0 || abs_y < 0 || abs_x >= ###GRID_WIDTH### || abs_y >= ###GRID_HEIGHT###) {
				// TODO: it is out of bounds, we should nudge it inwards?
				continue;
			}

			field[abs_x][abs_y] = true;
		}

		check_for_filled_lines();
		spawn_new_piece();
	}
}

function draw_updated_score() {
	this.getField("T_score").value = "Score: " + score
}

function set_pixel(x, y, state) {
	if (x < 0 || y < 0 || x >= ###GRID_WIDTH### || y >= ###GRID_HEIGHT###) {
		return;
	}
	pixel_fields[x][###GRID_HEIGHT### - 1 - y].hidden = !state;
}

function draw_field() {
	for (var x = 0; x < ###GRID_WIDTH###; ++x) {
		for (var y = 0; y < ###GRID_HEIGHT###; ++y) {
			set_pixel(x, y, field[x][y]);
		}
	}
}

function draw_current_piece() {
	for (var square = 0; square < 4; ++square) {
		var x_off = piece_data[piece_type * 32 + piece_rot * 8 + square * 2 + 0];
		var y_off = piece_data[piece_type * 32 + piece_rot * 8 + square * 2 + 1];

		var abs_x = piece_x + x_off;
		var abs_y = piece_y + y_off;

		set_pixel(abs_x, abs_y, 1);
	}
}

function draw() {
	draw_field();
	draw_current_piece();
}

function game_tick() {
	time_ms += TICK_INTERVAL;
	game_update();
	draw();
}

// Hide controls to start with
set_controls_visibility(false);

// Zoom to fit (on FF)
app.execMenuItem("FitPage");

endstream
endobj

###PDF_OBJECTS###
"""

PDF_FILE_TRAILER = """###XREF_ENTRIES###
trailer
<<
	/Root 1 0 R
	/Size ###OBJ_COUNT###
>>
startxref
###START_XREF###
%%EOF
"""

PLAYING_FIELD_OBJ = """
###IDX### obj
<<
	/Type /Annot
	/Subtype /Widget
	/FT /Btn
	/F 6 % Bit 2 = hidden, Bit 3 = print
	/Ff 65538 % Bit 2 = hidden, Bit 17 = pushbutton
	/MK <<
		/BG [ 0.8 ]
		/BC [ 0 0 0 ]
	>>
	/Border [ 0 0 1 ]
	/P 3 0 R
	/Rect [ ###RECT### ]
	/T (playing_field)
>>
endobj
"""

PIXEL_WIDGET_OBJ = """
###IDX### obj
<<
	/Type /Annot
	/Subtype /Widget
	/FT /Btn
	/F 6 % Bit 2 = hidden, Bit 3 = print
	/Ff 65538 % Bit 2 = hidden, Bit 17 = pushbutton
	/MK <<
		/BG [ ###COLOR### ]
		/BC [ 0.5 0.5 0.5 ]
	>>
	/Border [ 0 0 1 ]
	/P 3 0 R
	/Rect [ ###RECT### ]
	/T (P_###X###_###Y###)
>>
endobj
"""

BUTTON_AP_STREAM = """
###IDX### obj
<<
	/Type /XObject
	/Subtype /Form
	/BBox [ 0 0 ###WIDTH### ###HEIGHT### ]
	/FormType 1
	/Matrix [ 1 0 0 1 0 0 ]
	/Resources << /Font << /HeBo 5 0 R >> >>
	/Length ###LENGTH###
>>
stream
q
	0.75 g
	0 0 ###WIDTH### ###HEIGHT### re
	f
Q
q
	1 1 ###WIDTH### ###HEIGHT### re
	W
	n
	BT
		/HeBo 12 Tf
		0 g
		10 8 Td
		(###TEXT###) Tj
	ET
Q
endstream
endobj
"""

BUTTON_WIDGET_OBJ = """
###IDX### obj
<<
	/Type /Annot
	/Subtype /Widget
	/FT /Btn
	/A <<
		/Type /Action
		/JS (###SCRIPT###)
		/S /JavaScript
	>>
	/AP << /N ###AP_IDX### R >>
	/F 3
	/Ff 65536 % Bit 17 = pushbutton
	/MK <<
		/BG [ 0.75 ]
		/CA (###LABEL###)
	>>
	/P 3 0 R
	/Rect [ ###RECT### ]
	/T (###NAME###)
>>
endobj
"""

TEXT_WIDGET_OBJ = """
###IDX### obj
<<
	/Type /Annot
	/Subtype /Widget
	/FT /Tx
	/AA <<
		/K <<
			/Type /Action
			/JS (###SCRIPT###)
			/S /JavaScript
		>>
	>>
	/MK << >>
	/F 3
	/Ff 0
	/MaxLen 0
	/P 3 0 R
	/Rect [ ###RECT### ]
	/T (###NAME###)
	/V (###LABEL###)
>>
endobj
"""

PX_SIZE = 20
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_OFF_X = 200
GRID_OFF_Y = 350

pdf_objects = ""
annots_list = []
field_list = []
obj_idx_ctr = 8
first_obj_idx = obj_idx_ctr

def add_field(field):
	global pdf_objects, field_list, annots_list, obj_idx_ctr
	pdf_objects += field
	field_list.append(obj_idx_ctr)
	annots_list.append(obj_idx_ctr)
	obj_idx_ctr += 1

def add_annot(annot):
	global pdf_objects, annots_list, obj_idx_ctr
	pdf_objects += annot
	annots_list.append(obj_idx_ctr)
	obj_idx_ctr += 1

def add_stream(stm):
	global pdf_objects, obj_idx_ctr
	pdf_objects += stm
	obj_idx_ctr += 1


# Playing field outline
playing_field = PLAYING_FIELD_OBJ
playing_field = playing_field.replace("###IDX###", f"{obj_idx_ctr} 0")
playing_field = playing_field.replace("###RECT###", f"{GRID_OFF_X} {GRID_OFF_Y} {GRID_OFF_X+GRID_WIDTH*PX_SIZE} {GRID_OFF_Y+GRID_HEIGHT*PX_SIZE}")
add_field(playing_field)

for x in range(GRID_WIDTH):
	for y in range(GRID_HEIGHT):
		# Build object
		pixel = PIXEL_WIDGET_OBJ
		pixel = pixel.replace("###IDX###", f"{obj_idx_ctr} 0")
		c = [0, 0, 0]
		pixel = pixel.replace("###COLOR###", f"{c[0]} {c[1]} {c[2]}")
		pixel = pixel.replace("###RECT###", f"{GRID_OFF_X+x*PX_SIZE} {GRID_OFF_Y+y*PX_SIZE} {GRID_OFF_X+x*PX_SIZE+PX_SIZE} {GRID_OFF_Y+y*PX_SIZE+PX_SIZE}")
		pixel = pixel.replace("###X###", f"{x}")
		pixel = pixel.replace("###Y###", f"{y}")
		add_field(pixel)

def add_button(label, name, x, y, width, height, js):
	ap_stream = BUTTON_AP_STREAM
	ap_stream = ap_stream.replace("###IDX###", f"{obj_idx_ctr} 0")
	ap_stream = ap_stream.replace("###TEXT###", label)
	ap_stream = ap_stream.replace("###WIDTH###", f"{width}")
	ap_stream = ap_stream.replace("###HEIGHT###", f"{height}")
	stm = (ap_stream.encode().find(b"stream") + len("stream"))
	endstm = ap_stream.encode().find(b"endstream\n")
	stm_length = endstm	- stm - 1
	ap_stream = ap_stream.replace("###LENGTH###", f"{stm_length}")
	add_stream(ap_stream)

	button = BUTTON_WIDGET_OBJ
	button = button.replace("###IDX###", f"{obj_idx_ctr} 0")
	button = button.replace("###SCRIPT###", js)
	button = button.replace("###AP_IDX###", f"{obj_idx_ctr-1} 0")
	button = button.replace("###LABEL###", label)
	button = button.replace("###NAME###", name if name else f"B_{obj_idx_ctr}")
	button = button.replace("###RECT###", f"{x} {y} {x + width} {y + height}")
	add_field(button)

def add_text(label, name, x, y, width, height, js):
	text = TEXT_WIDGET_OBJ
	text = text.replace("###IDX###", f"{obj_idx_ctr} 0")
	text = text.replace("###SCRIPT###", js)
	text = text.replace("###LABEL###", label)
	text = text.replace("###NAME###", name)
	text = text.replace("###RECT###", f"{x} {y} {x + width} {y + height}")
	add_field(text)


add_button("<", "B_left", GRID_OFF_X + 0, GRID_OFF_Y - 70, 50, 50, "move_left();")
add_button(">", "B_right", GRID_OFF_X + 60, GRID_OFF_Y - 70, 50, 50, "move_right();")
add_button("\\\\/", "B_down", GRID_OFF_X + 30, GRID_OFF_Y - 130, 50, 50, "lower_piece();")
add_button("SPIN", "B_rotate", GRID_OFF_X + 140, GRID_OFF_Y - 70, 50, 50, "rotate_piece();")
add_button("Start game", "B_start", GRID_OFF_X + (GRID_WIDTH*PX_SIZE)/2-50, GRID_OFF_Y + (GRID_HEIGHT*PX_SIZE)/2-50, 100, 100, "game_init();")

add_text("Type here for keyboard controls (WASD)", "T_input", GRID_OFF_X + 0, GRID_OFF_Y - 200, GRID_WIDTH*PX_SIZE, 50, "handle_input(event);")
add_text("Score: 0", "T_score", GRID_OFF_X + GRID_WIDTH*PX_SIZE+10, GRID_OFF_Y + GRID_HEIGHT*PX_SIZE-50, 100, 50, "")

filled_pdf = PDF_FILE_TEMPLATE.replace("###PDF_OBJECTS###", pdf_objects)
filled_pdf = filled_pdf.replace("###FIELDS_LIST###", " ".join([f"{i} 0 R" for i in field_list]))
filled_pdf = filled_pdf.replace("###ANNOTS_LIST###", " ".join([f"{i} 0 R" for i in annots_list]))
filled_pdf = filled_pdf.replace("###GRID_WIDTH###",	f"{GRID_WIDTH}")
filled_pdf = filled_pdf.replace("###GRID_HEIGHT###", f"{GRID_HEIGHT}")

# Build footer of PDF (cross-reference table, trailer, startxref) and append.
# Note: obj_idx_ctr is already incremented to 1 plus the last object number
pdf_as_bytes = filled_pdf.encode()
footer = PDF_FILE_TRAILER.replace("###OBJ_COUNT###", f"{obj_idx_ctr}")
footer = footer.replace("###START_XREF###", f"{len(pdf_as_bytes)}")
xref = f"xref\n0 {obj_idx_ctr}\n0000000000 65535 f \n"
for x in range(1, obj_idx_ctr):
	offset = pdf_as_bytes.find(f"{x} 0 obj".encode())
	xref += f"{offset:010} 00000 n \n"
footer = footer.replace("###XREF_ENTRIES###", xref)
filled_pdf += footer

# PDFs are binary! In order to be portable across platform, write as a BINARY file
# Avoids \n differences (1 or 2 byes) and thus incorrect byte offsets and stream lengths.
pdffile = open("tris.pdf", "wb")
pdffile.write(filled_pdf.encode())
pdffile.close()
